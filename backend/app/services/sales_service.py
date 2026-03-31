from sqlalchemy.orm import Session
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Optional
import random
import string

from app.models.sale import Sale, SaleItem, Transaction, Product, Customer
from app.schemas.sale import SaleCreate, SaleItemCreate, TransactionCreate

# Tax rate (5%)
TAX_RATE = Decimal("0.05")


# =========================
# RECEIPT NUMBER GENERATION
# =========================
def generate_receipt_number(db: Session) -> str:
    today = datetime.utcnow().strftime("%Y%m%d")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    receipt_number = f"RCP-{today}-{random_suffix}"
    
    # Ensure uniqueness
    while db.query(Sale).filter(Sale.receipt_number == receipt_number).first():
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        receipt_number = f"RCP-{today}-{random_suffix}"
    
    return receipt_number


# =========================
# TAX CALCULATION
# =========================
def calculate_tax(amount: Decimal) -> Decimal:
    
    return (amount * TAX_RATE).quantize(Decimal("0.01"))


def calculate_item_tax(unit_price: Decimal, quantity: int, discount: Decimal = Decimal("0")) -> Decimal:
    
    subtotal = unit_price * Decimal(str(quantity))
    taxable_amount = subtotal - discount
    return (taxable_amount * TAX_RATE).quantize(Decimal("0.01"))


# =========================
# STOCK MANAGEMENT
# =========================
def decrement_stock(db: Session, product_id: int, quantity: int) -> bool:
    
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        return False
    
    if product.stock_quantity < quantity:
        return False  # Insufficient stock
    
    product.stock_quantity -= quantity
    db.commit()
    return True


def restore_stock(db: Session, product_id: int, quantity: int) -> bool:
    
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        return False
    
    product.stock_quantity += quantity
    db.commit()
    return True


def check_stock_availability(db: Session, items: List[SaleItemCreate]) -> tuple[bool, Optional[str]]:
    
    for item in items:
        product = db.query(Product).filter(Product.product_id == item.product_id).first()
        if not product:
            return False, f"Product ID {item.product_id} not found"
        if product.stock_quantity < item.quantity:
            return False, f"Insufficient stock for {product.name}. Available: {product.stock_quantity}, Requested: {item.quantity}"
    return True, None


# =========================
# CREDIT MANAGEMENT
# =========================
def deduct_credit(db: Session, customer_id: int, amount: Decimal) -> bool:
    
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        return False
    
    if customer.credit_balance < amount:
        return False  # Insufficient credit
    
    customer.credit_balance -= amount
    db.commit()
    return True


def restore_credit(db: Session, customer_id: int, amount: Decimal) -> bool:
    
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        return False
    
    customer.credit_balance -= amount
    db.commit()
    return True


def add_credit(db: Session, customer_id: int, amount: Decimal) -> bool:
    
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        return False
    
    customer.credit_balance += amount
    db.commit()
    return True


# =========================
# SALE CREATION
# =========================
def create_sale(
    db: Session,
    sale_data: SaleCreate,
    user_id: int
) -> tuple[Optional[Sale], Optional[str]]:
    
    # Validate stock availability
    is_available, error_msg = check_stock_availability(db, sale_data.items)
    if not is_available:
        return None, error_msg
    
    # Calculate totals
    total_amount = Decimal("0")
    total_tax = Decimal("0")
    
    # For validation, calculate subtotals
    for item in sale_data.items:
        item_subtotal = item.subtotal
        item_tax = calculate_item_tax(item.unit_price, item.quantity, item.discount)
        total_amount += item_subtotal
        total_tax += item_tax
    
    # Apply discount
    total_amount = (total_amount - sale_data.discount_amount).quantize(Decimal("0.01"))
    
    # Create sale
    sale = Sale(
        customer_id=sale_data.customer_id,
        user_id=user_id,
        bill_date=datetime.utcnow(),
        total_amount=total_amount,
        discount_amount=sale_data.discount_amount,
        tax_amount=total_tax,
        payment_method=sale_data.payment_method,
        status="pending" if sale_data.payment_method == "credit" else "paid",
        receipt_number=generate_receipt_number(db)
    )
    
    db.add(sale)
    db.flush()  # Flush to get the bill_id
    
    # Add sale items
    for item in sale_data.items:
        sale_item = SaleItem(
            bill_id=sale.bill_id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            discount=item.discount,
            tax_amount=calculate_item_tax(item.unit_price, item.quantity, item.discount),
            subtotal=item.subtotal
        )
        db.add(sale_item)
        
        # Decrement stock
        if not decrement_stock(db, item.product_id, item.quantity):
            db.rollback()
            return None, f"Failed to decrement stock for product {item.product_id}"
    
    # Handle credit payment
    if sale_data.payment_method == "credit" and sale_data.customer_id:
        if not add_credit(db, sale_data.customer_id, total_amount):
            db.rollback()
            return None, "Failed to add credit to customer"
    
    # Add transaction
    transaction = Transaction(
        bill_id=sale.bill_id,
        amount=total_amount,
        payment_mode=sale_data.payment_method,
        reference_no=None  # Can be set later if needed
    )
    db.add(transaction)
    
    db.commit()
    return sale, None


