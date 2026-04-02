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
    category_id = Column(Integer, ForeignKey("categories.category_id"))

    sku = Column(String(50), unique=True, nullable=True, index=True)
    barcode = Column(String(100), unique=True, nullable=True, index=True)

    unit = Column(String(20))
    cost_price = Column(DECIMAL(10, 2))
    price = Column(DECIMAL(10, 2))
    stock_quantity = Column(Integer, default=0)

    reorder_level = Column(Integer, default=10)
    max_stock = Column(Integer, default=100)
    expiry_date = Column(Date, nullable=True)
    status = Column(String(20), default="active")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bill_items = relationship("SaleItem", back_populates="product")
    stock_movements = relationship("StockMovement", back_populates="product", cascade="all, delete-orphan")
    damage_loss_records = relationship("DamageLossRecord", back_populates="product", cascade="all, delete-orphan")


# =========================
# CATEGORY MODEL
# =========================
class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(50), unique=True, nullable=False)


# =========================
# CUSTOMER MODEL
# =========================
class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    credit_balance = Column(DECIMAL(10, 2), default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    bills = relationship("Sale", back_populates="customer")


# =========================
# SALE MODEL (Bills Table)
# =========================
class Sale(Base):
    __tablename__ = "bills"

    bill_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))

    bill_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(DECIMAL(10, 2))
    discount_amount = Column(DECIMAL(10, 2), default=0)
    tax_amount = Column(DECIMAL(10, 2), default=0)

    payment_method = Column(Enum("cash", "card", "upi", "credit", name="payment_method"))
    status = Column(Enum("paid", "pending", "cancelled", name="sale_status"))
    receipt_number = Column(String(50), unique=True, nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer", back_populates="bills")
    user = relationship("User", back_populates="bills")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="sale", cascade="all, delete-orphan")


# =========================
# SALE ITEM MODEL (Bill Items Table)
# =========================
class SaleItem(Base):
    __tablename__ = "bill_items"

    bill_item_id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.bill_id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.product_id"))

    quantity = Column(Integer)
    unit_price = Column(DECIMAL(10, 2))
    discount = Column(DECIMAL(10, 2), default=0)
    tax_amount = Column(DECIMAL(10, 2), default=0)
    subtotal = Column(DECIMAL(10, 2))

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="bill_items")


# =========================
# TRANSACTION MODEL (Payment Tracking)
# =========================
class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.bill_id", ondelete="CASCADE"))

    amount = Column(DECIMAL(10, 2))
    payment_mode = Column(Enum("cash", "credit", "upi", name="payment_mode"))
    reference_no = Column(String(100))

    created_at = Column(DateTime, default=datetime.utcnow)

    sale = relationship("Sale", back_populates="transactions")


from app.models.inventory import StockMovement, DamageLossRecord  # noqa: E402, F401
