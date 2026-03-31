from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Date, 
    DECIMAL, Enum, Text
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
    phone = Column(String(20))

    role_id = Column(Integer, ForeignKey("roles.role_id"))
    designation_id = Column(Integer, ForeignKey("designations.designation_id"))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    role = relationship("Role", back_populates="users")
    designation = relationship("Designation", back_populates="users")

    shifts = relationship("Shift", back_populates="user")
    bills = relationship("Sale", back_populates="user")


# =========================
# SHIFTS
# =========================
class Shift(Base):
    __tablename__ = "shifts"

    shift_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))

    start_time = Column(DateTime)
    end_time = Column(DateTime)
    shift_date = Column(Date)

    status = Column(Enum("active", "completed", "cancelled", name="shift_status"))

    user = relationship("User", back_populates="shifts")


# =========================
# NOTE: Category, Product, Customer, Sale, SaleItem, Transaction models
# are now defined in app/models/sale.py to avoid duplication
# =========================
    __tablename__ = "milk_subscribers"

    subscriber_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), unique=True)

    daily_quantity = Column(DECIMAL(5, 2))
    price_per_liter = Column(DECIMAL(10, 2))

    start_date = Column(Date)
    status = Column(Enum("active", "inactive", name="subscriber_status"))


# =========================
# MILK DAILY ENTRIES
# =========================
class MilkDailyEntry(Base):
    __tablename__ = "milk_daily_entries"

    entry_id = Column(Integer, primary_key=True)
    subscriber_id = Column(Integer, ForeignKey("milk_subscribers.subscriber_id"))
    delivered_by = Column(Integer, ForeignKey("users.user_id"))

    entry_date = Column(Date)
    quantity = Column(DECIMAL(5, 2))
    amount = Column(DECIMAL(10, 2))