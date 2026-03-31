import pytest
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from pydantic import ValidationError

from app.database import Base
from app.models.sale import Product, Category, Customer, Sale, SaleItem, Transaction
from app.models.user import User, Role
from app.services import sales_service
from app.schemas.sale import SaleCreate, SaleItemCreate


# =========================
# DATABASE SETUP & FIXTURES
# =========================

@pytest.fixture(scope="function")
def test_db():
    """
    Create an in-memory SQLite database for testing.
    Uses StaticPool to ensure the same connection is reused.
    """
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
def sample_user(test_db: Session, sample_role: Role):
    user = User(
        user_id=1,
        name="Admin User",
        email="admin@example.com",
        password="hashed_password",
        role_id=sample_role.role_id
    )
    test_db.add(user)
    test_db.commit()
    return user


@pytest.fixture
def sample_category(test_db: Session):
    category = Category(category_id=1, category_name="Dairy")
    test_db.add(category)
    test_db.commit()
    return category


@pytest.fixture
def sample_products(test_db: Session, sample_category: Category):
    product1 = Product(
        product_id=1,
        name="Full Cream Milk",
        category_id=sample_category.category_id,
        unit="Liter",
        cost_price=Decimal("60.00"),
        price=Decimal("100.00"),
        stock_quantity=50
    )
    product2 = Product(
        product_id=2,
        name="Toned Milk",
        category_id=sample_category.category_id,
        unit="Liter",
        cost_price=Decimal("50.00"),
        price=Decimal("80.00"),
        stock_quantity=30
    )
    product3 = Product(
        product_id=3,
        name="Double Toned Milk",
        category_id=sample_category.category_id,
        unit="Liter",
        cost_price=Decimal("40.00"),
        price=Decimal("60.00"),
        stock_quantity=5  # Low stock 
    )
    test_db.add_all([product1, product2, product3])
    test_db.commit()
    return [product1, product2, product3]


@pytest.fixture
def sample_customers(test_db: Session):
    customer1 = Customer(
        customer_id=1,
        name="John Doe",
        phone="9876543210",
        address="123 Main St",
        credit_balance=Decimal("10000.00")
    )
    customer2 = Customer(
        customer_id=2,
        name="Jane Smith",
        phone="9876543211",
        address="456 Oak St",
        credit_balance=Decimal("5000.00")
    )
    test_db.add_all([customer1, customer2])
    test_db.commit()
    return [customer1, customer2]


# =========================
# PRODUCT SEARCH TESTS
# =========================

class TestProductSearch:
    
    def test_search_products_by_name(self, test_db: Session, sample_products):
        results = sales_service.search_products(test_db, "Milk")
        
        # ASSERTIONS
        assert len(results) == 3, f"Expected 3 results, got {len(results)}"
        assert all("Milk" in p.name for p in results), "All results should contain 'Milk'"
        
    def test_search_products_partial_match(self, test_db: Session, sample_products):
        results = sales_service.search_products(test_db, "Toned")
        
        assert len(results) == 2, f"Expected 2 results for 'Toned', got {len(results)}"
        assert results[0].name == "Toned Milk"
        assert results[1].name == "Double Toned Milk"
        
    def test_search_products_case_insensitive(self, test_db: Session, sample_products):
        results = sales_service.search_products(test_db, "full cream")
        
        assert len(results) >= 1, "Should find product despite case difference"
        assert any("Full Cream" in p.name for p in results)
        
    def test_search_products_no_match(self, test_db: Session, sample_products):
        results = sales_service.search_products(test_db, "NonExistent")
        
        assert len(results) == 0, "Should return empty list for non-matching query"


class TestGetProduct:
    
    def test_get_product_by_id_success(self, test_db: Session, sample_products):
        product = sales_service.get_product_by_id(test_db, 1)
        
        assert product is not None, "Product should be found"
        assert product.product_id == 1
        assert product.name == "Full Cream Milk"
        assert product.price == Decimal("100.00")
        assert product.cost_price == Decimal("60.00")
        
    def test_get_product_not_found(self, test_db: Session, sample_products):
        product = sales_service.get_product_by_id(test_db, 999)
        
        assert product is None, "Should return None for non-existent product"


# =========================
# SALE CREATION TESTS
# =========================

