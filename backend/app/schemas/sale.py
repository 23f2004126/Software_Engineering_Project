from pydantic import BaseModel, field_validator
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
# PRODUCT SCHEMAS (used inside sale responses)
# =========================

class ProductSearchResponse(BaseModel):
    """Used by /api/sales/products/search and barcode lookup."""
    product_id: int
    name: str
    sku: Optional[str] = None
    barcode: Optional[str] = None
    unit: Optional[str] = None
    price: Optional[Decimal] = None
    cost: Optional[Decimal] = None      
    stock: int = 0                       
    category_id: Optional[int] = None
    status: Optional[str] = None

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
    
    @field_validator("subtotal")
    @classmethod
    def validate_subtotal(cls, v, info):
        if "quantity" in info.data and "unit_price" in info.data:
            quantity = info.data["quantity"]
            unit_price = info.data["unit_price"]
            discount = info.data.get("discount", Decimal("0"))
            tax_amount = info.data.get("tax_amount", Decimal("0"))
            
            base_subtotal = Decimal(str(quantity)) * unit_price
            calculated_subtotal = base_subtotal - discount + tax_amount
            
            if abs(v - calculated_subtotal) > Decimal("0.01"):  # Allow for rounding
                raise ValueError(
                    f"Item subtotal {v} does not match calculated subtotal {calculated_subtotal}. "
                    f"Expected: {quantity} x {unit_price} - {discount} + {tax_amount} = {calculated_subtotal}"
                )
        return v                   


class SaleItemResponse(BaseModel):
    bill_item_id: int                    
    bill_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    discount: Decimal
    tax_amount: Decimal
    subtotal: Decimal                      

    class Config:
        from_attributes = True


# =========================
# TRANSACTION SCHEMAS
# =========================

class TransactionCreate(BaseModel):
    amount: Decimal
    payment_mode: str                    # 'cash', 'upi', 'credit'
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
    customer_id: Optional[int] = None       # None = walk-in customer
    payment_method: PaymentMethodEnum
    items: List[SaleItemCreate]
    discount_amount: Decimal = Decimal("0")

    # Set by the route before passing to the service — not sent by client
    receipt_number: Optional[str] = None
    tax_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None


class SaleResponse(BaseModel):
    bill_id: int                             # model PK: bill_id
    customer_id: Optional[int] = None
    user_id: Optional[int] = None
    receipt_number: str
    bill_date: datetime                    
    total_amount: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    payment_method: PaymentMethodEnum
    status: SaleStatusEnum
    created_at: datetime
    updated_at: datetime
    items: List[SaleItemResponse] = []
    transactions: List[TransactionResponse] = []

    class Config:
        from_attributes = True


# =========================
# SALES HISTORY SCHEMAS
# =========================

class SalesHistorySummary(BaseModel):
    """Lightweight row used in the sales history list."""
    bill_id: int
    receipt_number: str
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None     # Resolved by the route from Sale.customer
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
    payment_breakdown: dict              # e.g., {"cash": 1000.0, "upi": 500.0, "credit": 200.0}