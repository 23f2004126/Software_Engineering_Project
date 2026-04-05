from pydantic import BaseModel, field_validator
from typing import Optional, List
from decimal import Decimal
from datetime import date

VALID_CATEGORIES = ("rent", "salary", "utilities", "maintenance", "supplies", "other")


# =========================
# EXPENSE SCHEMAS
# =========================

class ExpenseCreate(BaseModel):
    title: str
    amount: float
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
    amount: float
    category: str
    note: Optional[str] = None
    expense_date: date
    recurring: bool
    created_by: Optional[int] = None

    class Config:
        from_attributes = True


# =========================
# SUMMARY SCHEMAS
# =========================

class CategorySummary(BaseModel):
    category: str
    total: float
    count: int
    percentage: float


class ExpenseSummaryResponse(BaseModel):
    month: int
    year: int
    total_expenses: float
    by_category: List[CategorySummary]
    previous_month_total: float
    change_percentage: float


# =========================
# FINANCIAL REPORT (P&L)
# =========================

class FinancialReportResponse(BaseModel):
    from_date: date
    to_date: date
    total_revenue: float
    total_expenses: float
    net_profit: float
    profit_margin_pct: float
    expense_breakdown: List[CategorySummary]