class TestCreateSale:
    
    def test_create_sale_success_with_customer(self, test_db: Session, sample_products, sample_customers, sample_user):
        # Create sale request
        sale_data = SaleCreate(
            customer_id=1,
            payment_method="cash",
            discount_amount=Decimal("10.00"),
            items=[
                SaleItemCreate(
                    product_id=1,
                    quantity=2,
                    unit_price=Decimal("100.00"),
                    discount=Decimal("0.00"),
                    tax_amount=Decimal("10.00"),
                    subtotal=Decimal("210.00")
                ),
                SaleItemCreate(
                    product_id=2,
                    quantity=1,
                    unit_price=Decimal("80.00"),
                    discount=Decimal("0.00"),
                    tax_amount=Decimal("4.00"),
                    subtotal=Decimal("84.00")
                )
            ]
        )
        
        # Create sale
        sale, error = sales_service.create_sale(test_db, sale_data, user_id=1)
        
        # ASSERTIONS
        assert error is None, f"Should not have error. Got: {error}"
        assert sale is not None, "Sale should be created"
        assert sale.bill_id is not None
        assert sale.receipt_number is not None, "Receipt number should be generated"
        assert len(sale.receipt_number) > 0, "Receipt number should not be empty"
        assert sale.receipt_number.startswith("RCP-"), "Receipt should have correct format"
        assert sale.status == "paid", "Cash payment should have 'paid' status"
        assert sale.payment_method == "cash"
        assert sale.customer_id == 1
        assert len(sale.items) == 2, "Should have 2 items"
        assert sale.total_amount == Decimal("284.00"), f"Total should be 284 (210+84-10), got {sale.total_amount}"
        
        # Check stock was decremented
        product1 = test_db.query(Product).filter(Product.product_id == 1).first()
        product2 = test_db.query(Product).filter(Product.product_id == 2).first()
        assert product1.stock_quantity == 48, f"Product 1 stock should be 48, got {product1.stock_quantity}"
        assert product2.stock_quantity == 29, f"Product 2 stock should be 29, got {product2.stock_quantity}"
        
    def test_create_sale_success_walk_in_customer(self, test_db: Session, sample_products, sample_user):
        sale_data = SaleCreate(
            customer_id=None,
            payment_method="card",
            discount_amount=Decimal("0.00"),
            items=[
                SaleItemCreate(
                    product_id=1,
                    quantity=1,
                    unit_price=Decimal("100.00"),
                    discount=Decimal("0.00"),
                    tax_amount=Decimal("5.00"),
                    subtotal=Decimal("105.00")
                )
            ]
        )
        
        sale, error = sales_service.create_sale(test_db, sale_data, user_id=1)
        
        assert error is None, f"Should not have error. Got: {error}"
        assert sale.customer_id is None, "Walk-in customer should have null customer_id"
        
    def test_create_sale_out_of_stock_error(self, test_db: Session, sample_products, sample_customers, sample_user):
        
        sale_data = SaleCreate(
            customer_id=1,
            payment_method="cash",
            discount_amount=Decimal("0.00"),
            items=[
                SaleItemCreate(
                    product_id=3,
                    quantity=100,
                    unit_price=Decimal("60.00"),
                    discount=Decimal("0.00"),
                    tax_amount=Decimal("300.00"),
                    subtotal=Decimal("6300.00")
                )
            ]
        )
        
        sale, error = sales_service.create_sale(test_db, sale_data, user_id=1)
        
        # ASSERTIONS
        assert sale is None, "Sale should not be created"
        assert error is not None, "Should have error message"
        assert "Insufficient stock" in error, f"Error should mention stock. Got: {error}"
        assert "Double Toned Milk" in error, "Error should mention product name"
        
        # Check stock was NOT changed
        product3_stock = test_db.query(Product).filter(Product.product_id == 3).first().stock_quantity
        assert product3_stock == 5, f"Stock should remain 5, got {product3_stock}"
        
    def test_create_sale_invalid_payment_method(self, test_db: Session, sample_products, sample_customers, sample_user):
        
        try:
            sale_data = SaleCreate(
                customer_id=1,
                payment_method="cheque",  # Invalid!
                discount_amount=Decimal("0.00"),
                items=[
                    SaleItemCreate(
                        product_id=1,
                        quantity=1,
                        unit_price=Decimal("100.00"),
                        discount=Decimal("0.00"),
                        tax_amount=Decimal("5.00"),
                        subtotal=Decimal("105.00")
                    )
                ]
            )
            assert False, "Should have raised validation error"
        except ValidationError:
            pass  # Expected - Pydantic v2 raises ValidationError for invalid enum
            
    def test_create_sale_credit_payment(self, test_db: Session, sample_products, sample_customers, sample_user):
        
        # Get initial credit
        customer = test_db.query(Customer).filter(Customer.customer_id == 2).first()
        initial_credit = customer.credit_balance
        
        sale_data = SaleCreate(
            customer_id=2,
            payment_method="credit",
            discount_amount=Decimal("0.00"),
            items=[
                SaleItemCreate(
                    product_id=1,
                    quantity=2,
                    unit_price=Decimal("100.00"),
                    discount=Decimal("0.00"),
                    tax_amount=Decimal("10.00"),
                    subtotal=Decimal("210.00")
                )
            ]
        )
        
        sale, error = sales_service.create_sale(test_db, sale_data, user_id=1)
        
        assert error is None, f"Should not have error. Got: {error}"
        assert sale.status == "pending", "Credit sale should be 'pending', not 'paid'"
        
        # Check customer credit was updated
        customer_updated = test_db.query(Customer).filter(Customer.customer_id == 2).first()
        assert customer_updated.credit_balance > initial_credit, "Credit should be added for credit payment"


