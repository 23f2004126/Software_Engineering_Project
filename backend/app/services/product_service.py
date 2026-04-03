"""
Service layer for products.py routes.
Handles product CRUD with category resolution and computed fields.
"""

from sqlalchemy.orm import Session
from typing import Optional, Tuple, List
from datetime import date

from app.models.sale import Product
from app.models.user import Category


# =========================
# HELPERS
# =========================

def _compute_fields(product: Product) -> dict:
    """Return computed profit_margin and inventory_value for a product."""
    profit_margin = None
    if product.price and product.cost and product.price > 0:
        profit_margin = round((product.price - product.cost) / product.price * 100, 2)
    inventory_value = round((product.cost or 0) * (product.stock or 0), 2)
    return {"profit_margin": profit_margin, "inventory_value": inventory_value}


def _resolve_category(db: Session, category_name: str) -> Tuple[Optional[Category], Optional[str]]:
    cat = db.query(Category).filter(Category.category_name == category_name).first()
    if not cat:
        return None, f"Category '{category_name}' not found"
    return cat, None


# =========================
# PRODUCT QUERIES
# =========================

def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.product_id == product_id).first()


def get_product_by_barcode(db: Session, barcode: str) -> Optional[Product]:
    return db.query(Product).filter(
        Product.barcode == barcode,
        Product.status == "active",
    ).first()


def get_products(
    db: Session,
    category: Optional[str] = None,
    status: Optional[str] = "active",
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Product]:
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
    return query.offset(skip).limit(limit).all()


def search_products_live(db: Session, q: str, limit: int = 20) -> List[Product]:
    """Fast POS product search by name, SKU, or barcode."""
    return db.query(Product).filter(
        Product.status == "active",
        (
            Product.name.ilike(f"%{q}%") |
            Product.sku.ilike(f"%{q}%") |
            Product.barcode.ilike(f"%{q}%")
        )
    ).limit(limit).all()


# =========================
# PRODUCT CRUD
# =========================

def create_product(
    db: Session,
    name: str,
    category_name: str,
    sku: str,
    barcode: Optional[str],
    unit: str,
    price: float,
    cost: float,
    stock: int,
    reorder_level: int,
    max_stock: int,
    supplier_id: Optional[int],
    expiry_date: Optional[date],
    manufactured_date: Optional[date],
    status: str
) -> Tuple[Optional[Product], Optional[str]]:
    """
    Create a new product. Validates category, SKU, and barcode uniqueness.
    Returns (product, None) on success, (None, error_message) on failure.
    """
    category, err = _resolve_category(db, category_name)
    if err:
        return None, err

    if db.query(Product).filter(Product.sku == sku).first():
        return None, "SKU already exists"

    if barcode and db.query(Product).filter(Product.barcode == barcode).first():
        return None, "Barcode already exists"

    product = Product(
        name=name,
        category_id=category.category_id,
        sku=sku,
        barcode=barcode,
        unit=unit,
        price=price,
        cost=cost,
        stock=stock,
        reorder_level=reorder_level,
        max_stock=max_stock,
        supplier_id=supplier_id,
        expiry_date=expiry_date,
        manufactured_date=manufactured_date,
        status=status,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product, None


def update_product(
    db: Session,
    product_id: int,
    name: str,
    category_name: str,
    sku: str,
    barcode: Optional[str],
    unit: str,
    price: float,
    cost: float,
    reorder_level: int,
    max_stock: int,
    supplier_id: Optional[int],
    expiry_date: Optional[date],
    manufactured_date: Optional[date],
    status: str
) -> Tuple[Optional[Product], Optional[str]]:
    """
    Update a product. Validates category, SKU conflicts, and barcode conflicts.
    Returns (product, None) on success, (None, error_message) on failure.
    """
    product = get_product_by_id(db, product_id)
    if not product:
        return None, "Product not found"

    category, err = _resolve_category(db, category_name)
    if err:
        return None, err

    sku_conflict = db.query(Product).filter(
        Product.sku == sku, Product.product_id != product_id
    ).first()
    if sku_conflict:
        return None, "SKU already in use"

    if barcode:
        bc_conflict = db.query(Product).filter(
            Product.barcode == barcode, Product.product_id != product_id
        ).first()
        if bc_conflict:
            return None, "Barcode already in use"

    product.name = name
    product.category_id = category.category_id
    product.sku = sku
    product.barcode = barcode
    product.unit = unit
    product.price = price
    product.cost = cost
    product.reorder_level = reorder_level
    product.max_stock = max_stock
    product.supplier_id = supplier_id
    product.expiry_date = expiry_date
    product.manufactured_date = manufactured_date
    product.status = status

    db.commit()
    db.refresh(product)
    return product, None


def discontinue_product(db: Session, product_id: int) -> Tuple[bool, Optional[str]]:
    """Soft delete — marks product as discontinued."""
    product = get_product_by_id(db, product_id)
    if not product:
        return False, "Product not found"

    product.status = "discontinued"
    db.commit()
    return True, None