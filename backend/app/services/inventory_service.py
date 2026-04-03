"""
All service methods called by inventory.py routes.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from typing import Optional, Tuple, List

from app.models.sale import Product
from app.models.inventory import StockMovement, DamageLossRecord
from app.models.user import Category


# =========================
# HELPERS
# =========================

def calculate_profit_margin(price: float, cost: float) -> float:
    """Return gross profit margin as a percentage, or 0 if not computable."""
    if price and cost and price > 0:
        return round((price - cost) / price * 100, 2)
    return 0.0


def calculate_inventory_value(db: Session) -> float:
    """Total cost value of all active stock."""
    result = db.query(func.sum(Product.cost * Product.stock)).filter(
        Product.status == "active"
    ).scalar()
    return round(float(result or 0), 2)


# =========================
# PRODUCT CRUD
# =========================

def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.product_id == product_id).first()


def get_product_by_barcode(db: Session, barcode: str) -> Optional[Product]:
    return db.query(Product).filter(
        Product.barcode == barcode,
        Product.status == "active"
    ).first()


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
        cat = db.query(Category).filter(Category.category_name == category).first()
        if cat:
            query = query.filter(Product.category_id == cat.category_id)

    if search:
        query = query.filter(
            Product.name.ilike(f"%{search}%") |
            Product.sku.ilike(f"%{search}%") |
            Product.barcode.ilike(f"%{search}%")
        )

    total = query.count()
    products = query.offset(skip).limit(limit).all()
    return products, total


def create_product(db: Session, product_data) -> Tuple[Optional[Product], Optional[str]]:
    category = db.query(Category).filter(
        Category.category_name == product_data.category
    ).first()
    if not category:
        return None, f"Category '{product_data.category}' not found"

    if db.query(Product).filter(Product.sku == product_data.sku).first():
        return None, "SKU already exists"

    if product_data.barcode and db.query(Product).filter(
        Product.barcode == product_data.barcode
    ).first():
        return None, "Barcode already exists"

    product = Product(
        name=product_data.name,
        category_id=category.category_id,
        sku=product_data.sku,
        barcode=getattr(product_data, "barcode", None),
        unit=product_data.unit,
        price=product_data.price,
        cost=product_data.cost,
        stock=getattr(product_data, "stock", 0),
        reorder_level=getattr(product_data, "reorder_level", 10),
        max_stock=getattr(product_data, "max_stock", 1000),
        supplier_id=getattr(product_data, "supplier_id", None),
        expiry_date=getattr(product_data, "expiry_date", None),
        manufactured_date=getattr(product_data, "manufactured_date", None),
        status=getattr(product_data, "status", "active")
    )

    db.add(product)
    db.commit()
    db.refresh(product)
    return product, None


def update_product(db: Session, product_id: int, product_data) -> Tuple[Optional[Product], Optional[str]]:
    from app.models.user import Category

    product = get_product_by_id(db, product_id)
    if not product:
        return None, "Product not found"

    if hasattr(product_data, "category") and product_data.category:
        category = db.query(Category).filter(
            Category.category_name == product_data.category
        ).first()
        if not category:
            return None, f"Category '{product_data.category}' not found"
        product.category_id = category.category_id

    # Apply all provided fields
    for field in ("name", "sku", "barcode", "unit", "price", "cost",
                  "reorder_level", "max_stock", "supplier_id",
                  "expiry_date", "manufactured_date", "status"):
        if hasattr(product_data, field) and getattr(product_data, field) is not None:
            setattr(product, field, getattr(product_data, field))

    db.commit()
    db.refresh(product)
    return product, None


def delete_product(db: Session, product_id: int) -> Tuple[bool, Optional[str]]:
    """Soft delete — marks product as discontinued."""
    product = get_product_by_id(db, product_id)
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
    notes: Optional[str],
    created_by: int
) -> Tuple[bool, Optional[str]]:
    product = get_product_by_id(db, product_id)
    if not product:
        return False, "Product not found"

    new_stock = product.stock + quantity_change
    if new_stock < 0:
        return False, f"Stock cannot go below 0. Current: {product.stock}, Change: {quantity_change}"

    product.stock = new_stock

    movement = StockMovement(
        product_id=product_id,
        quantity_change=quantity_change,
        movement_type=movement_type,
        notes=notes,
        created_by=created_by
    )
    db.add(movement)
    db.commit()
    return True, None


def get_stock_movements_for_product(
    db: Session,
    product_id: int,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[StockMovement], int]:
    query = db.query(StockMovement).filter(
        StockMovement.product_id == product_id
    ).order_by(StockMovement.created_at.desc())

    total = query.count()
    movements = query.offset(skip).limit(limit).all()
    return movements, total


# =========================
# ALERTS
# =========================

def get_low_stock_products(db: Session) -> List[dict]:
    products = db.query(Product).filter(
        Product.status == "active",
        Product.stock < Product.reorder_level
    ).all()

    return [
        {
            "product_id": p.product_id,
            "name": p.name,
            "sku": p.sku,
            "current_stock": p.stock,
            "reorder_level": p.reorder_level,
            "units_needed": p.reorder_level - p.stock
        }
        for p in products
    ]


def get_expiring_soon_products(db: Session, days: int = 30) -> List[dict]:
    today = date.today()
    threshold = today + timedelta(days=days)

    products = db.query(Product).filter(
        Product.status == "active",
        Product.expiry_date != None,
        Product.expiry_date >= today,
        Product.expiry_date <= threshold
    ).order_by(Product.expiry_date.asc()).all()

    return [
        {
            "product_id": p.product_id,
            "name": p.name,
            "sku": p.sku,
            "expiry_date": str(p.expiry_date),
            "days_until_expiry": (p.expiry_date - today).days,
            "current_stock": p.stock
        }
        for p in products
    ]


# =========================
# DAMAGE & LOSS
# =========================

def log_damage_loss(
    db: Session,
    damage_data,
    reported_by: int
) -> Tuple[Optional[DamageLossRecord], Optional[str]]:
    product = get_product_by_id(db, damage_data.product_id)
    if not product:
        return None, "Product not found"

    if product.stock < damage_data.quantity:
        return None, f"Cannot record loss of {damage_data.quantity} — only {product.stock} in stock"

    product.stock -= damage_data.quantity

    record = DamageLossRecord(
        product_id=damage_data.product_id,
        quantity=damage_data.quantity,
        reason=damage_data.reason,
        estimated_loss=damage_data.quantity * product.cost,
        reported_by=reported_by
    )

    # Also record a negative stock movement for audit trail
    movement = StockMovement(
        product_id=damage_data.product_id,
        quantity_change=-damage_data.quantity,
        movement_type="damage_loss",
        notes=damage_data.reason,
        created_by=reported_by
    )

    db.add(record)
    db.add(movement)
    db.commit()
    db.refresh(record)
    return record, None


def get_damage_loss_report(
    db: Session,
    start_date=None,
    end_date=None,
    reason: Optional[str] = None
) -> dict:
    query = db.query(DamageLossRecord)

    if start_date:
        query = query.filter(DamageLossRecord.created_at >= start_date)
    if end_date:
        query = query.filter(DamageLossRecord.created_at <= end_date)
    if reason:
        query = query.filter(DamageLossRecord.reason.ilike(f"%{reason}%"))

    records = query.order_by(DamageLossRecord.created_at.desc()).all()

    total_quantity = sum(r.quantity for r in records)
    total_loss_value = sum(r.estimated_loss for r in records)

    return {
        "records": [
            {
                "record_id": r.id,
                "product_id": r.product_id,
                "quantity": r.quantity,
                "reason": r.reason,
                "estimated_loss": r.estimated_loss,
                "reported_by": r.reported_by,
                "created_at": str(r.created_at)
            }
            for r in records
        ],
        "summary": {
            "total_records": len(records),
            "total_quantity_lost": total_quantity,
            "total_estimated_loss_value": round(float(total_loss_value), 2)
        }
    }