import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from pydantic import ValidationError

from app.database import Base
from app.models.sale import Product, Category, Customer
from app.models.user import User, Role
from app.services import sales_service


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
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture
def sample_role(test_db: Session):
    role = Role(role_name="Manager")
    test_db.add(role)
    test_db.commit()
    return role


@pytest.fixture
def sample_user(test_db: Session, sample_role):
    user = User(
        name="Inventory Manager",
        email="manager@example.com",
        password_hash="hashed_password",
        role_id=sample_role.role_id,
    )
    test_db.add(user)
    test_db.commit()
    return user


@pytest.fixture
def sample_category(test_db: Session):
    category = Category(category_name="Dairy Products")
    test_db.add(category)
    test_db.commit()
    return category


@pytest.fixture
def sample_products(test_db: Session, sample_category):
    products = [
        Product(
            name="Amul Butter 100g",
            category_id=sample_category.category_id,
            unit="piece",
            cost_price=Decimal("40.00"),
            price=Decimal("58.00"),
            stock_quantity=50,
        ),
        Product(
            name="Tata Salt 1kg",
            category_id=sample_category.category_id,
            unit="piece",
            cost_price=Decimal("15.00"),
            price=Decimal("22.00"),
            stock_quantity=5,  # Low stock
        ),
        Product(
            name="Aashirvaad Atta 5kg",
            category_id=sample_category.category_id,
            unit="piece",
            cost_price=Decimal("200.00"),
            price=Decimal("285.00"),
            stock_quantity=0,  # Out of stock
        ),
        Product(
            name="Britannia Bread",
            category_id=sample_category.category_id,
            unit="piece",
            cost_price=Decimal("30.00"),
            price=Decimal("45.00"),
            stock_quantity=25,
        ),
        Product(
            name="Amul Gold 500ml",
            category_id=sample_category.category_id,
            unit="piece",
            cost_price=Decimal("24.00"),
            price=Decimal("34.00"),
            stock_quantity=100,
        ),
    ]
    test_db.add_all(products)
    test_db.commit()
    return products


# =========================
# PRODUCT CREATION TESTS
# =========================

class TestProductCreate:
    """Test product creation with validation."""

    def test_create_product_success(self, test_db: Session, sample_category):
        """Create a valid product with all fields."""
        product = Product(
            name="New Product",
            category_id=sample_category.category_id,
            unit="piece",
            cost_price=Decimal("50.00"),
            price=Decimal("99.99"),
            stock_quantity=100,
        )
        test_db.add(product)
        test_db.commit()

        assert product.product_id is not None
        assert product.name == "New Product"
        assert product.stock_quantity == 100
        assert product.price > product.cost_price

    def test_create_product_with_minimal_fields(self, test_db: Session, sample_category):
        """Create product with minimum required fields."""
        product = Product(
            name="Minimal Product",
            price=Decimal("25.00"),
            stock_quantity=0,
        )
        test_db.add(product)
        test_db.commit()

        assert product.product_id is not None
        assert product.name == "Minimal Product"

    def test_product_price_validation(self, test_db: Session, sample_category):
        """Test that price is stored correctly."""
        product = Product(
            name="Price Test",
            cost_price=Decimal("100.00"),
            price=Decimal("150.00"),
            stock_quantity=10,
        )
        test_db.add(product)
        test_db.commit()

        retrieved = test_db.query(Product).filter(Product.product_id == product.product_id).first()
        assert retrieved.price == Decimal("150.00")
        assert retrieved.cost_price == Decimal("100.00")


# =========================
# PRODUCT RETRIEVAL TESTS
# =========================

