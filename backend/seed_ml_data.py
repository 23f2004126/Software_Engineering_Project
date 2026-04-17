"""
ML Test Data Seeder
Run this once to populate the DB with 90 days of realistic sales, expenses,
customers with credit history, and inventory — enough for all 4 ML models.

Usage:
    python seed_ml_data.py
"""

import os
import sys
import random
from datetime import date, datetime, timedelta

# Make sure app is importable
sys.path.insert(0, os.path.dirname(__file__))

from app.db import SessionLocal, engine
from app.models import (
    Base, Category, Customer, CreditTransaction,
    Expense, Product, Sale, SaleItem, User,
)
from app.security import hash_password
from sqlalchemy import select

random.seed(42)

DAYS = 90  # 90 days of history
TODAY = date.today()
START = TODAY - timedelta(days=DAYS)

# ── Helpers ──────────────────────────────────────────────────────────────────

def rand_date(start, end):
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

def seasonal_multiplier(d):
    """Weekend + month-end boost."""
    mult = 1.0
    if d.weekday() >= 5:       mult *= 1.35   # weekend
    if d.day >= 28:            mult *= 1.15   # month-end rush
    if d.month in [10, 11]:    mult *= 1.25   # festive season
    return mult

# ── Main seeder ──────────────────────────────────────────────────────────────

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # ── 1. Ensure admin user exists ──────────────────────────
    admin = db.scalar(select(User).where(User.role == "admin"))
    if not admin:
        admin = User(
            name="Admin User",
            email="admin@gmail.com",
            password=hash_password("admin@123"),
            phone="9999999999",
            role="admin",
            designation="Store_manager",
        )
        db.add(admin)
        db.flush()
        print("  Created admin user")
    else:
        print("  Admin user already exists")

    # ── 2. Categories ────────────────────────────────────────
    cat_names = ["Dairy", "Grains", "Bakery", "Snacks", "Grocery", "Beverages", "Personal Care"]
    cat_map = {}
    for name in cat_names:
        cat = db.scalar(select(Category).where(Category.category_name == name))
        if not cat:
            cat = Category(category_name=name)
            db.add(cat)
            db.flush()
        cat_map[name] = cat
    print(f"  Categories ready: {len(cat_map)}")

    # ── 3. Products ──────────────────────────────────────────
    product_defs = [
        ("Amul Butter 100g",      "Dairy",        45,  55,  30, 10, 80),
        ("Amul Milk 1L",          "Dairy",        52,  62,  50, 20, 120),
        ("Amul Cheese Slice",     "Dairy",        90, 115,  25, 10, 60),
        ("Whole Wheat Bread",     "Bakery",       28,  35,  20,  8, 50),
        ("Britannia Biscuits",    "Snacks",       18,  25,  60, 20, 150),
        ("Basmati Rice 5kg",      "Grains",      420, 470,  15,  5, 30),
        ("Aashirvaad Atta 5kg",   "Grains",      280, 320,   8,  5, 25),
        ("Maggi Noodles 70g",     "Snacks",       12,  16,  80, 30, 200),
        ("Tata Salt 1kg",         "Grocery",      18,  22,  40, 15, 100),
        ("Surf Excel 500g",       "Personal Care",95, 120,  20,  8, 50),
        ("Coca Cola 600ml",       "Beverages",    35,  45,  45, 15, 100),
        ("Frooti 200ml",          "Beverages",    15,  20,  55, 20, 120),
    ]

    products = []
    for name, cat, cost, price, stock, reorder, max_s in product_defs:
        p = db.scalar(select(Product).where(Product.name == name))
        if not p:
            expiry = None
            if cat in ("Dairy", "Bakery"):
                expiry = TODAY + timedelta(days=random.randint(3, 25))
            p = Product(
                name=name,
                category_id=cat_map[cat].category_id,
                unit="Piece" if cat != "Grains" else "Pack",
                cost_price=cost,
                price=price,
                stock_quantity=stock,
                reorder_level=reorder,
                max_stock=max_s,
                expiry_date=expiry,
                status="active",
            )
            db.add(p)
            db.flush()
        products.append(p)
    print(f"  Products ready: {len(products)}")

    # ── 4. Customers with credit history ─────────────────────
    customer_defs = [
        ("Ramesh Patil",    "9876543210", 20000, 15000, "high"),   # high risk
        ("Sunita Sharma",   "9876543211", 15000,  4000, "medium"), # medium risk
        ("Fresh Mart",      "9876543212", 25000,   800, "low"),    # low risk
        ("Vijay Traders",   "9876543213", 10000,  9500, "high"),   # high risk
        ("Meena Stores",    "9876543214", 12000,  2000, "low"),    # low risk
        ("Ravi Groceries",  "9876543215",  8000,  5500, "medium"), # medium risk
    ]

    customers = []
    for name, phone, limit, balance, risk in customer_defs:
        c = db.scalar(select(Customer).where(Customer.phone == phone))
        if not c:
            c = Customer(
                name=name, phone=phone,
                credit_limit=limit, credit_balance=balance,
                risk_level=risk, status="active",
                city="Pune",
            )
            db.add(c)
            db.flush()

            # Add credit transactions for history
            n_txns = random.randint(3, 8)
            for _ in range(n_txns):
                txn_date = rand_date(START, TODAY - timedelta(days=5))
                amount = random.randint(500, 3000)
                due = txn_date + timedelta(days=30)
                is_overdue = due < TODAY and risk in ("high", "medium")
                db.add(CreditTransaction(
                    customer_id=c.customer_id,
                    amount=amount,
                    type="debit",
                    status="overdue" if is_overdue else "pending",
                    note=f"Credit sale",
                    due_date=due,
                    transaction_date=datetime.combine(txn_date, datetime.min.time()),
                ))
        customers.append(c)
    db.flush()
    print(f"  Customers ready: {len(customers)}")

    # ── 5. Expenses (90 days) ────────────────────────────────
    expense_categories = {
        "Rent":        (3500, 0.02),
        "Utilities":   (800,  0.10),
        "Salaries":    (6000, 0.05),
        "Inventory":   (15000, 0.15),
        "Marketing":   (1200, 0.20),
        "Maintenance": (500,  0.25),
    }

    existing_expense_count = db.query(Expense).count()
    if existing_expense_count < 10:
        expense_rows = []
        for day_offset in range(DAYS):
            d = START + timedelta(days=day_offset)
            for cat, (base, noise_pct) in expense_categories.items():
                # Only add some categories daily (rent monthly, etc.)
                if cat == "Rent" and d.day != 1:
                    continue
                if cat == "Salaries" and d.day != 1:
                    continue
                amt = base + random.gauss(0, base * noise_pct)
                # Occasional spike
                if random.random() < 0.03:
                    amt *= random.uniform(2.0, 3.5)
                amt = max(50, round(amt, 2))
                expense_rows.append(Expense(
                    title=f"{cat} - {d.strftime('%b %Y')}",
                    amount=amt,
                    category=cat.lower(),
                    expense_date=d,
                    recurring=(cat in ("Rent", "Salaries")),
                    created_by=admin.user_id,
                ))
        db.add_all(expense_rows)
        db.flush()
        print(f"  Expenses created: {len(expense_rows)}")
    else:
        print(f"  Expenses already exist ({existing_expense_count}), skipping")

    # ── 6. Sales + SaleItems (90 days) ───────────────────────
    existing_sale_count = db.query(Sale).count()
    if existing_sale_count < 20:
        sale_count = 0
        item_count = 0
        receipt_counter = 1000

        for day_offset in range(DAYS):
            d = START + timedelta(days=day_offset)
            mult = seasonal_multiplier(d)
            n_bills = int(random.gauss(25, 6) * mult)
            n_bills = max(5, min(60, n_bills))

            for _ in range(n_bills):
                # Pick customer (30% chance of named customer, else walk-in)
                customer = random.choice(customers) if random.random() < 0.3 else None
                payment = random.choices(
                    ["cash", "upi", "credit", "card"],
                    weights=[45, 35, 10, 10]
                )[0]
                if payment == "credit" and not customer:
                    payment = "cash"

                # Pick 1-4 products
                n_items = random.randint(1, 4)
                chosen = random.sample(products, min(n_items, len(products)))

                items_data = []
                total = 0.0
                for prod in chosen:
                    qty = random.randint(1, 5)
                    unit_price = float(prod.price)
                    discount = round(unit_price * random.choice([0, 0, 0, 0.05, 0.10]), 2)
                    subtotal = round((unit_price - discount) * qty, 2)
                    total += subtotal
                    items_data.append((prod, qty, unit_price, discount, subtotal))

                discount_total = round(total * random.choice([0, 0, 0.02, 0.05]), 2)
                total = round(total - discount_total, 2)

                receipt_counter += 1
                sale = Sale(
                    customer_id=customer.customer_id if customer else None,
                    user_id=admin.user_id,
                    receipt_number=f"RCP-{d.strftime('%Y%m%d')}-{receipt_counter}",
                    bill_date=datetime.combine(d, datetime.min.time().replace(
                        hour=random.randint(8, 21),
                        minute=random.randint(0, 59)
                    )),
                    total_amount=total,
                    discount_amount=discount_total,
                    tax_amount=0,
                    payment_method=payment,
                    status="paid",
                )
                db.add(sale)
                db.flush()

                for prod, qty, unit_price, discount, subtotal in items_data:
                    db.add(SaleItem(
                        bill_id=sale.bill_id,
                        product_id=prod.product_id,
                        quantity=qty,
                        unit_price=unit_price,
                        discount=discount,
                        tax_amount=0,
                        subtotal=subtotal,
                    ))
                    item_count += 1

                sale_count += 1

        db.commit()
        print(f"  Sales created: {sale_count} bills, {item_count} line items")
    else:
        print(f"  Sales already exist ({existing_sale_count}), skipping")
        db.commit()

    db.close()
    print("\n✅ Seed complete. Your DB is ready for ML insights.")
    print("   Login: admin@gmail.com / admin@123")


if __name__ == "__main__":
    print("🌱 Seeding ML test data...")
    seed()
