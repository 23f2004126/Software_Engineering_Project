import pytest
import os
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Add parent directory to path so imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import Base
from app.models.sale import Product, Category, Customer, Sale, SaleItem, Transaction
from app.models.user import User, Role


# =========================
# PYTEST CONFIGURATION
# =========================

def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests (deselect with '-m \"not integration\"')"
    )
    config.addinivalue_line(
        "markers",
        "unit: marks tests as unit tests"
    )


# =========================
# PYTEST HOOKS
# =========================

@pytest.fixture(scope="session")
def setup_test_environment():
    os.environ['TESTING'] = 'true'

    print("\n" + "="*80)
    print("TEST SUITE INITIALIZATION")
    print("="*80)
    print("Running Billing & Sales + Inventory Tests")
    print("Database: SQLite In-Memory")
    print("="*80)


# =========================
# DATABASE SETUP & FIXTURES
# =========================

@pytest.fixture(scope="function")
def test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    yield db
    
    # Cleanup
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_role(test_db: Session):
    admin_role = Role(role_id=1, role_name="admin")
    employee_role = Role(role_id=2, role_name="employee")
    test_db.add(admin_role)
    test_db.add(employee_role)
    test_db.commit()
    return admin_role


@pytest.fixture
def test_user(test_db: Session, sample_role: Role):
    user = User(
        user_id=1,
        name="Test User",
        email="test@example.com",
        password="hashed_password",
        role_id=sample_role.role_id
    )
    test_db.add(user)
    test_db.commit()
    return user


@pytest.fixture
def sample_products(test_db: Session):
    category = Category(category_id=1, category_name="Dairy")
    test_db.add(category)
    test_db.commit()

    product1 = Product(
        product_id=1,
        name="Full Cream Milk 500ml",
        category_id=category.category_id,
        unit="Bottle",
        cost_price=Decimal("30.00"),
        price=Decimal("50.00"),
        stock_quantity=50
    )
    product2 = Product(
        product_id=2,
        name="Toned Milk 1L",
        category_id=category.category_id,
        unit="Liter",
        cost_price=Decimal("50.00"),
        price=Decimal("80.00"),
        stock_quantity=30
    )
    product3 = Product(
        product_id=3,
        name="Double Toned Milk 1L",
        category_id=category.category_id,
        unit="Liter",
        cost_price=Decimal("40.00"),
        price=Decimal("60.00"),
        stock_quantity=5
    )
    product4 = Product(
        product_id=4,
        name="Yogurt 400g",
        category_id=category.category_id,
        unit="Cup",
        cost_price=Decimal("25.00"),
        price=Decimal("45.00"),
        stock_quantity=20
    )
    product5 = Product(
        product_id=5,
        name="Paneer 200g",
        category_id=category.category_id,
        unit="Pack",
        cost_price=Decimal("80.00"),
        price=Decimal("150.00"),
        stock_quantity=10
    )
    test_db.add_all([product1, product2, product3, product4, product5])
    test_db.commit()
    return [product1, product2, product3, product4, product5]


@pytest.fixture
def products_with_near_expiry(test_db: Session):
    category = Category(category_id=2, category_name="Bakery")
    test_db.add(category)
    test_db.commit()

    today = date.today()
    
    # Expiring in 3 days
    product1 = Product(
        product_id=10,
        name="Bread",
        category_id=category.category_id,
        unit="Loaf",
        cost_price=Decimal("20.00"),
        price=Decimal("35.00"),
        stock_quantity=15,
        expiry_date=today + timedelta(days=3)
    )
    
    # Expiring in 7 days
    product2 = Product(
        product_id=11,
        name="Cake",
        category_id=category.category_id,
        unit="Piece",
        cost_price=Decimal("50.00"),
        price=Decimal("80.00"),
        stock_quantity=8,
        expiry_date=today + timedelta(days=7)
    )
    
    # Already expired
    product3 = Product(
        product_id=12,
        name="Biscuits",
        category_id=category.category_id,
        unit="Pack",
        cost_price=Decimal("15.00"),
        price=Decimal("25.00"),
        stock_quantity=5,
        expiry_date=today - timedelta(days=1)
    )

    test_db.add_all([product1, product2, product3])
    test_db.commit()
    return [product1, product2, product3]