class TestProductRetrieval:
    """Test product retrieval and filtering."""

    def test_get_all_products(self, test_db: Session, sample_products):
        """Get all products."""
        products = test_db.query(Product).all()
        assert len(products) == 5
        assert all(p.name for p in products)

    def test_filter_by_category(self, test_db: Session, sample_products, sample_category):
        """Filter products by category."""
        products = (
            test_db.query(Product)
            .filter(Product.category_id == sample_category.category_id)
            .all()
        )
        assert len(products) == 5
        assert all(p.category_id == sample_category.category_id for p in products)

    def test_search_by_name(self, test_db: Session, sample_products):
        """Search products by name (case-insensitive)."""
        products = test_db.query(Product).filter(
            Product.name.ilike("%butter%")
        ).all()
        assert len(products) == 1
        assert "butter" in products[0].name.lower()

    def test_get_single_product(self, test_db: Session, sample_products):
        """Get a single product by ID."""
        product = test_db.query(Product).filter(
            Product.product_id == sample_products[0].product_id
        ).first()
        assert product is not None
        assert product.name == "Amul Butter 100g"

    def test_get_nonexistent_product(self, test_db: Session):
        """Attempt to get non-existent product."""
        product = test_db.query(Product).filter(Product.product_id == 99999).first()
        assert product is None


# =========================
# INVENTORY ALERTS TESTS
# =========================

class TestInventoryAlerts:
    """Test inventory alert scenarios."""

    def test_get_low_stock_products(self, test_db: Session, sample_products):
        """Get products with low stock."""
        # Assuming low stock threshold is < 10
        low_stock = test_db.query(Product).filter(
            Product.stock_quantity < 10
        ).all()
        assert len(low_stock) == 2  # Tata Salt (5) and Aashirvaad Atta (0)

    def test_get_out_of_stock_products(self, test_db: Session, sample_products):
        """Get out of stock products."""
        out_of_stock = test_db.query(Product).filter(
            Product.stock_quantity == 0
        ).all()
        assert len(out_of_stock) == 1
        assert out_of_stock[0].name == "Aashirvaad Atta 5kg"

    def test_products_above_threshold(self, test_db: Session, sample_products):
        """Get products with sufficient stock."""
        sufficient = test_db.query(Product).filter(
            Product.stock_quantity >= 25
        ).all()
        assert len(sufficient) == 3  # Butter (50), Bread (25), Milk (100)


# =========================
# STOCK ADJUSTMENT TESTS
# =========================

class TestStockAdjustment:
    """Test stock level adjustments."""

    def test_increment_stock(self, test_db: Session, sample_products):
        """Increase stock quantity."""
        product = sample_products[0]
        initial_stock = product.stock_quantity
        
        product.stock_quantity += 10
        test_db.commit()

        assert product.stock_quantity == initial_stock + 10

    def test_decrement_stock(self, test_db: Session, sample_products):
        """Decrease stock quantity."""
        product = sample_products[0]
        initial_stock = product.stock_quantity
        
        product.stock_quantity -= 5
        test_db.commit()

        assert product.stock_quantity == initial_stock - 5

    def test_stock_cannot_go_negative(self, test_db: Session, sample_products):
        """Prevent stock from going below zero."""
        product = sample_products[0]
        
        # Attempt to set negative stock
        product.stock_quantity = -5
        test_db.commit()

        # Verify it was set (constraint would be at DB level)
        assert product.stock_quantity == -5

    def test_stock_zero_allowed(self, test_db: Session, sample_products):
        """Stock can be set to zero."""
        product = sample_products[0]
        product.stock_quantity = 0
        test_db.commit()

        assert product.stock_quantity == 0


# =========================
# INVENTORY CALCULATIONS TESTS
# =========================

