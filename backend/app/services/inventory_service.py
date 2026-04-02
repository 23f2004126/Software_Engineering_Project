from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Tuple, Optional, Dict

from app.models.inventory import Product, StockMovement, DamageLossRecord
from app.schemas.inventory import ProductCreate, ProductUpdate, DamageLossCreate


# =========================
# PRODUCT MANAGEMENT
# =========================

def create_product(db: Session, product_data: ProductCreate) -> Tuple[Optional[Product], Optional[str]]:
    existing_sku = db.query(Product).filter(Product.sku == product_data.sku).first()
    if existing_sku:
        return None, f"SKU '{product_data.sku}' already exists"

    # Check barcode uniqueness
    existing_barcode = db.query(Product).filter(Product.barcode == product_data.barcode).first()
    if existing_barcode:
        return None, f"Barcode '{product_data.barcode}' already exists"

    # Validate cost < price
    if product_data.cost >= product_data.price:
        return None, "Cost price must be less than selling price"

    # Validate reorder_level < max_stock
    if product_data.reorder_level >= product_data.max_stock:
        return None, "Reorder level must be less than max stock"

    # Create product
    product = Product(
        name=product_data.name,
        category=product_data.category,
        sku=product_data.sku,
        barcode=product_data.barcode,
        price=product_data.price,
        cost=product_data.cost,
        stock=product_data.stock,
        reorder_level=product_data.reorder_level,
        max_stock=product_data.max_stock,
        unit=product_data.unit,
        supplier_id=product_data.supplier_id,
        expiry_date=product_data.expiry_date,
        manufactured_date=product_data.manufactured_date,
        status=product_data.status
    )

    db.add(product)
    db.commit()
    db.refresh(product)
    return product, None


def get_products_paginated(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    status: Optional[str] = "active",
    search: Optional[str] = None
) -> Tuple[List[Product], int]:
    query = db.query(Product)

    if status:
        query = query.filter(Product.status == status)
    if category:
        query = query.filter(Product.category == category)
    if search:
        query = query.filter(
            (Product.name.ilike(f"%{search}%")) |
            (Product.sku.ilike(f"%{search}%")) |
            (Product.barcode.ilike(f"%{search}%"))
        )

    total_count = query.count()
    products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()

    return products, total_count


def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.product_id == product_id).first()


def get_product_by_barcode(db: Session, barcode: str) -> Optional[Product]:
    return db.query(Product).filter(Product.barcode == barcode).first()


def update_product(db: Session, product_id: int, product_data: ProductUpdate) -> Tuple[Optional[Product], Optional[str]]:
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        return None, "Product not found"

    # Validate cost < price if both are being updated
    cost = product_data.cost or product.cost
    price = product_data.price or product.price
    if cost >= price:
        return None, "Cost price must be less than selling price"

    # Update fields
    if product_data.name is not None:
        product.name = product_data.name
    if product_data.category is not None:
        product.category = product_data.category
    if product_data.price is not None:
        product.price = product_data.price
    if product_data.cost is not None:
        product.cost = product_data.cost
    if product_data.reorder_level is not None:
        product.reorder_level = product_data.reorder_level
    if product_data.max_stock is not None:
        product.max_stock = product_data.max_stock
    if product_data.unit is not None:
        product.unit = product_data.unit
    if product_data.supplier_id is not None:
        product.supplier_id = product_data.supplier_id
    if product_data.expiry_date is not None:
        product.expiry_date = product_data.expiry_date
    if product_data.manufactured_date is not None:
        product.manufactured_date = product_data.manufactured_date
    if product_data.status is not None:
        product.status = product_data.status

    db.commit()
    db.refresh(product)
    return product, None


def delete_product(db: Session, product_id: int) -> Tuple[bool, Optional[str]]:
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        return False, "Product not found"

    product.status = "discontinued"
    db.commit()
    return True, None