# =========================
# SALE REVERSAL
# =========================
def reverse_sale(db: Session, bill_id: int) -> tuple[bool, Optional[str]]:

    sale = db.query(Sale).filter(Sale.bill_id == bill_id).first()
    if not sale:
        return False, "Sale not found"
    
    if sale.status == "cancelled":
        return False, "Sale is already cancelled"
    
    # Restore stock for all items
    for item in sale.items:
        if not restore_stock(db, item.product_id, item.quantity):
            db.rollback()
            return False, f"Failed to restore stock for product {item.product_id}"
    
    # Handle credit reversal
    if sale.payment_method == "credit" and sale.customer_id:
        if not restore_credit(db, sale.customer_id, sale.total_amount):
            db.rollback()
            return False, "Failed to restore credit to customer"
    
    # Mark sale as cancelled
    sale.status = "cancelled"
    db.commit()
    
    return True, None


# =========================
# SALE RETRIEVAL
# =========================
def get_sale_by_id(db: Session, bill_id: int) -> Optional[Sale]:
    
    return db.query(Sale).filter(Sale.bill_id == bill_id).first()


def get_sales_history(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    payment_method: Optional[str] = None,
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> tuple[List[Sale], int]:
    query = db.query(Sale)
    
    if start_date:
        query = query.filter(Sale.bill_date >= start_date)
    if end_date:
        query = query.filter(Sale.bill_date <= end_date)
    if payment_method:
        query = query.filter(Sale.payment_method == payment_method)
    if status:
        query = query.filter(Sale.status == status)
    if customer_id:
        query = query.filter(Sale.customer_id == customer_id)
    
    total_count = query.count()
    sales = query.order_by(Sale.bill_date.desc()).offset(skip).limit(limit).all()
    
    return sales, total_count


def get_daily_summary(db: Session, summary_date: date) -> Dict:
    start = datetime.combine(summary_date, datetime.min.time())
    end = datetime.combine(summary_date, datetime.max.time())
    
    sales = db.query(Sale).filter(
        Sale.bill_date >= start,
        Sale.bill_date <= end,
        Sale.status != "cancelled"
    ).all()
    
    total_sales = Decimal("0")
    total_discount = Decimal("0")
    total_tax = Decimal("0")
    payment_breakdown = {}
    
    for sale in sales:
        total_sales += sale.total_amount
        total_discount += sale.discount_amount
        total_tax += sale.tax_amount
        
        # Payment breakdown
        if sale.payment_method not in payment_breakdown:
            payment_breakdown[sale.payment_method] = Decimal("0")
        payment_breakdown[sale.payment_method] += sale.total_amount
    
    total_revenue = total_sales + total_tax - total_discount
    
    return {
        "date": summary_date.isoformat(),
        "total_sales": total_sales,
        "total_discount": total_discount,
        "total_tax": total_tax,
        "total_revenue": total_revenue,
        "transaction_count": len(sales),
        "payment_breakdown": {k: str(v) for k, v in payment_breakdown.items()}
    }


# =========================
# PRODUCT SEARCH
# =========================
def search_products(db: Session, query: str) -> List[Product]:

    return db.query(Product).filter(
        Product.name.ilike(f"%{query}%")
    ).limit(10).all()


def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    
    return db.query(Product).filter(Product.product_id == product_id).first()
