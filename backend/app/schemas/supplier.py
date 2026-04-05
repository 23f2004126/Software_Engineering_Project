from pydantic import BaseModel, field_validator
from typing import Optional, List
from decimal import Decimal
from datetime import date, datetime


# =========================
# SUPPLIER SCHEMAS
# =========================

class SupplierCreate(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    rating: float = 0.0
    payment_terms: int = 30
    status: str = "active"

    @field_validator("rating")
    @classmethod
    def valid_rating(cls, v):
        if not (0 <= v <= 5):
            raise ValueError("Rating must be between 0 and 5")
        return v

    @field_validator("status")
    @classmethod
    def valid_status(cls, v):
        if v not in ("active", "inactive"):
            raise ValueError("Status must be 'active' or 'inactive'")
        return v


class SupplierResponse(BaseModel):
    supplier_id: int
    name: str
    contact_person: Optional[str] = None
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    rating: float
    payment_terms: int
    status: str
    pending_amount: Optional[float] = None   # computed in GET /{supplier_id}

    class Config:
        from_attributes = True


# =========================
# SUPPLIER PAYMENT SCHEMAS
# =========================

class SupplierPaymentCreate(BaseModel):
    amount: float
    mode: str                                # cash / cheque / transfer / upi
    po_id: Optional[int] = None
    cheque_no: Optional[str] = None
    note: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("Payment amount must be greater than 0")
        return v

    @field_validator("mode")
    @classmethod
    def valid_mode(cls, v):
        if v not in ("cash", "cheque", "transfer", "upi"):
            raise ValueError("Mode must be cash, cheque, transfer, or upi")
        return v


class SupplierPaymentResponse(BaseModel):
    payment_id: int
    supplier_id: int
    amount: float
    mode: str
    po_id: Optional[int] = None
    cheque_no: Optional[str] = None
    status: str
    due_date: Optional[date] = None
    paid_date: Optional[date] = None
    note: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True