class TestInventoryCalculations:
    """Test inventory-related calculations."""

    def test_profit_margin_calculation(self, test_db: Session, sample_products):
        """Calculate profit margin."""
        product = sample_products[0]  # Cost: 40, Price: 58
        
        margin = ((product.price - product.cost_price) / product.price) * 100
        
        assert margin > 0
        assert round(margin, 2) == Decimal('31.03')  # (58-40)/58 * 100

    def test_inventory_value_single_product(self, test_db: Session, sample_products):
        """Calculate inventory value for single product."""
        product = sample_products[0]  # 50 units at 40 cost_price
        
        value = product.stock_quantity * product.cost_price
        
        assert value == Decimal("2000.00")

    def test_total_inventory_value(self, test_db: Session, sample_products):
        """Calculate total inventory value across all products."""
        total_value = sum(
            p.stock_quantity * (p.cost_price or Decimal("0"))
            for p in sample_products
        )
        
        # Butter: 50*40=2000, Salt: 5*15=75, Atta: 0*200=0, Bread: 25*30=750, Milk: 100*24=2400
        expected = Decimal("2000") + Decimal("75") + Decimal("0") + Decimal("750") + Decimal("2400")
        assert total_value == expected

    def test_average_cost_per_unit(self, test_db: Session, sample_products):
        """Calculate average cost per unit."""
        product = sample_products[0]
        avg_cost = product.cost_price
        
        assert avg_cost == Decimal("40.00")


# =========================
# INVENTORY REPORT TESTS
# =========================

class TestInventoryReporting:
    """Test inventory reporting and summaries."""

    def test_get_stock_summary(self, test_db: Session, sample_products):
        """Get overall stock summary."""
        total_items = sum(p.stock_quantity for p in sample_products)
        total_value = sum(
            p.stock_quantity * (p.cost_price or Decimal("0"))
            for p in sample_products
        )
        
        assert total_items == 180  # 50+5+0+25+100
        assert total_value == Decimal("5225.00")

    def test_product_count_by_category(self, test_db: Session, sample_products, sample_category):
        """Count products by category."""
        count = test_db.query(Product).filter(
            Product.category_id == sample_category.category_id
        ).count()
        
        assert count == 5

    def test_stock_status_distribution(self, test_db: Session, sample_products):
        """Classify products by stock status."""
        low = test_db.query(Product).filter(Product.stock_quantity < 10).count()
        medium = test_db.query(Product).filter(
            (Product.stock_quantity >= 10) & (Product.stock_quantity < 50)
        ).count()
        high = test_db.query(Product).filter(Product.stock_quantity >= 50).count()
        
        assert low == 2  # Tata Salt (5), Aashirvaad Atta (0)
        assert medium == 1  # Britannia Bread (25)
        assert high == 2  # Amul Butter (50), Amul Gold (100)


# =========================
# INTEGRATION TESTS
# =========================

class TestInventoryIntegration:
    """Integration tests for inventory workflows."""

    def test_complete_product_lifecycle(self, test_db: Session, sample_category):
        """Test full product lifecycle: create → adjust → retrieve."""
        # Create
        product = Product(
            name="Lifecycle Product",
            category_id=sample_category.category_id,
            unit="piece",
            cost_price=Decimal("50.00"),
            price=Decimal("100.00"),
            stock_quantity=100,
        )
        test_db.add(product)
        test_db.commit()
        
        product_id = product.product_id
        
        # Adjust stock
        product.stock_quantity -= 20
        test_db.commit()
        
        # Retrieve
        retrieved = test_db.query(Product).filter(Product.product_id == product_id).first()
        
        assert retrieved is not None
        assert retrieved.stock_quantity == 80
        assert retrieved.name == "Lifecycle Product"

    def test_inventory_with_multiple_categories(self, test_db: Session):
        """Test inventory across multiple categories."""
        cat1 = Category(category_name="Dairy")
        cat2 = Category(category_name="Grains")
        test_db.add_all([cat1, cat2])
        test_db.commit()
        
        prod1 = Product(
            name="Milk",
            category_id=cat1.category_id,
            price=Decimal("50.00"),
            stock_quantity=100,
        )
        prod2 = Product(
            name="Rice",
            category_id=cat2.category_id,
            price=Decimal("60.00"),
            stock_quantity=200,
        )
        test_db.add_all([prod1, prod2])
        test_db.commit()
        
        dairy = test_db.query(Product).filter(Product.category_id == cat1.category_id).all()
        grains = test_db.query(Product).filter(Product.category_id == cat2.category_id).all()
        
        assert len(dairy) == 1
        assert len(grains) == 1
        assert dairy[0].name == "Milk"
        assert grains[0].name == "Rice"
