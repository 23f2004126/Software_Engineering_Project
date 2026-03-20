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
    bills = relationship("Bill", back_populates="user")


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
# CATEGORIES
# =========================
class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True)
    category_name = Column(String(50), unique=True, nullable=False)

    products = relationship("Product", back_populates="category")


# =========================
# PRODUCTS
# =========================
class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)

    category_id = Column(Integer, ForeignKey("categories.category_id"))
    unit = Column(String(20))
    price = Column(DECIMAL(10, 2))
    stock_quantity = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="products")
    bill_items = relationship("BillItem", back_populates="product")


# =========================
# CUSTOMERS
# =========================
class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    phone = Column(String(20), index=True)
    address = Column(Text)
    credit_balance = Column(DECIMAL(10, 2), default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    bills = relationship("Bill", back_populates="customer")
    transactions = relationship("CreditTransaction", back_populates="customer")


# =========================
# BILLS
# =========================
class Bill(Base):
    __tablename__ = "bills"

    bill_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))

    bill_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(DECIMAL(10, 2))

    payment_method = Column(Enum("cash", "card", "upi", "credit", name="payment_method"))
    status = Column(Enum("paid", "pending", "cancelled", name="bill_status"))

    customer = relationship("Customer", back_populates="bills")
    user = relationship("User", back_populates="bills")
    items = relationship("BillItem", back_populates="bill", cascade="all, delete")


# =========================
# BILL ITEMS
# =========================
class BillItem(Base):
    __tablename__ = "bill_items"

    bill_item_id = Column(Integer, primary_key=True)
    bill_id = Column(Integer, ForeignKey("bills.bill_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))

    quantity = Column(Integer)
    price = Column(DECIMAL(10, 2))
    subtotal = Column(DECIMAL(10, 2))

    bill = relationship("Bill", back_populates="items")
    product = relationship("Product", back_populates="bill_items")


# =========================
# CREDIT TRANSACTIONS
# =========================
class CreditTransaction(Base):
    __tablename__ = "credit_transactions"

    transaction_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))

    amount = Column(DECIMAL(10, 2))
    type = Column(Enum("credit", "payment", name="credit_type"))
    transaction_date = Column(DateTime, default=datetime.utcnow)
    note = Column(Text)

    customer = relationship("Customer", back_populates="transactions")


# =========================
# EXPENSES
# =========================
class Expense(Base):
    __tablename__ = "expenses"

    expense_id = Column(Integer, primary_key=True)
    title = Column(String(100))
    amount = Column(DECIMAL(10, 2))
    category = Column(String(50))
    expense_date = Column(Date)
    note = Column(Text)


# =========================
# SUPPLIERS
# =========================
class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    purchases = relationship("PurchaseOrder", back_populates="supplier")


# =========================
# PURCHASE ORDERS
# =========================
class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    purchase_id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))

    quantity = Column(Integer)
    price = Column(DECIMAL(10, 2))
    total_cost = Column(DECIMAL(10, 2))
    purchase_date = Column(Date)

    supplier = relationship("Supplier", back_populates="purchases")


# =========================
# LOSS LOGS
# =========================
class LossLog(Base):
    __tablename__ = "loss_logs"

    loss_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id"))

    quantity_lost = Column(Integer)
    reason = Column(String(255))
    loss_date = Column(Date)


# =========================
# MILK SUBSCRIBERS
# =========================
class MilkSubscriber(Base):
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