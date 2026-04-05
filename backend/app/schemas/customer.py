from pydantic import BaseModel, field_validator
from typing import Optional, List
from decimal import Decimal
from datetime import date, datetime
import re


# =========================
# CUSTOMER SCHEMAS
# =========================

class CustomerCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    credit_limit: float = 0.0

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if not re.fullmatch(r"\d{10}", v):
            raise ValueError("Phone number must be exactly 10 digits")
        return v

    @field_validator("credit_limit")
    @classmethod
    def credit_limit_non_negative(cls, v):
        if v < 0:
            raise ValueError("Credit limit cannot be negative")
        return v


class CustomerResponse(BaseModel):
    customer_id: int
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    credit_limit: float
    credit_balance: float
    risk_level: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class CustomerDetailResponse(CustomerResponse):
    total_purchases: float = 0.0
    total_payments: float = 0.0
    outstanding_balance: float = 0.0
    average_order_value: float = 0.0
    purchase_count: int = 0


class RiskCustomerResponse(BaseModel):
    customer_id: int
    name: str
    phone: str
    credit_limit: float
    credit_balance: float
    risk_percentage: float
    risk_level: str


# =========================
# CREDIT LIMIT SCHEMAS
# =========================

class CreditLimitUpdate(BaseModel):
    credit_limit: float
    reason: str

    @field_validator("credit_limit")
    @classmethod
    def must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Credit limit must be greater than 0")
        return v


# =========================
# PAYMENT SCHEMAS
# =========================

class PaymentCreate(BaseModel):
    amount: float
    mode: str
    reference: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("Payment amount must be greater than 0")
        return v

    @field_validator("mode")
    @classmethod
    def valid_mode(cls, v):
        if v not in ("cash", "upi", "cheque", "transfer"):
            raise ValueError("Mode must be cash, upi, cheque, or transfer")
        return v


class PaymentResponse(BaseModel):
    message: str
    customer_id: int
    amount_paid: float
    remaining_balance: float


# =========================
# CREDIT FREEZE SCHEMAS
# =========================

class CreditFreezeRequest(BaseModel):
    reason: str
    duration_days: int

    @field_validator("duration_days")
    @classmethod
    def positive_duration(cls, v):
        if v <= 0:
            raise ValueError("Duration must be at least 1 day")
        return v


class CreditFreezeResponse(BaseModel):
    message: str
    customer_id: int
    duration_days: int
    reason: str