# =========================
# SALE RETRIEVAL TESTS
# =========================

class TestGetSaleDetails:
    
    def test_get_sale_by_id_success(self, test_db: Session, sample_products, sample_customers, sample_user):
        # Create a sale first
        sale_data = SaleCreate(
            customer_id=1,
            payment_method="cash",
            discount_amount=Decimal("10.00"),
            items=[
                SaleItemCreate(
                    product_id=1,
                    quantity=2,
                    unit_price=Decimal("100.00"),
                    discount=Decimal("0.00"),
                    tax_amount=Decimal("10.00"),
                    subtotal=Decimal("210.00")
                )
            ]
        )
        sale_created, _ = sales_service.create_sale(test_db, sale_data, user_id=1)
        bill_id = sale_created.bill_id
        
        # Now retrieve it
        sale = sales_service.get_sale_by_id(test_db, bill_id)
        
        # ASSERTIONS
        assert sale is not None, "Sale should be found"
        assert sale.bill_id == bill_id
        assert sale.customer_id == 1
        assert len(sale.items) == 1, "Should have 1 item"
        assert len(sale.transactions) >= 1, "Should have at least 1 transaction"
        assert sale.receipt_number is not None
        
    def test_get_sale_not_found(self, test_db: Session):
    
        sale = sales_service.get_sale_by_id(test_db, 9999)
        
        assert sale is None, "Should return None for non-existent sale"


# =========================
# SALES HISTORY TESTS
# =========================

