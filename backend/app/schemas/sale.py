from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from enum import Enum


# =========================
# ENUMS
# =========================
class PaymentMethodEnum(str, Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
    CREDIT = "credit"


class SaleStatusEnum(str, Enum):
    PAID = "paid"
    PENDING = "pending"
    CANCELLED = "cancelled"


# =========================
# PRODUCT SCHEMAS
# =========================
class ProductResponse(BaseModel):
    product_id: int
    name: str
    category_id: Optional[int] = None
    unit: Optional[str] = None
    cost_price: Optional[Decimal] = None
    price: Decimal
    stock_quantity: int

    class Config:
        from_attributes = True


# =========================
# SALE ITEM SCHEMAS
# =========================
class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal
    discount: Decimal = Decimal("0")
    tax_amount: Decimal = Decimal("0")
    subtotal: Decimal


class SaleItemResponse(BaseModel):
    bill_item_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    discount: Decimal
    tax_amount: Decimal
    subtotal: Decimal
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True


# =========================
# TRANSACTION SCHEMAS
# =========================
class TransactionCreate(BaseModel):
    amount: Decimal
    payment_mode: str  # 'cash', 'credit', 'upi'
    reference_no: Optional[str] = None


class TransactionResponse(BaseModel):
    transaction_id: int
    bill_id: int
    amount: Decimal
    payment_mode: str
    reference_no: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# SALE SCHEMAS
# =========================
class SaleCreate(BaseModel):
    customer_id: Optional[int] = None  # None for walk-in customers
    payment_method: PaymentMethodEnum  # 'cash', 'card', 'upi', 'credit'
    items: List[SaleItemCreate]
    discount_amount: Decimal = Decimal("0")


class SaleResponse(BaseModel):
    bill_id: int
    customer_id: Optional[int] = None
    user_id: Optional[int] = None
    bill_date: datetime
    total_amount: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    payment_method: PaymentMethodEnum
    status: SaleStatusEnum
    receipt_number: str
    created_at: datetime
    updated_at: datetime
    items: List[SaleItemResponse] = []
    transactions: List[TransactionResponse] = []

    class Config:
        from_attributes = True


# =========================
# SALES HISTORY (LIST) SCHEMAS
# =========================
class SalesHistoryFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    payment_method: Optional[str] = None
    status: Optional[str] = None
    customer_id: Optional[int] = None


class SalesHistorySummary(BaseModel):
    bill_id: int
    receipt_number: str
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    bill_date: datetime
    total_amount: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    payment_method: PaymentMethodEnum
    status: str


# =========================
# DAILY SUMMARY SCHEMA
# =========================
class DailySummaryResponse(BaseModel):
    date: str
    total_sales: Decimal
    total_discount: Decimal
    total_tax: Decimal
    total_revenue: Decimal
    transaction_count: int
    payment_breakdown: dict  # e.g., {'cash': 1000, 'card': 500}


# =========================
# PRODUCT SEARCH RESPONSE
# =========================
class ProductSearchResponse(BaseModel):
    product_id: int
    name: str
    price: Decimal
    stock_quantity: int
    cost_price: Optional[Decimal] = None

    class Config:
        from_attributes = True
