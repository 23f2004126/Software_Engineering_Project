from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from pydantic import BaseModel, field_validator, Field
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

from app.database import get_db
from app.models.user import Expense, User
from app.models.sale import Sale
from app.routes.deps import get_current_user

router = APIRouter(prefix="/api/expenses", tags=["Expenses"])

VALID_CATEGORIES = ("rent", "salary", "utilities", "maintenance", "supplies", "other")


# =========================
# SCHEMAS
# =========================

class ExpenseCreate(BaseModel):
    title: str
    amount: Decimal = Field(..., gt=0)
    category: str
    note: Optional[str] = None
    expense_date: Optional[date] = None
    recurring: bool = False

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("Expense amount must be greater than 0")
        return v

    @field_validator("category")
    @classmethod
    def valid_category(cls, v):
        if v not in VALID_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(VALID_CATEGORIES)}")
        return v

    @field_validator("expense_date")
    @classmethod
    def date_not_future(cls, v):
        if v and v > date.today():
            raise ValueError("Expense date cannot be in the future")
        return v


class ExpenseResponse(BaseModel):
    expense_id: int
    title: str
    amount: Decimal
    category: str
    note: Optional[str] = None
    expense_date: date
    recurring: bool
    created_by: Optional[int] = None

    class Config:
        from_attributes = True


class CategorySummary(BaseModel):
    category: str
    total: Decimal
    count: int
    percentage: float


class ExpenseSummaryResponse(BaseModel):
    month: int
    year: int
    total_expenses: Decimal
    by_category: List[CategorySummary]
    previous_month_total: Decimal
    change_percentage: float


class FinancialReportResponse(BaseModel):
    from_date: date
    to_date: date
    total_revenue: Decimal
    total_expenses: Decimal
    net_profit: Decimal
    profit_margin_pct: float
    expense_breakdown: List[CategorySummary]


# =========================
# POST /api/expenses/
# =========================

@router.post("/", response_model=ExpenseResponse)
def add_expense(
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = Expense(
        title=data.title,
        amount=data.amount,
        category=data.category,
        note=data.note,
        expense_date=data.expense_date or date.today(),
        recurring=data.recurring,
        created_by=current_user.user_id
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense


# =========================
# GET /api/expenses/
# =========================

@router.get("/", response_model=List[ExpenseResponse])
def get_expenses(
    category: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Expense)

    if category:
        if category not in VALID_CATEGORIES:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        query = query.filter(Expense.category == category)

    if start_date:
        try:
            query = query.filter(Expense.expense_date >= date.fromisoformat(start_date))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format (use YYYY-MM-DD)")

    if end_date:
        try:
            query = query.filter(Expense.expense_date <= date.fromisoformat(end_date))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format (use YYYY-MM-DD)")

    return query.order_by(Expense.expense_date.desc()).offset(skip).limit(limit).all()


# =========================
# GET /api/expenses/summary
# =========================

@router.get("/summary", response_model=ExpenseSummaryResponse)
def get_expense_summary(
    month: int = Query(None, ge=1, le=12),
    year: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()
    target_month = month or today.month
    target_year = year or today.year

    current = db.query(Expense).filter(
        extract("month", Expense.expense_date) == target_month,
        extract("year", Expense.expense_date) == target_year
    ).all()

    total = sum(e.amount for e in current)

    category_map = {}
    for e in current:
        category_map.setdefault(e.category, {"total": 0.0, "count": 0})
        category_map[e.category]["total"] += e.amount
        category_map[e.category]["count"] += 1

    by_category = [
        CategorySummary(
            category=cat,
            total=round(vals["total"], 2),
            count=vals["count"],
            percentage=round((vals["total"] / total * 100) if total > 0 else 0, 2)
        )
        for cat, vals in category_map.items()
    ]

    if target_month == 1:
        prev_month, prev_year = 12, target_year - 1
    else:
        prev_month, prev_year = target_month - 1, target_year

    prev_total = db.query(func.sum(Expense.amount)).filter(
        extract("month", Expense.expense_date) == prev_month,
        extract("year", Expense.expense_date) == prev_year
    ).scalar() or 0.0

    change_pct = (
        ((total - prev_total) / prev_total * 100) if prev_total > 0 else 0.0
    )

    return ExpenseSummaryResponse(
        month=target_month,
        year=target_year,
        total_expenses=round(total, 2),
        by_category=by_category,
        previous_month_total=round(float(prev_total), 2),
        change_percentage=round(change_pct, 2)
    )


# =========================
# GET /api/expenses/financial-report  (P&L)
# =========================

@router.get("/financial-report", response_model=FinancialReportResponse)
def get_financial_report(
    from_date: str = Query(..., description="YYYY-MM-DD"),
    to_date: str = Query(..., description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        start = date.fromisoformat(from_date)
        end = date.fromisoformat(to_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    if start > end:
        raise HTTPException(status_code=400, detail="from_date must be before to_date")

    total_revenue = db.query(func.sum(Sale.total_amount)).filter(
        func.date(Sale.bill_date) >= start,
        func.date(Sale.bill_date) <= end,
        Sale.status == "completed"
    ).scalar() or 0.0

    expenses_in_range = db.query(Expense).filter(
        Expense.expense_date >= start,
        Expense.expense_date <= end
    ).all()

    total_expenses = sum(e.amount for e in expenses_in_range)
    net_profit = total_revenue - total_expenses
    profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0.0

    category_map = {}
    for e in expenses_in_range:
        category_map.setdefault(e.category, {"total": 0.0, "count": 0})
        category_map[e.category]["total"] += e.amount
        category_map[e.category]["count"] += 1

    breakdown = [
        CategorySummary(
            category=cat,
            total=round(vals["total"], 2),
            count=vals["count"],
            percentage=round((vals["total"] / total_expenses * 100) if total_expenses > 0 else 0, 2)
        )
        for cat, vals in category_map.items()
    ]

    return FinancialReportResponse(
        from_date=start,
        to_date=end,
        total_revenue=round(float(total_revenue), 2),
        total_expenses=round(total_expenses, 2),
        net_profit=round(net_profit, 2),
        profit_margin_pct=round(profit_margin, 2),
        expense_breakdown=breakdown
    )


# =========================
# DELETE /api/expenses/:expense_id
# =========================

@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = db.query(Expense).filter(Expense.expense_id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    db.commit()

    return {"message": "Expense deleted successfully"}