class TestSalesHistory:
    
    def test_get_sales_history_all(self, test_db: Session, sample_products, sample_customers, sample_user):
        # Create multiple sales
        for i in range(3):
            sale_data = SaleCreate(
                customer_id=1 if i % 2 == 0 else 2,
                payment_method="cash" if i % 2 == 0 else "card",
                discount_amount=Decimal("0.00"),
                items=[
                    SaleItemCreate(
                        product_id=1,
                        quantity=1,
                        unit_price=Decimal("100.00"),
                        discount=Decimal("0.00"),
                        tax_amount=Decimal("5.00"),
                        subtotal=Decimal("105.00")
                    )
                ]
            )
            sales_service.create_sale(test_db, sale_data, user_id=1)
        
        # Retrieve history
        sales, total = sales_service.get_sales_history(test_db)
        
        # ASSERTIONS
        assert total == 3, f"Should have 3 sales total, got {total}"
        assert len(sales) == 3, f"Should return 3 sales, got {len(sales)}"
        
    def test_get_sales_history_filter_by_payment_method(self, test_db: Session, sample_products, sample_customers, sample_user):
        
        # Create sales
        for i in range(3):
            sale_data = SaleCreate(
                customer_id=1,
                payment_method="cash" if i < 2 else "card",
                discount_amount=Decimal("0.00"),
                items=[
                    SaleItemCreate(
                        product_id=1,
                        quantity=1,
                        unit_price=Decimal("100.00"),
                        discount=Decimal("0.00"),
                        tax_amount=Decimal("5.00"),
                        subtotal=Decimal("105.00")
                    )
                ]
            )
            sales_service.create_sale(test_db, sale_data, user_id=1)
        
        # Filter by cash
        sales, total = sales_service.get_sales_history(test_db, payment_method="cash")
        
        assert total >= 2, f"Should have at least 2 cash sales, got {total}"
        assert all(s.payment_method == "cash" for s in sales), "All results should be cash payments"
        
    def test_get_sales_history_filter_by_customer(self, test_db: Session, sample_products, sample_customers, sample_user):
        
        # Create sales for both customers
        for customer_id in [1, 1, 2, 2]:
            sale_data = SaleCreate(
                customer_id=customer_id,
                payment_method="cash",
                discount_amount=Decimal("0.00"),
                items=[
                    SaleItemCreate(
                        product_id=1,
                        quantity=1,
                        unit_price=Decimal("100.00"),
                        discount=Decimal("0.00"),
                        tax_amount=Decimal("5.00"),
                        subtotal=Decimal("105.00")
                    )
                ]
            )
            sales_service.create_sale(test_db, sale_data, user_id=1)
        
        # Filter by customer 1
        sales, total = sales_service.get_sales_history(test_db, customer_id=1)
        
        assert len(sales) >= 2, f"Should have at least 2 sales for customer 1, got {len(sales)}"
        assert all(s.customer_id == 1 for s in sales), "All results should be for customer 1"
        
    def test_get_sales_history_pagination(self, test_db: Session, sample_products, sample_customers, sample_user):
        
        # Create 5 sales
        for i in range(5):
            sale_data = SaleCreate(
                customer_id=1,
                payment_method="cash",
                discount_amount=Decimal("0.00"),
                items=[
                    SaleItemCreate(
                        product_id=1,
                        quantity=1,
                        unit_price=Decimal("100.00"),
                        discount=Decimal("0.00"),
                        tax_amount=Decimal("5.00"),
                        subtotal=Decimal("105.00")
                    )
                ]
            )
            sales_service.create_sale(test_db, sale_data, user_id=1)
        
        # Get first 2
        sales, total = sales_service.get_sales_history(test_db, skip=0, limit=2)
        
        assert len(sales) == 2, f"Should return 2 results per page, got {len(sales)}"
        assert total == 5, f"Total should be 5, got {total}"


# =========================
# DAILY SUMMARY TESTS
# =========================

class TestDailySummary:
    
    def test_get_daily_summary_success(self, test_db: Session, sample_products, sample_customers, sample_user):
    
        # Create 2 sales
        for i in range(2):
            sale_data = SaleCreate(
                customer_id=1,
                payment_method="cash" if i == 0 else "card",
                discount_amount=Decimal("0.00"),
                items=[
                    SaleItemCreate(
                        product_id=1,
                        quantity=1,
                        unit_price=Decimal("100.00"),
                        discount=Decimal("0.00"),
                        tax_amount=Decimal("5.00"),
                        subtotal=Decimal("105.00")
                    )
                ]
            )
            sales_service.create_sale(test_db, sale_data, user_id=1)
        
        # Get summary for today
        summary = sales_service.get_daily_summary(test_db, date.today())
        
        # ASSERTIONS
        assert summary is not None, "Should return summary"
        assert summary["transaction_count"] >= 2, f"Should have at least 2 transactions, got {summary['transaction_count']}"
        assert summary["total_sales"] > 0, "Total sales should be positive"
        assert summary["total_tax"] > 0, "Total tax should be calculated"
        assert "payment_breakdown" in summary, "Should include payment breakdown"
        assert isinstance(summary["payment_breakdown"], dict), "Payment breakdown should be a dict"


# =========================
# SALE REVERSAL TESTS
# =========================

