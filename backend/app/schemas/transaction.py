from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import date, datetime


# =========================
# CREDIT TRANSACTION SCHEMAS
# =========================

class TransactionCreate(BaseModel):
    customer_id: int
    amount: float
    type: str                                # 'debit' (purchase) or 'credit' (payment)
    sale_id: Optional[int] = None
    note: Optional[str] = None
    due_date: Optional[date] = None

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v

    @field_validator("type")
    @classmethod
    def valid_type(cls, v):
        if v not in ("debit", "credit"):
            raise ValueError("Type must be 'debit' (purchase) or 'credit' (payment)")
        return v


class TransactionResponse(BaseModel):
    transaction_id: int
    customer_id: int
    sale_id: Optional[int] = None
    amount: float
    type: str
    status: str
    note: Optional[str] = None
    due_date: Optional[date] = None
    transaction_date: datetime

    class Config:
        from_attributes = True


# =========================
# CREDIT AGING REPORT
# =========================

class CreditReportItem(BaseModel):
    customer_id: int
    name: str
    phone: str
    current: float           # not yet overdue
    overdue_30: float        # 1–30 days overdue
    overdue_60: float        # 31–60 days overdue
    overdue_90: float        # 60+ days overdue
    total_outstanding: float