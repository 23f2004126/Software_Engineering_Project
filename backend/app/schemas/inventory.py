from pydantic import BaseModel, field_validator, Field
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal


# =========================
# PRODUCT SCHEMAS
# =========================
class ProductCreate(BaseModel):
    name: str
    category_id: Optional[int] = None
    sku: str
    barcode: str
    price: Decimal = Field(..., gt=0)
    cost_price: Decimal = Field(..., gt=0)
    stock_quantity: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=10, ge=0)
    max_stock: int = Field(default=100, ge=0)
    unit: Optional[str] = None
    expiry_date: Optional[date] = None
    status: str = "active"

    @field_validator("price", "cost_price")
    @classmethod
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError("Price and cost must be positive")
        return v

    @field_validator("cost_price")
    @classmethod
    def validate_cost_less_than_price(cls, v, info):
        if "price" in info.data and v >= info.data["price"]:
            raise ValueError("Cost price must be less than selling price")
        return v

    @field_validator("reorder_level")
    @classmethod
    def validate_reorder_level(cls, v, info):
        if "max_stock" in info.data and v >= info.data["max_stock"]:
            raise ValueError("Reorder level must be less than max stock")
        return v

    @field_validator("expiry_date")
    @classmethod
    def validate_expiry_date(cls, v):
        if v and v <= date.today():
            raise ValueError("Expiry date must be in the future")
        return v


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[Decimal] = Field(None, gt=0)
    cost_price: Optional[Decimal] = Field(None, gt=0)
    reorder_level: Optional[int] = Field(None, ge=0)
    max_stock: Optional[int] = Field(None, ge=0)
    unit: Optional[str] = None
    expiry_date: Optional[date] = None
    status: Optional[str] = None

    @field_validator("expiry_date")
    @classmethod
    def validate_expiry_date(cls, v):
        if v and v <= date.today():
            raise ValueError("Expiry date must be in the future")
        return v


class ProductResponse(BaseModel):
    product_id: int
    name: str
    category_id: Optional[int] = None
    sku: str
    barcode: str
    price: Decimal
    cost_price: Decimal
    stock_quantity: int
    reorder_level: int
    max_stock: int
    unit: Optional[str] = None
    expiry_date: Optional[date] = None
    status: str
    created_at: datetime
    updated_at: datetime

    # Calculated fields
    profit_margin: Optional[float] = None
    inventory_value: Optional[Decimal] = None

    class Config:
        from_attributes = True


class ProductDetailResponse(ProductResponse):
    stock_movements: List["StockMovementResponse"] = []
    low_stock_alert: Optional[bool] = None
    expiring_soon_alert: Optional[bool] = None

    class Config:
        from_attributes = True


# =========================
# STOCK MOVEMENT SCHEMAS
# =========================
class StockMovementResponse(BaseModel):
    movement_id: int
    product_id: int
    movement_type: str
    quantity: int
    reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class StockAdjustmentRequest(BaseModel):
    product_id: int
    quantity: int
    movement_type: str = "adjustment"
    reason: str
    notes: Optional[str] = None


# =========================
# DAMAGE/LOSS SCHEMAS
# =========================
class DamageLossCreate(BaseModel):
    product_id: int
    quantity_lost: int = Field(..., gt=0)
    loss_type: str  # 'damaged', 'expired', 'theft', 'other'
    reason: Optional[str] = None
    loss_value: Optional[Decimal] = None

    @field_validator("loss_type")
    @classmethod
    def validate_loss_type(cls, v):
        valid_types = ["damaged", "expired", "theft", "other"]
        if v not in valid_types:
            raise ValueError(f"Loss type must be one of {valid_types}")
        return v


class DamageLossResponse(BaseModel):
    record_id: int
    product_id: int
    quantity_lost: int
    loss_type: str
    loss_value: Optional[Decimal] = None
    reason: Optional[str] = None
    reported_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# INVENTORY REPORT SCHEMAS
# =========================
class LowStockAlert(BaseModel):
    product_id: int
    name: str
    sku: str
    current_stock: int
    reorder_level: int
    shortage: int  # reorder_level - current_stock


class ExpiryAlert(BaseModel):
    product_id: int
    name: str
    sku: str
    expiry_date: date
    days_until_expiry: int
    stock: int


class InventoryValueResponse(BaseModel):
    total_inventory_value: Decimal
    number_of_products: int
    average_product_value: Decimal


class DamageLossReport(BaseModel):
    total_loss_count: int
    total_financial_loss: Decimal
    by_reason: dict  # e.g., {"expired": {count: 5, loss: 500}, ...}
    by_product: List[dict]  # e.g., [{product_id, name, count, loss}]


class InventoryFilterResponse(BaseModel):
    category: Optional[str] = None
    status: Optional[str] = None
    search_query: Optional[str] = None
    total_count: int
    products: List[ProductResponse]


# =========================
# PAGINATION
# =========================
class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 100
    category: Optional[str] = None
    status: Optional[str] = "active"
    search: Optional[str] = None
