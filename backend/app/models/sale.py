from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Date,
    DECIMAL, Enum, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


# =========================
# PRODUCT MODEL
# =========================
class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True)
    # Keep this model aligned with the *actual* MySQL schema currently present.
    # (See `backend/inspect_db.py` output.)
    unit = Column(String(20), nullable=True)
    price = Column(DECIMAL(10, 2), nullable=True)
    stock = Column(Integer, default=0, nullable=False, name="stock_quantity")
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sale_items = relationship("SaleItem", back_populates="product")


# =========================
# SALE MODEL (Bills Table)
# =========================
class Sale(Base):
    __tablename__ = "bills"

    bill_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)

    receipt_number = Column(String(50), unique=True, nullable=False, index=True)
    bill_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    total_amount = Column(DECIMAL(10, 2), nullable=False)
    discount_amount = Column(DECIMAL(10, 2), default=0)
    tax_amount = Column(DECIMAL(10, 2), default=0)

    payment_method = Column(
        Enum("cash", "card", "upi", "credit", name="payment_method"),
        nullable=False
    )

    status = Column(
        Enum("paid", "pending", "cancelled", name="sale_status"),
        default="pending",
        nullable=False
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="sales")
    user = relationship("User", back_populates="bills")
    items = relationship("SaleItem", back_populates="sale")
    credit_transactions = relationship("CreditTransaction", back_populates="sale")


# =========================
# SALE ITEM MODEL
# =========================
class SaleItem(Base):
    __tablename__ = "bill_items"

    bill_item_id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.bill_id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)

    quantity = Column(Integer, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    subtotal = Column(DECIMAL(10, 2), nullable=False)

    # Relationships
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")


# Late import to avoid circular dependency — inventory models reference Product
from app.models.inventory import StockMovement, DamageLossRecord  # noqa: E402, F401