class TestSaleReversal:
    
    def test_reverse_sale_success(self, test_db: Session, sample_products, sample_customers, sample_user):
        
        # Create a sale
        sale_data = SaleCreate(
            customer_id=1,
            payment_method="cash",
            discount_amount=Decimal("0.00"),
            items=[
                SaleItemCreate(
                    product_id=1,
                    quantity=2,
                    unit_price=Decimal("100.00"),
                    discount=Decimal("0.00"),
                    tax_amount=Decimal("10.00"),
                    subtotal=Decimal("210.00")
                )
            ]
        )
        sale_created, _ = sales_service.create_sale(test_db, sale_data, user_id=1)
        bill_id = sale_created.bill_id
        
        # Check stock was decremented
        product_before = test_db.query(Product).filter(Product.product_id == 1).first()
        assert product_before.stock_quantity == 48, "Stock should be 48 after sale"
        
        # Reverse the sale
        success, error = sales_service.reverse_sale(test_db, bill_id)
        
        # ASSERTIONS
        assert success is True, f"Reversal should succeed. Error: {error}"
        assert error is None, f"Should not have error. Got: {error}"
        
        # Check sale status
        sale_reversed = test_db.query(Sale).filter(Sale.bill_id == bill_id).first()
        assert sale_reversed.status == "cancelled", f"Sale status should be 'cancelled', got {sale_reversed.status}"
        
        # Check stock was restored
        product_after = test_db.query(Product).filter(Product.product_id == 1).first()
        assert product_after.stock_quantity == 50, f"Stock should be restored to 50, got {product_after.stock_quantity}"
        
    def test_reverse_sale_not_found(self, test_db: Session):
        success, error = sales_service.reverse_sale(test_db, 9999)
        
        assert success is False, "Should fail for non-existent sale"
        assert error is not None, "Should have error message"
        assert "not found" in error.lower(), f"Error should mention not found. Got: {error}"
        
    def test_reverse_sale_already_cancelled(self, test_db: Session, sample_products, sample_customers, sample_user):
        # Create and reverse once
        sale_data = SaleCreate(
            customer_id=1,
            payment_method="cash",
            discount_amount=Decimal("0.00"),
            items=[
                SaleItemCreate(
                    product_id=1,
                    quantity=1,
                    unit_price=Decimal("100.00"),
                    discount=Decimal("0.00"),
                    tax_amount=Decimal("5.00"),
                    subtotal=Decimal("105.00")
                )
            ]
        )
        sale_created, _ = sales_service.create_sale(test_db, sale_data, user_id=1)
        bill_id = sale_created.bill_id
        
        # First reversal
        success1, _ = sales_service.reverse_sale(test_db, bill_id)
        assert success1 is True, "First reversal should succeed"
        
        # Second reversal (should fail)
        success2, error = sales_service.reverse_sale(test_db, bill_id)
        
        assert success2 is False, "Second reversal should fail"
        assert "already cancelled" in error.lower(), f"Error should mention already cancelled. Got: {error}"
        
    def test_reverse_sale_credit_restoration(self, test_db: Session, sample_products, sample_customers, sample_user):
        # Get initial credit
        customer = test_db.query(Customer).filter(Customer.customer_id == 1).first()
        initial_credit = customer.credit_balance
        
        # Create credit sale
        sale_data = SaleCreate(
            customer_id=1,
            payment_method="credit",
            discount_amount=Decimal("0.00"),
            items=[
                SaleItemCreate(
                    product_id=1,
                    quantity=2,
                    unit_price=Decimal("100.00"),
                    discount=Decimal("0.00"),
                    tax_amount=Decimal("10.00"),
                    subtotal=Decimal("210.00")
                )
            ]
        )
        sale_created, _ = sales_service.create_sale(test_db, sale_data, user_id=1)
        bill_id = sale_created.bill_id
        
        # Credit should be updated
        customer_after_sale = test_db.query(Customer).filter(Customer.customer_id == 1).first()
        assert customer_after_sale.credit_balance > initial_credit, "Credit should increase for credit sale"
        credit_after_sale = customer_after_sale.credit_balance
        
        # Reverse
        success, error = sales_service.reverse_sale(test_db, bill_id)
        
        assert success is True, f"Reversal should succeed. Error: {error}"
        
        # Credit should be restored
        customer_after_reversal = test_db.query(Customer).filter(Customer.customer_id == 1).first()
        assert customer_after_reversal.credit_balance == initial_credit, \
            "Credit should be restored to initial value after reversal"


# =========================
# TAX CALCULATION TESTS
# =========================

class TestTaxCalculation:
    
    def test_calculate_tax_simple(self):
        tax = sales_service.calculate_tax(Decimal("100.00"))
        
        assert tax == Decimal("5.00"), f"Tax on 100 should be 5, got {tax}"
        
    def test_calculate_tax_precision(self):
       
        tax = sales_service.calculate_tax(Decimal("123.45"))
        
        # Tax should be 123.45 * 0.05 = 6.1725, rounded to 6.17
        assert tax == Decimal("6.17"), f"Tax on 123.45 should be 6.17, got {tax}"
        
    def test_calculate_item_tax(self):
       
        tax = sales_service.calculate_item_tax(
            unit_price=Decimal("100.00"),
            quantity=2,
            discount=Decimal("10.00")
        )
        
        assert tax == Decimal("9.50"), f"Tax should be 9.50, got {tax}"


