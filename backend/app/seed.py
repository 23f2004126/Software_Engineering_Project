import os
from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import Base, engine
from app.models import (
    Category,
    Customer,
    Expense,
    MilkDeliveryEntry,
    MilkSubscriber,
    Product,
    Sale,
    SaleItem,
    Supplier,
    User,
)
from app.security import hash_password


DEFAULT_CATEGORIES = ["Dairy", "Grains", "Bakery", "Snacks", "Grocery", "Personal"]


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def seed_data(db: Session) -> None:
    if db.scalar(select(User).limit(1)):
        return

    admin = User(
        name="Admin User",
        email=os.getenv("ADMIN_EMAIL", "admin@gmail.com"),
        password=hash_password(os.getenv("ADMIN_PASSWORD", "admin@123")),
        phone="9999999999",
        role="admin",
        designation="Store_manager",
    )
    employee = User(
        name="Store Employee",
        email=os.getenv("EMPLOYEE_EMAIL", "employee@gmail.com"),
        password=hash_password(os.getenv("EMPLOYEE_PASSWORD", "employee@123")),
        phone="8888888888",
        role="employee",
        designation="Sales_staff",
    )
    db.add_all([admin, employee])
    db.flush()

    categories = [Category(category_name=name) for name in DEFAULT_CATEGORIES]
    db.add_all(categories)
    db.flush()
    category_map = {category.category_name: category for category in categories}

    products = [
        Product(
            name="Amul Butter 100g",
            category_id=category_map["Dairy"].category_id,
            sku="DBT-001",
            barcode="890123450001",
            unit="Piece",
            cost_price=45,
            price=55,
            stock_quantity=28,
            reorder_level=10,
            max_stock=80,
            status="active",
            description="Salted table butter",
        ),
        Product(
            name="Whole Wheat Bread",
            category_id=category_map["Bakery"].category_id,
            sku="BBR-001",
            barcode="890123450002",
            unit="Pack",
            cost_price=28,
            price=35,
            stock_quantity=18,
            reorder_level=8,
            max_stock=40,
            expiry_date=date.today() + timedelta(days=4),
            status="active",
        ),
        Product(
            name="Basmati Rice 5kg",
            category_id=category_map["Grains"].category_id,
            sku="GRN-001",
            barcode="890123450003",
            unit="Pack",
            cost_price=420,
            price=470,
            stock_quantity=12,
            reorder_level=6,
            max_stock=25,
            status="active",
        ),
    ]
    db.add_all(products)
    db.flush()

    customer = Customer(
        name="Fresh Mart",
        phone="9876543210",
        email="freshmart@example.com",
        city="Pune",
        address="MG Road",
        credit_limit=25000,
        credit_balance=1800,
        risk_level="low",
        status="active",
    )
    milk_subscribers = [
        MilkSubscriber(
            name="Rajesh Patel",
            phone="9876543210",
            quantity=0.5,
            frequency="daily",
            start_date=date.today() - timedelta(days=90),
            status="active",
            amount=35,
            address="MG Road",
            note="Morning delivery",
        ),
        MilkSubscriber(
            name="Priya Singh",
            phone="9876543211",
            quantity=1.0,
            frequency="daily",
            start_date=date.today() - timedelta(days=60),
            status="active",
            amount=70,
            address="Baner",
        ),
    ]
    supplier = Supplier(
        name="Fresh Farms Dairy",
        contact_person="Rajesh Kumar",
        phone="9123456780",
        email="supply@example.com",
        city="Pune",
        rating=4.5,
        payment_terms=30,
        status="active",
    )
    expense = Expense(
        title="Electricity Bill",
        amount=3200,
        category="utilities",
        note="Monthly utility cost",
        expense_date=date.today(),
        recurring=True,
        created_by=admin.user_id,
    )
    db.add_all([customer, supplier, expense, *milk_subscribers])
    db.flush()

    db.add_all(
        [
            MilkDeliveryEntry(
                subscriber_id=milk_subscribers[0].subscriber_id,
                entry_date=date.today() - timedelta(days=3),
                quantity=0.5,
                temperature=4,
                quality="A+",
            ),
            MilkDeliveryEntry(
                subscriber_id=milk_subscribers[0].subscriber_id,
                entry_date=date.today() - timedelta(days=2),
                quantity=0.5,
                temperature=4,
                quality="A+",
            ),
            MilkDeliveryEntry(
                subscriber_id=milk_subscribers[0].subscriber_id,
                entry_date=date.today() - timedelta(days=1),
                quantity=0.5,
                temperature=5,
                quality="A",
            ),
            MilkDeliveryEntry(
                subscriber_id=milk_subscribers[1].subscriber_id,
                entry_date=date.today() - timedelta(days=2),
                quantity=1.0,
                temperature=4,
                quality="A+",
            ),
        ]
    )

    sale = Sale(
        customer_id=customer.customer_id,
        user_id=admin.user_id,
        receipt_number=f"RCP-{datetime.utcnow().strftime('%Y%m%d')}-0001",
        bill_date=datetime.utcnow(),
        total_amount=110,
        discount_amount=0,
        tax_amount=5,
        payment_method="cash",
        status="paid",
    )
    db.add(sale)
    db.flush()

    db.add(
        SaleItem(
            bill_id=sale.bill_id,
            product_id=products[0].product_id,
            quantity=2,
            unit_price=52.5,
            discount=0,
            tax_amount=5,
            subtotal=110,
        )
    )

    db.commit()
