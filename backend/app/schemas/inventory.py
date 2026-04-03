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
    barcode: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    cost: Decimal = Field(..., gt=0)          
    stock: int = Field(default=0, ge=0)       
    reorder_level: int = Field(default=10, ge=0)
    max_stock: int = Field(default=1000, ge=0)
    unit: Optional[str] = None
    supplier_id: Optional[int] = None
    expiry_date: Optional[date] = None
    manufactured_date: Optional[date] = None
    status: str = "active"

    @field_validator("cost")
    @classmethod
    def validate_cost_less_than_price(cls, v, info):
        if "price" in info.data and info.data["price"] and v >= info.data["price"]:
            raise ValueError("Cost must be less than selling price")
        return v

    @field_validator("reorder_level")
    @classmethod
    def validate_reorder_less_than_max(cls, v, info):
        if "max_stock" in info.data and info.data["max_stock"] and v >= info.data["max_stock"]:
            raise ValueError("Reorder level must be less than max stock")
        return v

    @field_validator("expiry_date")
    @classmethod
    def validate_expiry_date(cls, v):
        if v and v <= date.today():
            raise ValueError("Expiry date must be in the future")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v not in ("active", "discontinued"):
            raise ValueError("Status must be 'active' or 'discontinued'")
        return v


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[Decimal] = Field(None, gt=0)
    cost: Optional[Decimal] = Field(None, gt=0)
    reorder_level: Optional[int] = Field(None, ge=0)
    max_stock: Optional[int] = Field(None, ge=0)
    unit: Optional[str] = None
    supplier_id: Optional[int] = None
    expiry_date: Optional[date] = None
    manufactured_date: Optional[date] = None
    status: Optional[str] = None

    @field_validator("expiry_date")
    @classmethod
    def validate_expiry_date(cls, v):
        if v and v <= date.today():
            raise ValueError("Expiry date must be in the future")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v is not None and v not in ("active", "discontinued"):
            raise ValueError("Status must be 'active' or 'discontinued'")
        return v


class ProductResponse(BaseModel):
    product_id: int
    name: str
    category_id: Optional[int] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    price: Optional[Decimal] = None
    cost: Optional[Decimal] = None            
    stock: int = 0                            
    reorder_level: int = 10
    max_stock: int = 1000
    unit: Optional[str] = None
    supplier_id: Optional[int] = None
    expiry_date: Optional[date] = None
    manufactured_date: Optional[date] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Computed fields (set by route/service, not from DB directly)
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
    quantity_change: int          
    previous_stock: Optional[int] = None
    new_stock: Optional[int] = None
    reference_id: Optional[str] = None
    notes: Optional[str] = None  
    created_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class StockAdjustmentRequest(BaseModel):
    product_id: int
    quantity: int               
    reason: str
    notes: Optional[str] = None


# =========================
# DAMAGE / LOSS SCHEMAS
# =========================

class DamageLossCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)          
    reason: str                              
    estimated_loss: Decimal = Field(..., gt=0)  
    notes: Optional[str] = None

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v):
        valid = ("damaged", "expired", "theft", "other")
        if v not in valid:
            raise ValueError(f"Reason must be one of {valid}")
        return v


class DamageLossResponse(BaseModel):
    id: int                                  
    product_id: int
    quantity: int
    reason: str
    estimated_loss: Decimal
    notes: Optional[str] = None
    reported_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# ALERT & REPORT SCHEMAS
# =========================

class LowStockAlert(BaseModel):
    product_id: int
    name: str
    sku: Optional[str] = None
    stock: int                   
    reorder_level: int
    shortage: int                


class ExpiryAlert(BaseModel):
    product_id: int
    name: str
    sku: Optional[str] = None
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
    by_reason: dict              
    by_product: List[dict]        


# =========================
# PAGINATION
# =========================

class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 100
    category: Optional[str] = None
    status: Optional[str] = "active"
    search: Optional[str] = None


# Resolve forward references
ProductDetailResponse.model_rebuild()