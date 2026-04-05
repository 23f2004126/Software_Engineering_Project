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
    # Current DB schema doesn't store `cost`. Use `price` as an approximation
    # so inventory pages can still render.
    result = db.query(func.sum(Product.price * Product.stock)).scalar()
    return round(float(result or 0), 2)


# =========================
# PRODUCT CRUD
# =========================

def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.product_id == product_id).first()


def get_product_by_barcode(db: Session, barcode: str) -> Optional[Product]:
    if not hasattr(Product, "barcode"):
        return None
    return db.query(Product).filter(Product.barcode == barcode).first()


def get_products_paginated(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    status: Optional[str] = "active",
    search: Optional[str] = None
) -> Tuple[List[Product], int]:
    query = db.query(Product)

    # DB schema doesn't store product status.
    # Keep the argument for API compatibility but ignore it.

    if category:
        cat = db.query(Category).filter(Category.category_name == category).first()
        if cat:
            query = query.filter(Product.category_id == cat.category_id)

    if search:
        query = query.filter(
            Product.name.ilike(f"%{search}%") |
            Product.unit.ilike(f"%{search}%")
        )

    total = query.count()
    products = query.offset(skip).limit(limit).all()
    return products, total


def create_product(db: Session, product_data) -> Tuple[Optional[Product], Optional[str]]:
    category = None
    # Accept either `category_id` or `category` (category name) from callers.
    if getattr(product_data, "category_id", None) is not None:
        category = db.query(Category).filter(Category.category_id == product_data.category_id).first()
    elif getattr(product_data, "category", None):
        category = db.query(Category).filter(Category.category_name == product_data.category).first()

    if not category:
        return None, "Category not found"

    if db.query(Product).filter(Product.sku == product_data.sku).first():
        return None, "SKU already exists"

    if product_data.barcode and db.query(Product).filter(
        Product.barcode == product_data.barcode
    ).first():
        return None, "Barcode already exists"

    product = Product(
        name=product_data.name,
        category_id=category.category_id,
        unit=product_data.unit,
        price=product_data.price,
        stock=getattr(product_data, "stock", 0),
        supplier_id=getattr(product_data, "supplier_id", None),
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

    if getattr(product_data, "category_id", None) is not None:
        category = db.query(Category).filter(Category.category_id == product_data.category_id).first()
        if not category:
            return None, "Category not found"
        product.category_id = category.category_id
    elif getattr(product_data, "category", None):
        category = db.query(Category).filter(Category.category_name == product_data.category).first()
        if not category:
            return None, f"Category '{product_data.category}' not found"
        product.category_id = category.category_id

    # Apply all provided fields
    for field in ("name", "unit", "price", "stock", "supplier_id", "category_id"):
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

    # Current DB schema doesn't have `status`. Soft-delete by setting stock to 0.
    product.stock = 0
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
    notes: Optional[str]
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
    reorder_level_default = 10
    products = db.query(Product).filter(Product.stock < reorder_level_default).all()

    return [
        {
            "product_id": p.product_id,
            "name": p.name,
            "sku": getattr(p, "sku", None),
            "current_stock": p.stock,
            "reorder_level": reorder_level_default,
            "units_needed": reorder_level_default - p.stock,
        }
        for p in products
    ]


def get_expiring_soon_products(db: Session, days: int = 30) -> List[dict]:
    # Current DB schema doesn't include expiry dates.
    return []


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
        estimated_loss=damage_data.quantity * (product.price or 0),
        reported_by=reported_by
    )

    # Also record a negative stock movement for audit trail
    # `stock_movements.movement_type` is constrained by schema.sql enum values.
    # For losses/damage, record this as an `out` movement of the lost quantity.
    movement = StockMovement(
        product_id=damage_data.product_id,
        quantity_change=damage_data.quantity,
        movement_type="out",
        notes=damage_data.reason,
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

    # Frontend expects an array of log objects for the Damage & Loss page.
    # Example shape:
    # { date, product_name, reason, quantity, cost_price, notes }
    return [
        {
            "date": r.created_at.isoformat() if r.created_at else None,
            "product_name": r.product.name if r.product else None,
            "reason": r.reason,
            "quantity": r.quantity,
            "cost_price": r.product.price if r.product else None,
            "notes": r.notes,
        }
        for r in records
    ]


def get_inventory_statistics(db: Session) -> dict:
    """
    Minimal overview stats used by `/api/inventory/stats/overview`.
    Kept defensive because frontend may render different fields.
    """
    total_products = db.query(Product).count()
    active_products = total_products
    low_stock = db.query(Product).filter(
        Product.stock < 10,
    ).count()

    expiring_soon = 0

    return {
        "total_products": total_products,
        "active_products": active_products,
        "low_stock": low_stock,
        "expiring_soon": expiring_soon,
    }