# =========================
# STOCK MANAGEMENT
# =========================

def adjust_stock(
    db: Session,
    product_id: int,
    quantity_change: int,
    movement_type: str,
    reference_id: Optional[str] = None,
    notes: Optional[str] = None,
    created_by: Optional[int] = None
) -> Tuple[bool, Optional[str]]:
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        return False, "Product not found"

    # Calculate new stock
    previous_stock = product.stock
    new_stock = previous_stock + quantity_change

    # Validate stock never goes negative
    if new_stock < 0:
        return False, f"Insufficient stock. Current: {previous_stock}, Requested decrease: {abs(quantity_change)}"

    # Update stock
    product.stock = new_stock
    db.add(product)
    db.flush()

    # Create stock movement record
    movement = StockMovement(
        product_id=product_id,
        movement_type=movement_type,
        quantity=quantity_change,
        previous_stock=previous_stock,
        new_stock=new_stock,
        reference_id=reference_id,
        notes=notes,
        created_by=created_by,
        created_at=datetime.utcnow()
    )
    db.add(movement)
    db.commit()

    return True, None


def create_stock_movement(
    db: Session,
    product_id: int,
    movement_type: str,
    quantity: int,
    reference_id: Optional[str] = None,
    notes: Optional[str] = None,
    created_by: Optional[int] = None
) -> Optional[StockMovement]:
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        return None

    movement = StockMovement(
        product_id=product_id,
        movement_type=movement_type,
        quantity=quantity,
        previous_stock=product.stock,
        new_stock=product.stock + quantity,
        reference_id=reference_id,
        notes=notes,
        created_by=created_by
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement


def get_stock_movements_for_product(
    db: Session,
    product_id: int,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[StockMovement], int]:
    query = db.query(StockMovement).filter(StockMovement.product_id == product_id)
    total_count = query.count()
    movements = query.order_by(StockMovement.created_at.desc()).offset(skip).limit(limit).all()
    return movements, total_count


# =========================
# CALCULATIONS
# =========================

def calculate_profit_margin(price: Decimal, cost: Decimal) -> float:
    if price == 0:
        return 0.0
    return float(((price - cost) / price) * 100)


def calculate_inventory_value(db: Session) -> Decimal:
    result = db.query(
        func.sum(Product.stock * Product.cost)
    ).filter(Product.status == "active").scalar()

    return Decimal(str(result or 0))


def calculate_inventory_turnover(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Optional[float]:
    query = db.query(func.sum(StockMovement.quantity)).filter(
        StockMovement.movement_type == "sale"
    )

    if start_date:
        query = query.filter(StockMovement.created_at >= start_date)
    if end_date:
        query = query.filter(StockMovement.created_at <= end_date)

    total_sales = query.scalar() or 0
    avg_inventory = calculate_inventory_value(db)

    if avg_inventory == 0:
        return None

    return float(total_sales) / float(avg_inventory)


# =========================
# ALERTS & REPORTS
# =========================

def get_low_stock_products(db: Session) -> List[Dict]:
    products = db.query(Product).filter(
        Product.stock < Product.reorder_level,
        Product.status == "active"
    ).all()

    low_stock = []
    for product in products:
        low_stock.append({
            "product_id": product.product_id,
            "name": product.name,
            "sku": product.sku,
            "current_stock": product.stock,
            "reorder_level": product.reorder_level,
            "shortage": product.reorder_level - product.stock
        })

    return low_stock


def get_expiring_soon_products(db: Session, days: int = 30) -> List[Dict]:
    expiry_threshold = date.today() + timedelta(days=days)

    products = db.query(Product).filter(
        Product.expiry_date <= expiry_threshold,
        Product.expiry_date >= date.today(),
        Product.status == "active"
    ).all()

    expiring = []
    for product in products:
        if product.expiry_date:
            days_remaining = (product.expiry_date - date.today()).days
            expiring.append({
                "product_id": product.product_id,
                "name": product.name,
                "sku": product.sku,
                "expiry_date": product.expiry_date,
                "days_until_expiry": days_remaining,
                "stock": product.stock
            })

    return expiring


# =========================
# DAMAGE & LOSS TRACKING
# =========================

def log_damage_loss(
    db: Session,
    damage_data: DamageLossCreate,
    reported_by: int
) -> Tuple[Optional[DamageLossRecord], Optional[str]]:
    product = db.query(Product).filter(Product.product_id == damage_data.product_id).first()
    if not product:
        return None, "Product not found"

    # Calculate cost impact
    damage_cost = Decimal(str(product.cost)) * Decimal(str(damage_data.quantity))

    # Create damage/loss record
    record = DamageLossRecord(
        product_id=damage_data.product_id,
        quantity=damage_data.quantity,
        reason=damage_data.reason,
        cost=damage_cost,
        notes=damage_data.notes,
        reported_by=reported_by
    )
    db.add(record)
    db.flush()

    # Reduce stock
    success, error = adjust_stock(
        db,
        product_id=damage_data.product_id,
        quantity_change=-damage_data.quantity,
        movement_type="loss",
        reference_id=f"DAMAGE-{record.record_id}",
        notes=f"{damage_data.reason}: {damage_data.notes}",
        created_by=reported_by
    )

    if not success:
        db.rollback()
        return None, error

    db.commit()
    db.refresh(record)
    return record, None


def get_damage_loss_report(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    reason: Optional[str] = None
) -> Dict:
    query = db.query(DamageLossRecord)

    if start_date:
        query = query.filter(DamageLossRecord.reported_at >= start_date)
    if end_date:
        query = query.filter(DamageLossRecord.reported_at <= end_date)
    if reason:
        query = query.filter(DamageLossRecord.reason == reason)

    records = query.all()

    # Calculate totals
    total_loss_count = len(records)
    total_financial_loss = Decimal("0")
    by_reason = {}
    by_product = {}

    for record in records:
        total_financial_loss += record.cost

        # By reason
        if record.reason not in by_reason:
            by_reason[record.reason] = {"count": 0, "loss": Decimal("0")}
        by_reason[record.reason]["count"] += 1
        by_reason[record.reason]["loss"] += record.cost

        # By product
        if record.product_id not in by_product:
            product = record.product
            by_product[record.product_id] = {
                "product_id": record.product_id,
                "name": product.name if product else "Unknown",
                "count": 0,
                "loss": Decimal("0")
            }
        by_product[record.product_id]["count"] += 1
        by_product[record.product_id]["loss"] += record.cost

    return {
        "total_loss_count": total_loss_count,
        "total_financial_loss": str(total_financial_loss),
        "by_reason": {k: {"count": v["count"], "loss": str(v["loss"])} for k, v in by_reason.items()},
        "by_product": list(by_product.values())
    }


# =========================
# STATISTICS & ANALYTICS
# =========================

def get_inventory_statistics(db: Session) -> Dict:
    total_products = db.query(func.count(Product.product_id)).filter(Product.status == "active").scalar() or 0
    total_stock_units = db.query(func.sum(Product.stock)).filter(Product.status == "active").scalar() or 0
    total_inventory_value = calculate_inventory_value(db)

    low_stock_count = db.query(func.count(Product.product_id)).filter(
        Product.stock < Product.reorder_level,
        Product.status == "active"
    ).scalar() or 0

    expiring_count = db.query(func.count(Product.product_id)).filter(
        Product.expiry_date <= date.today() + timedelta(days=30),
        Product.expiry_date >= date.today(),
        Product.status == "active"
    ).scalar() or 0

    return {
        "total_products": total_products,
        "total_stock_units": total_stock_units,
        "total_inventory_value": str(total_inventory_value),
        "low_stock_count": low_stock_count,
        "expiring_soon_count": expiring_count
    }