# =========================
# STOCK MANAGEMENT TESTS
# =========================

class TestStockManagement:
    
    def test_decrement_stock_success(self, test_db: Session, sample_products):
        success = sales_service.decrement_stock(test_db, 1, 5)
        
        assert success is True, "Stock decrement should succeed"
        product = test_db.query(Product).filter(Product.product_id == 1).first()
        assert product.stock_quantity == 45, f"Stock should be 45, got {product.stock_quantity}"
        
    def test_decrement_stock_insufficient(self, test_db: Session, sample_products):
        success = sales_service.decrement_stock(test_db, 3, 10)
        
        assert success is False, "Stock decrement should fail"
        product = test_db.query(Product).filter(Product.product_id == 3).first()
        assert product.stock_quantity == 5, f"Stock should remain 5, got {product.stock_quantity}"
        
    def test_restore_stock(self, test_db: Session, sample_products):
        success = sales_service.restore_stock(test_db, 1, 5)
        
        assert success is True, "Stock restore should succeed"
        product = test_db.query(Product).filter(Product.product_id == 1).first()
        assert product.stock_quantity == 55, f"Stock should be 55, got {product.stock_quantity}"


# =========================
# RECEIPT NUMBER TESTS
# =========================

class TestReceiptGeneration:
    
    def test_receipt_number_format(self, test_db: Session):
        receipt = sales_service.generate_receipt_number(test_db)
        
        assert receipt.startswith("RCP-"), f"Receipt should start with 'RCP-', got {receipt}"
        parts = receipt.split("-")
        assert len(parts) == 3, f"Receipt should have 3 parts, got {len(parts)}"
        assert len(parts[1]) == 8, f"Date part should be 8 chars (YYYYMMDD), got {len(parts[1])}"
        assert len(parts[2]) == 6, f"Random part should be 6 chars, got {len(parts[2])}"
        
    def test_receipt_number_uniqueness(self, test_db: Session):
        receipts = [sales_service.generate_receipt_number(test_db) for _ in range(10)]
        
        unique_receipts = set(receipts)
        assert len(unique_receipts) == 10, f"All receipts should be unique. Got duplicates: {len(receipts) - len(unique_receipts)}"


# =========================
# INTEGRATION TESTS
# =========================

class TestIntegration:
    
    def test_complete_sale_workflow(self, test_db: Session, sample_products, sample_customers, sample_user):

        # 1. Create sale
        sale_data = SaleCreate(
            customer_id=1,
            payment_method="cash",
            discount_amount=Decimal("20.00"),
            items=[
                SaleItemCreate(
                    product_id=1,
                    quantity=2,
                    unit_price=Decimal("100.00"),
                    discount=Decimal("0.00"),
                    tax_amount=Decimal("10.00"),
                    subtotal=Decimal("210.00")
                ),
                SaleItemCreate(
                    product_id=2,
                    quantity=1,
                    unit_price=Decimal("80.00"),
                    discount=Decimal("0.00"),
                    tax_amount=Decimal("4.00"),
                    subtotal=Decimal("84.00")
                )
            ]
        )
        
        sale_created, error = sales_service.create_sale(test_db, sale_data, user_id=1)
        assert error is None, f"Sale creation failed: {error}"
        
        bill_id = sale_created.bill_id
        receipt = sale_created.receipt_number
        total = sale_created.total_amount
        
        # 2. Retrieve details
        sale_details = sales_service.get_sale_by_id(test_db, bill_id)
        assert sale_details is not None
        assert sale_details.receipt_number == receipt
        assert sale_details.total_amount == total
        assert len(sale_details.items) == 2
        
        # 3. Get history
        sales_list, count = sales_service.get_sales_history(test_db)
        assert count >= 1, "History should include created sale"
        assert any(s.bill_id == bill_id for s in sales_list), "Created sale should be in history"
        
        # 4. Daily summary
        summary = sales_service.get_daily_summary(test_db, date.today())
        assert summary["transaction_count"] >= 1
        assert summary["total_sales"] > 0
