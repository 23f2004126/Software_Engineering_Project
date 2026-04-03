"""
Service layer for expenses.py routes.
Handles expense CRUD, monthly summaries, and P&L financial reports.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Optional, Tuple, List
from datetime import date

from app.models.user import Expense
from app.models.sale import Sale


VALID_CATEGORIES = ("rent", "salary", "utilities", "maintenance", "supplies", "other")


# =========================
# EXPENSE CRUD
# =========================

def get_expense_by_id(db: Session, expense_id: int) -> Optional[Expense]:
    return db.query(Expense).filter(Expense.expense_id == expense_id).first()


def get_expenses(
    db: Session,
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 50
) -> Tuple[List[Expense], Optional[str]]:
    """
    Return filtered, paginated expenses.
    Returns (expenses, None) on success, ([], error_message) on invalid input.
    """
    if category and category not in VALID_CATEGORIES:
        return [], f"Invalid category: {category}"

    query = db.query(Expense)

    if category:
        query = query.filter(Expense.category == category)
    if start_date:
        query = query.filter(Expense.expense_date >= start_date)
    if end_date:
        query = query.filter(Expense.expense_date <= end_date)

    return query.order_by(Expense.expense_date.desc()).offset(skip).limit(limit).all(), None


def create_expense(
    db: Session,
    title: str,
    amount: float,
    category: str,
    note: Optional[str],
    expense_date: Optional[date],
    recurring: bool,
    created_by: int
) -> Expense:
    expense = Expense(
        title=title,
        amount=amount,
        category=category,
        note=note,
        expense_date=expense_date or date.today(),
        recurring=recurring,
        created_by=created_by,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, expense_id: int) -> Tuple[bool, Optional[str]]:
    expense = get_expense_by_id(db, expense_id)
    if not expense:
        return False, "Expense not found"

    db.delete(expense)
    db.commit()
    return True, None


# =========================
# MONTHLY SUMMARY
# =========================

def get_expense_summary(db: Session, month: int, year: int) -> dict:
    """
    Return total expenses for the given month/year, broken down by category,
    plus previous-month total and change percentage.
    """
    current = db.query(Expense).filter(
        extract("month", Expense.expense_date) == month,
        extract("year", Expense.expense_date) == year,
    ).all()

    total = sum(e.amount for e in current)

    category_map: dict = {}
    for e in current:
        category_map.setdefault(e.category, {"total": 0.0, "count": 0})
        category_map[e.category]["total"] += e.amount
        category_map[e.category]["count"] += 1

    by_category = [
        {
            "category": cat,
            "total": round(vals["total"], 2),
            "count": vals["count"],
            "percentage": round((vals["total"] / total * 100) if total > 0 else 0, 2),
        }
        for cat, vals in category_map.items()
    ]

    prev_month = 12 if month == 1 else month - 1
    prev_year = year - 1 if month == 1 else year

    prev_total = db.query(func.sum(Expense.amount)).filter(
        extract("month", Expense.expense_date) == prev_month,
        extract("year", Expense.expense_date) == prev_year,
    ).scalar() or 0.0

    change_pct = (
        ((total - float(prev_total)) / float(prev_total) * 100) if prev_total > 0 else 0.0
    )

    return {
        "month": month,
        "year": year,
        "total_expenses": round(total, 2),
        "by_category": by_category,
        "previous_month_total": round(float(prev_total), 2),
        "change_percentage": round(change_pct, 2),
    }


# =========================
# FINANCIAL REPORT (P&L)
# =========================

def get_financial_report(
    db: Session,
    start: date,
    end: date
) -> dict:
    """
    Profit & Loss report for a date range.
    Revenue from completed sales minus all expenses in the same period.
    """
    total_revenue = db.query(func.sum(Sale.total_amount)).filter(
        func.date(Sale.bill_date) >= start,
        func.date(Sale.bill_date) <= end,
        Sale.status == "completed",
    ).scalar() or 0.0

    expenses_in_range = db.query(Expense).filter(
        Expense.expense_date >= start,
        Expense.expense_date <= end,
    ).all()

    total_expenses = sum(e.amount for e in expenses_in_range)
    net_profit = float(total_revenue) - total_expenses
    profit_margin = (net_profit / float(total_revenue) * 100) if total_revenue > 0 else 0.0

    category_map: dict = {}
    for e in expenses_in_range:
        category_map.setdefault(e.category, {"total": 0.0, "count": 0})
        category_map[e.category]["total"] += e.amount
        category_map[e.category]["count"] += 1

    breakdown = [
        {
            "category": cat,
            "total": round(vals["total"], 2),
            "count": vals["count"],
            "percentage": round(
                (vals["total"] / total_expenses * 100) if total_expenses > 0 else 0, 2
            ),
        }
        for cat, vals in category_map.items()
    ]

    return {
        "from_date": start,
        "to_date": end,
        "total_revenue": round(float(total_revenue), 2),
        "total_expenses": round(total_expenses, 2),
        "net_profit": round(net_profit, 2),
        "profit_margin_pct": round(profit_margin, 2),
        "expense_breakdown": breakdown,
    }