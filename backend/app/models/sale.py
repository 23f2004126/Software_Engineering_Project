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

    sku = Column(String(50), unique=True, nullable=True, index=True)
    barcode = Column(String(100), unique=True, nullable=True, index=True)

    unit = Column(String(20), nullable=True)
    cost = Column(DECIMAL(10, 2), nullable=True, name="cost_price")
    price = Column(DECIMAL(10, 2), nullable=True)

    stock = Column(Integer, default=0, nullable=False, name="stock_quantity")

    reorder_level = Column(Integer, default=10)
    max_stock = Column(Integer, default=1000)

    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"), nullable=True)

    expiry_date = Column(Date, nullable=True)
    manufactured_date = Column(Date, nullable=True)

    status = Column(String(20), default="active", nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sale_items = relationship("SaleItem", back_populates="product")
    stock_movements = relationship(
        "StockMovement", back_populates="product", cascade="all, delete-orphan"
    )
    damage_loss_records = relationship(
        "DamageLossRecord", back_populates="product", cascade="all, delete-orphan"
    )
    supplier = relationship("Supplier", back_populates="products")


# =========================
# SALE MODEL (Bills Table)
# =========================
class Sale(Base):
    __tablename__ = "bills"

    bill_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)

    receipt_number = Column(String(50), unique=True, nullable=False, index=True)

    # FIX: was missing bill_date — routes filter/group by Sale.bill_date
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
        nullable=False,
        index=True
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="sales")
    user = relationship("User", back_populates="bills")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    transactions = relationship(
        "Transaction", back_populates="sale", cascade="all, delete-orphan"
    )


# =========================
# SALE ITEM MODEL
# =========================
class SaleItem(Base):
    __tablename__ = "bill_items"

    bill_item_id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.bill_id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)

    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    discount = Column(DECIMAL(10, 2), default=0)
    tax_amount = Column(DECIMAL(10, 2), default=0)
    total = Column(DECIMAL(10, 2), nullable=False, name="subtotal")

    # Relationships
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")


# =========================
# TRANSACTION MODEL (Payment Tracking)
# =========================
class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.bill_id", ondelete="CASCADE"), nullable=False)

    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_mode = Column(
        Enum("cash", "upi", "credit", name="payment_mode"),
        nullable=False
    )
    reference_no = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sale = relationship("Sale", back_populates="transactions")


# Late import to avoid circular dependency — inventory models reference Product
from app.models.inventory import StockMovement, DamageLossRecord  # noqa: E402, F401