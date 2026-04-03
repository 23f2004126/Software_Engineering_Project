from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Date,
    DECIMAL, Enum, Text, Boolean
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


# =========================
# ROLES
# =========================
class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)

    users = relationship("User", back_populates="role")


# =========================
# DESIGNATIONS
# =========================
class Designation(Base):
    __tablename__ = "designations"

    designation_id = Column(Integer, primary_key=True, index=True)
    designation_name = Column(String(50), unique=True, nullable=False)

    users = relationship("User", back_populates="designation")


# =========================
# USERS
# =========================
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)

    role_id = Column(Integer, ForeignKey("roles.role_id"), nullable=True)
    designation_id = Column(Integer, ForeignKey("designations.designation_id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    role = relationship("Role", back_populates="users")
    designation = relationship("Designation", back_populates="users")

    shifts = relationship("Shift", back_populates="user")
    bills = relationship("Sale", back_populates="user")
    damage_loss_records = relationship("DamageLossRecord", back_populates="user")


# =========================
# SHIFTS
# =========================
class Shift(Base):
    __tablename__ = "shifts"

    shift_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    shift_date = Column(Date, nullable=True)

    status = Column(
        Enum("active", "completed", "cancelled", name="shift_status"),
        default="active"
    )

    user = relationship("User", back_populates="shifts")


# =========================
# CATEGORY
# (kept here so routes that import from app.models.user still work;
#  the same table is defined in sale.py — pick one canonical home.
#  Routes in categories.py import Category from app.models.user.)
# =========================
class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(50), unique=True, nullable=False)


# =========================
# CUSTOMER
# FIX: was completely missing — imported by customers.py, transactions.py,
#      sales.py, dashboard.py all via: from app.models.user import Customer
# =========================
class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True, index=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)

    credit_limit = Column(DECIMAL(10, 2), default=0.0, nullable=False)
    credit_balance = Column(DECIMAL(10, 2), default=0.0, nullable=False)
    risk_level = Column(String(20), default="low", nullable=True)

    status = Column(String(20), default="active", nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sales = relationship("Sale", back_populates="customer")
    credit_transactions = relationship("CreditTransaction", back_populates="customer")


# =========================
# CREDIT TRANSACTION
# FIX: was completely missing — imported by customers.py, transactions.py,
#      and sales.py via: from app.models.user import CreditTransaction
# =========================
class CreditTransaction(Base):
    __tablename__ = "credit_transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(
        Integer, ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False, index=True
    )
    sale_id = Column(Integer, ForeignKey("bills.bill_id"), nullable=True)

    amount = Column(DECIMAL(10, 2), nullable=False)

    # type: debit (purchase/charge), credit (payment), credit_limit_change, credit_freeze, reversal
    type = Column(String(30), nullable=False, index=True)

    # status: pending, paid, overdue, waived
    status = Column(String(20), default="pending", nullable=False, index=True)

    note = Column(Text, nullable=True)
    due_date = Column(Date, nullable=True)
    transaction_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    customer = relationship("Customer", back_populates="credit_transactions")


# =========================
# EXPENSE
# FIX: was completely missing — imported by expenses.py and dashboard.py
#      via: from app.models.user import Expense
# =========================
class Expense(Base):
    __tablename__ = "expenses"

    expense_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)

    category = Column(String(50), nullable=False)
    expense_date = Column(Date, nullable=False)
    note = Column(Text, nullable=True)
    recurring = Column(Boolean, default=False, nullable=False)

    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# =========================
# SUPPLIER
# FIX: was completely missing — imported by supplier.py route
#      via: from app.models.user import Supplier
# =========================
class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    contact_person = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)

    rating = Column(DECIMAL(2, 1), default=0.0, nullable=False)
    payment_terms = Column(Integer, default=30, nullable=False)

    status = Column(String(20), default="active", nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    products = relationship("Product", back_populates="supplier")
    payments = relationship("SupplierPayment", back_populates="supplier")


# =========================
# MILK SUBSCRIBERS
# =========================
class MilkSubscriber(Base):
    __tablename__ = "milk_subscribers"

    subscriber_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(
        Integer, ForeignKey("customers.customer_id"), unique=True, nullable=False
    )

    daily_quantity = Column(DECIMAL(5, 2), nullable=False)
    price_per_liter = Column(DECIMAL(10, 2), nullable=False)

    start_date = Column(Date, nullable=True)
    status = Column(
        Enum("active", "inactive", name="subscriber_status"),
        default="active",
        nullable=False
    )


# =========================
# MILK DAILY ENTRIES
# =========================
class MilkDailyEntry(Base):
    __tablename__ = "milk_daily_entries"

    entry_id = Column(Integer, primary_key=True, index=True)
    subscriber_id = Column(
        Integer, ForeignKey("milk_subscribers.subscriber_id"), nullable=False
    )
    delivered_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)

    entry_date = Column(Date, nullable=False, index=True)
    quantity = Column(DECIMAL(5, 2), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)