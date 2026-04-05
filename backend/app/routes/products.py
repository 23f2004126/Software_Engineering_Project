from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models.user import User, Category
from app.models.sale import Product
from app.routes.deps import get_current_user

router = APIRouter(prefix="/api/products", tags=["Products"])


# =========================
# SCHEMAS
# =========================

class ProductCreate(BaseModel):
    name: str
    category: str
    sku: str
    barcode: Optional[str] = None
    unit: str
    price: float
    cost: float
    stock: int = 0
    reorder_level: int = 10
    max_stock: int = 1000
    supplier_id: Optional[int] = None
    expiry_date: Optional[date] = None
    manufactured_date: Optional[date] = None
    status: str = "active"

    @validator("price")
    def price_gt_zero(cls, v):
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v

    @validator("cost")
    def cost_lt_price(cls, v, values):
        if "price" in values and v >= values["price"]:
            raise ValueError("Cost must be less than selling price")
        return v

    @validator("reorder_level")
    def reorder_lt_max(cls, v, values):
        if "max_stock" in values and v >= values["max_stock"]:
            raise ValueError("Reorder level must be less than max stock")
        return v

    @validator("expiry_date")
    def expiry_must_be_future(cls, v):
        if v and v <= date.today():
            raise ValueError("Expiry date must be a future date")
        return v

    @validator("status")
    def valid_status(cls, v):
        if v not in ("active", "discontinued"):
            raise ValueError("Status must be 'active' or 'discontinued'")
        return v


class ProductResponse(BaseModel):
    product_id: int
    name: str
    category_id: Optional[int] = None
    sku: str
    barcode: Optional[str] = None
    unit: str
    price: float
    cost: float
    stock: int
    reorder_level: int
    max_stock: int
    supplier_id: Optional[int] = None
    expiry_date: Optional[date] = None
    manufactured_date: Optional[date] = None
    status: str
    profit_margin: Optional[float] = None
    inventory_value: Optional[float] = None

    class Config:
        from_attributes = True


def _attach_computed(product: Product) -> ProductResponse:
    resp = ProductResponse.from_orm(product)
    if product.price and product.cost and product.price > 0:
        resp.profit_margin = round((product.price - product.cost) / product.price * 100, 2)
    resp.inventory_value = round((product.cost or 0) * (product.stock or 0), 2)
    return resp


# =========================
# POST /api/products/
# =========================

@router.post("/", response_model=ProductResponse)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = db.query(Category).filter(
        Category.category_name == data.category
    ).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")

    if db.query(Product).filter(Product.sku == data.sku).first():
        raise HTTPException(status_code=400, detail="SKU already exists")

    if data.barcode and db.query(Product).filter(Product.barcode == data.barcode).first():
        raise HTTPException(status_code=400, detail="Barcode already exists")

    new_product = Product(
        name=data.name,
        category_id=category.category_id,
        sku=data.sku,
        barcode=data.barcode,
        unit=data.unit,
        price=data.price,
        cost=data.cost,
        stock=data.stock,
        reorder_level=data.reorder_level,
        max_stock=data.max_stock,
        supplier_id=data.supplier_id,
        expiry_date=data.expiry_date,
        manufactured_date=data.manufactured_date,
        status=data.status
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return _attach_computed(new_product)


# =========================
# GET /api/products/
# =========================

@router.get("/", response_model=List[ProductResponse])
def get_products(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query("active"),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
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

    products = query.offset(skip).limit(limit).all()
    return [_attach_computed(p) for p in products]


# =========================
# GET /api/products/search  (live POS search)
# =========================

@router.get("/search", response_model=List[ProductResponse])
def search_products(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    products = db.query(Product).filter(
        Product.status == "active",
        (
            Product.name.ilike(f"%{q}%") |
            Product.sku.ilike(f"%{q}%") |
            Product.barcode.ilike(f"%{q}%")
        )
    ).limit(20).all()

    return [_attach_computed(p) for p in products]


# =========================
# GET /api/products/barcode/:barcode
# =========================

@router.get("/barcode/{barcode}", response_model=ProductResponse)
def get_product_by_barcode(barcode: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(
        Product.barcode == barcode,
        Product.status == "active"
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with barcode '{barcode}' not found"
        )

    return _attach_computed(product)


# =========================
# GET /api/products/:product_id
# =========================

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return _attach_computed(product)


# =========================
# PUT /api/products/:product_id
# =========================

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    category = db.query(Category).filter(
        Category.category_name == data.category
    ).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")

    sku_conflict = db.query(Product).filter(
        Product.sku == data.sku, Product.product_id != product_id
    ).first()
    if sku_conflict:
        raise HTTPException(status_code=400, detail="SKU already in use")

    if data.barcode:
        bc_conflict = db.query(Product).filter(
            Product.barcode == data.barcode, Product.product_id != product_id
        ).first()
        if bc_conflict:
            raise HTTPException(status_code=400, detail="Barcode already in use")

    product.name = data.name
    product.category_id = category.category_id
    product.sku = data.sku
    product.barcode = data.barcode
    product.unit = data.unit
    product.price = data.price
    product.cost = data.cost
    product.reorder_level = data.reorder_level
    product.max_stock = data.max_stock
    product.supplier_id = data.supplier_id
    product.expiry_date = data.expiry_date
    product.manufactured_date = data.manufactured_date
    product.status = data.status

    db.commit()
    db.refresh(product)

    return _attach_computed(product)


# =========================
# DELETE /api/products/:product_id  (soft delete)
# =========================

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.status = "discontinued"
    db.commit()

    return {"message": "Product discontinued successfully", "product_id": product_id}