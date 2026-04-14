from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Optional
import uuid
import razorpay
from fastapi import Depends, FastAPI, Request, Header, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from app.db import SessionLocal
from app.models import (
    Category,
    CreditTransaction,
    Customer,
    DamageLossRecord,
    Expense,
    MilkDeliveryEntry,
    MilkSubscriber,
    Product,
    Sale,
    SaleItem,
    StockMovement,
    Supplier,
    SupplierPayment,
    User,
)
from app.seed import init_db, seed_data
from app.security import hash_password, verify_password


app = FastAPI(title="Sonik Backend V2", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(x_user_id: int = Header(..., alias="X-User-ID"), db: Session = Depends(get_db)) -> User:
    user = db.get(User, x_user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing X-User-ID header")
    return user


def as_float(value) -> float:
    return round(float(value or 0), 2)


def parse_iso_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {value}") from exc


def serialize_product(product: Product) -> dict:
    return {
        "product_id": product.product_id,
        "id": product.product_id,
        "name": product.name,
        "category_id": product.category_id,
        "category": product.category.category_name if product.category else None,
        "sku": product.sku,
        "barcode": product.barcode,
        "unit": product.unit,
        "cost_price": as_float(product.cost_price),
        "cost": as_float(product.cost_price),
        "price": as_float(product.price),
        "selling_price": as_float(product.price),
        "stock": product.stock_quantity,
        "quantity": product.stock_quantity,
        "reorder_level": product.reorder_level,
        "max_stock": product.max_stock,
        "expiry_date": product.expiry_date.isoformat() if product.expiry_date else None,
        "status": product.status,
        "hsn_code": product.hsn_code,
        "description": product.description,
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
        "profit_margin": round(((as_float(product.price) - as_float(product.cost_price)) / as_float(product.price) * 100), 2)
        if as_float(product.price) > 0
        else 0,
        "inventory_value": round(as_float(product.cost_price) * product.stock_quantity, 2),
    }


def serialize_stock_movement(movement: StockMovement) -> dict:
    return {
        "movement_id": movement.movement_id,
        "product_id": movement.product_id,
        "movement_type": movement.movement_type,
        "quantity_change": movement.quantity_change,
        "notes": movement.notes,
        "created_by": movement.created_by,
        "created_at": movement.created_at.isoformat() if movement.created_at else None,
    }


def serialize_customer(customer: Customer) -> dict:
    return {
        "customer_id": customer.customer_id,
        "id": customer.customer_id,
        "name": customer.name,
        "phone": customer.phone,
        "email": customer.email,
        "address": customer.address,
        "city": customer.city,
        "credit_limit": as_float(customer.credit_limit),
        "credit_balance": as_float(customer.credit_balance),
        "risk_level": customer.risk_level,
        "status": customer.status,
        "created_at": customer.created_at.isoformat() if customer.created_at else None,
        "updated_at": customer.updated_at.isoformat() if customer.updated_at else None,
    }


def serialize_milk_subscriber(subscriber: MilkSubscriber) -> dict:
    return {
        "subscriber_id": subscriber.subscriber_id,
        "id": subscriber.subscriber_id,
        "name": subscriber.name,
        "phone": subscriber.phone,
        "quantity": round(float(subscriber.quantity or 0), 2),
        "frequency": subscriber.frequency,
        "start_date": subscriber.start_date.isoformat() if subscriber.start_date else None,
        "status": subscriber.status,
        "amount": as_float(subscriber.amount),
        "address": subscriber.address,
        "note": subscriber.note,
        "created_at": subscriber.created_at.isoformat() if subscriber.created_at else None,
        "updated_at": subscriber.updated_at.isoformat() if subscriber.updated_at else None,
    }


def serialize_milk_delivery_entry(entry: MilkDeliveryEntry) -> dict:
    return {
        "entry_id": entry.entry_id,
        "subscriber_id": entry.subscriber_id,
        "entry_date": entry.entry_date.isoformat() if entry.entry_date else None,
        "quantity": round(float(entry.quantity or 0), 2),
        "temperature": round(float(entry.temperature), 2) if entry.temperature is not None else None,
        "quality": entry.quality,
        "note": entry.note,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
        "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,
    }


def serialize_supplier(supplier: Supplier, pending_amount: float = 0) -> dict:
    return {
        "supplier_id": supplier.supplier_id,
        "name": supplier.name,
        "contact_person": supplier.contact_person,
        "phone": supplier.phone,
        "email": supplier.email,
        "address": supplier.address,
        "city": supplier.city,
        "rating": round(float(supplier.rating or 0), 1),
        "payment_terms": supplier.payment_terms,
        "status": supplier.status,
        "pending_amount": round(float(pending_amount or 0), 2),
    }


def serialize_expense(expense: Expense) -> dict:
    return {
        "expense_id": expense.expense_id,
        "title": expense.title,
        "amount": as_float(expense.amount),
        "category": expense.category,
        "note": expense.note,
        "expense_date": expense.expense_date.isoformat() if expense.expense_date else None,
        "recurring": expense.recurring,
        "created_by": expense.created_by,
    }


def serialize_sale_item(item: SaleItem) -> dict:
    return {
        "bill_item_id": item.bill_item_id,
        "bill_id": item.bill_id,
        "product_id": item.product_id,
        "quantity": item.quantity,
        "unit_price": as_float(item.unit_price),
        "discount": as_float(item.discount),
        "tax_amount": as_float(item.tax_amount),
        "subtotal": as_float(item.subtotal),
        "product": {
            "product_id": item.product.product_id,
            "name": item.product.name,
            "unit": item.product.unit,
            "price": as_float(item.product.price),
            "stock": item.product.stock_quantity,
            "category_id": item.product.category_id,
        }
        if item.product
        else None,
    }


def serialize_sale(sale: Sale) -> dict:
    return {
        "bill_id": sale.bill_id,
        "customer_id": sale.customer_id,
        "user_id": sale.user_id,
        "receipt_number": sale.receipt_number,
        "bill_date": sale.bill_date.isoformat() if sale.bill_date else None,
        "total_amount": as_float(sale.total_amount),
        "discount_amount": as_float(sale.discount_amount),
        "tax_amount": as_float(sale.tax_amount),
        "payment_method": sale.payment_method,
        "status": sale.status,
        "created_at": sale.created_at.isoformat() if sale.created_at else None,
        "updated_at": sale.updated_at.isoformat() if sale.updated_at else None,
        "items": [serialize_sale_item(item) for item in sale.items],
        "transactions": [],
    }


def serialize_credit_transaction(txn: CreditTransaction) -> dict:
    return {
        "transaction_id": txn.transaction_id,
        "id": txn.transaction_id,
        "customer_id": txn.customer_id,
        "sale_id": txn.sale_id,
        "amount": as_float(txn.amount),
        "type": txn.type,
        "status": txn.status,
        "note": txn.note,
        "due_date": txn.due_date.isoformat() if txn.due_date else None,
        "transaction_date": txn.transaction_date.isoformat() if txn.transaction_date else None,
        "created_at": txn.transaction_date.isoformat() if txn.transaction_date else None,
    }


def compute_risk_level(balance: float, limit: float) -> tuple[float, str]:
    if limit <= 0:
        return 0.0, "low"
    usage = round((balance / limit) * 100, 2)
    if usage >= 80:
        return usage, "high"
    if usage >= 50:
        return usage, "medium"
    return usage, "low"


def resolve_category(db: Session, category_name: Optional[str], category_id: Optional[int]) -> Optional[Category]:
    if category_id:
        return db.get(Category, category_id)
    if category_name:
        category = db.scalar(select(Category).where(func.lower(Category.category_name) == category_name.strip().lower()))
        if not category:
            category = Category(category_name=category_name.strip())
            db.add(category)
            db.flush()
        return category
    return None


def create_stock_movement(db: Session, product_id: int, movement_type: str, quantity_change: int, notes: Optional[str], user_id: Optional[int]) -> None:
    db.add(
        StockMovement(
            product_id=product_id,
            movement_type=movement_type,
            quantity_change=quantity_change,
            notes=notes,
            created_by=user_id,
        )
    )


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    phone: str
    role: str


class ProductWrite(BaseModel):
    name: str
    category: Optional[str] = None
    category_id: Optional[int] = None
    unit: Optional[str] = None
    cost_price: float = Field(alias="cost_price")
    selling_price: float = Field(alias="selling_price")
    quantity: int = 0
    reorder_level: int = 10
    max_stock: int = 100
    expiry_date: Optional[str] = None
    hsn_code: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None


class StockAdjustmentRequest(BaseModel):
    product_id: int
    quantity: int
    reason: str


class DamageLossRequest(BaseModel):
    product_id: int
    quantity: int
    reason: str
    date: Optional[str] = None
    notes: Optional[str] = None
    estimated_loss: Optional[float] = None


class SaleItemWrite(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    discount: float = 0
    tax_amount: float = 0
    subtotal: float


class SaleWrite(BaseModel):
    customer_id: Optional[int] = None
    payment_method: str
    discount_amount: float = 0
    items: list[SaleItemWrite]


class CustomerWrite(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    credit_limit: float = 0


class MilkSubscriberWrite(BaseModel):
    name: str
    phone: str
    quantity: float
    frequency: str = "daily"
    start_date: Optional[str] = None
    status: str = "active"
    amount: Optional[float] = None
    address: Optional[str] = None
    note: Optional[str] = None


class MilkDeliveryEntryWrite(BaseModel):
    entry_date: str
    quantity: float
    temperature: Optional[float] = None
    quality: Optional[str] = None
    note: Optional[str] = None


class CreditLimitWrite(BaseModel):
    credit_limit: float
    reason: str


class PaymentWrite(BaseModel):
    amount: float
    mode: str
    reference: Optional[str] = None


class FreezeWrite(BaseModel):
    reason: str
    duration_days: int


class SupplierWrite(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    rating: float = 0
    payment_terms: int = 30
    status: str = "active"


class SupplierPaymentWrite(BaseModel):
    amount: float
    mode: str
    po_id: Optional[int] = None
    cheque_no: Optional[str] = None
    note: Optional[str] = None


class ExpenseWrite(BaseModel):
    title: str
    amount: float
    category: str
    note: Optional[str] = None
    expense_date: Optional[str] = None
    recurring: bool = False


class TransactionWrite(BaseModel):
    customer_id: int
    amount: float
    type: str
    sale_id: Optional[int] = None
    note: Optional[str] = None
    due_date: Optional[str] = None


class CategoryWrite(BaseModel):
    category_name: str


class RazorpayOrderRequest(BaseModel):
    amount: float = Field(gt=0)
    receipt: Optional[str] = None
    notes: Optional[dict] = None


@app.on_event("startup")
def startup_event() -> None:
    init_db()
    with SessionLocal() as db:
        seed_data(db)


@app.get("/")
def root():
    return {"message": "Sonik Backend V2 is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {
        "message": "Login successful",
        "user": {
            "id": user.user_id,
            "user_id": user.user_id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "designation": user.designation,
        },
    }


@app.post("/api/users/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        name=payload.name,
        email=payload.email,
        password=hash_password(payload.password),
        phone=payload.phone,
        role="employee",
        designation=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "message": "Registration successful",
        "user": {
            "user_id": user.user_id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "designation": user.designation,
        },
    }


@app.get("/api/categories")
def get_categories(db: Session = Depends(get_db)):
    rows = db.scalars(select(Category).order_by(Category.category_name.asc())).all()
    return [{"category_id": row.category_id, "category_name": row.category_name} for row in rows]


@app.post("/api/categories")
def create_category(payload: CategoryWrite, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    existing = db.scalar(select(Category).where(func.lower(Category.category_name) == payload.category_name.strip().lower()))
    if existing:
        return {"category_id": existing.category_id, "category_name": existing.category_name}
    category = Category(category_name=payload.category_name.strip())
    db.add(category)
    db.commit()
    db.refresh(category)
    return {"category_id": category.category_id, "category_name": category.category_name}


@app.get("/api/categories/{category_id}")
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"category_id": category.category_id, "category_name": category.category_name}


@app.put("/api/categories/{category_id}")
def update_category(category_id: int, payload: CategoryWrite, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category.category_name = payload.category_name.strip()
    db.commit()
    db.refresh(category)
    return {"category_id": category.category_id, "category_name": category.category_name}


@app.delete("/api/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}


@app.post("/api/inventory")
def create_product(payload: ProductWrite, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    category = resolve_category(db, payload.category, payload.category_id)
    product = Product(
        name=payload.name,
        category_id=category.category_id if category else None,
        sku=payload.sku,
        barcode=payload.barcode,
        unit=payload.unit,
        cost_price=payload.cost_price,
        price=payload.selling_price,
        stock_quantity=payload.quantity,
        reorder_level=payload.reorder_level,
        max_stock=payload.max_stock,
        expiry_date=parse_iso_date(payload.expiry_date),
        status="active",
        hsn_code=payload.hsn_code,
        description=payload.description,
    )
    db.add(product)
    db.flush()
    if payload.quantity:
        create_stock_movement(db, product.product_id, "in", payload.quantity, "Initial stock", user.user_id)
    db.commit()
    db.refresh(product)
    return serialize_product(product)


@app.get("/api/inventory")
def list_products(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = select(Product)
    if category:
        query = query.join(Category, isouter=True).where(func.lower(Category.category_name) == category.lower())
    if status_filter:
        query = query.where(Product.status == status_filter)
    if search:
        like = f"%{search.lower()}%"
        query = query.where(or_(func.lower(Product.name).like(like), func.lower(func.coalesce(Product.unit, "")).like(like)))
    rows = db.scalars(query.order_by(Product.created_at.desc()).offset(skip).limit(limit)).all()
    return [serialize_product(row) for row in rows]


@app.get("/api/inventory/{product_id}")
def get_product_detail(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    response = serialize_product(product)
    movements = db.scalars(select(StockMovement).where(StockMovement.product_id == product_id).order_by(StockMovement.created_at.desc())).all()
    response["stock_movements"] = [serialize_stock_movement(m) for m in movements]
    return response


@app.put("/api/inventory/{product_id}")
def update_product(product_id: int, payload: ProductWrite, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    category = resolve_category(db, payload.category, payload.category_id)
    product.name = payload.name
    product.category_id = category.category_id if category else None
    product.unit = payload.unit
    product.cost_price = payload.cost_price
    product.price = payload.selling_price
    product.stock_quantity = payload.quantity
    product.reorder_level = payload.reorder_level
    product.max_stock = payload.max_stock
    product.expiry_date = parse_iso_date(payload.expiry_date)
    product.hsn_code = payload.hsn_code
    product.description = payload.description
    if payload.sku is not None:
        product.sku = payload.sku
    if payload.barcode is not None:
        product.barcode = payload.barcode
    db.commit()
    db.refresh(product)
    return serialize_product(product)


@app.delete("/api/inventory/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.status = "discontinued"
    db.commit()
    return {"message": "Product discontinued successfully", "product_id": product_id}


@app.post("/api/inventory/stock-adjustment")
def adjust_stock(payload: StockAdjustmentRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    product = db.get(Product, payload.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    new_stock = product.stock_quantity + payload.quantity
    if new_stock < 0:
        raise HTTPException(status_code=400, detail="Stock cannot go below 0")
    product.stock_quantity = new_stock
    create_stock_movement(db, product.product_id, "adjustment", payload.quantity, payload.reason, user.user_id)
    db.commit()
    return {"message": "Stock adjusted successfully", "product_id": product.product_id, "new_stock": new_stock, "change": payload.quantity}


@app.get("/api/inventory/{product_id}/movements")
def get_stock_movements(product_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rows = db.scalars(
        select(StockMovement).where(StockMovement.product_id == product_id).order_by(StockMovement.created_at.desc()).offset(skip).limit(limit)
    ).all()
    return [serialize_stock_movement(row) for row in rows]


@app.get("/api/inventory/alerts/low-stock")
def low_stock_alerts(db: Session = Depends(get_db)):
    rows = db.scalars(select(Product).where(Product.status == "active", Product.stock_quantity < Product.reorder_level)).all()
    return [
        {
            "product_id": row.product_id,
            "name": row.name,
            "sku": row.sku,
            "current_stock": row.stock_quantity,
            "reorder_level": row.reorder_level,
            "units_needed": max(row.reorder_level - row.stock_quantity, 0),
        }
        for row in rows
    ]


@app.get("/api/inventory/alerts/expiring-soon")
def expiring_alerts(days: int = 30, db: Session = Depends(get_db)):
    threshold = date.today() + timedelta(days=days)
    rows = db.scalars(
        select(Product).where(Product.expiry_date.is_not(None), Product.expiry_date >= date.today(), Product.expiry_date <= threshold)
    ).all()
    return [
        {
            "product_id": row.product_id,
            "name": row.name,
            "expiry_date": row.expiry_date.isoformat(),
            "days_left": (row.expiry_date - date.today()).days,
            "stock": row.stock_quantity,
        }
        for row in rows
    ]


@app.get("/api/inventory/value/total")
def inventory_value(db: Session = Depends(get_db)):
    rows = db.scalars(select(Product).where(Product.status == "active")).all()
    total_value = round(sum(as_float(row.cost_price) * row.stock_quantity for row in rows), 2)
    count = len(rows)
    return {
        "total_inventory_value": total_value,
        "number_of_products": count,
        "average_product_value": round(total_value / count, 2) if count else 0,
    }


@app.post("/api/inventory/damage-loss")
def damage_loss(payload: DamageLossRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    product = db.get(Product, payload.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock_quantity < payload.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock to log damage/loss")
    product.stock_quantity -= payload.quantity
    record = DamageLossRecord(
        product_id=payload.product_id,
        quantity=payload.quantity,
        reason=payload.reason,
        estimated_loss=payload.estimated_loss or (as_float(product.cost_price) * payload.quantity),
        notes=payload.notes,
        reported_by=user.user_id,
    )
    db.add(record)
    create_stock_movement(db, payload.product_id, "out", -payload.quantity, payload.reason, user.user_id)
    db.commit()
    db.refresh(record)
    return {
        "id": record.id,
        "product_id": record.product_id,
        "quantity": record.quantity,
        "reason": record.reason,
        "estimated_loss": as_float(record.estimated_loss),
        "notes": record.notes,
        "reported_by": record.reported_by,
        "created_at": record.created_at.isoformat(),
    }


@app.get("/api/inventory/damage-loss/report")
def damage_loss_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = select(DamageLossRecord)
    if start_date:
        query = query.where(DamageLossRecord.created_at >= datetime.combine(parse_iso_date(start_date), datetime.min.time()))
    if end_date:
        query = query.where(DamageLossRecord.created_at <= datetime.combine(parse_iso_date(end_date), datetime.max.time()))
    if reason:
        query = query.where(DamageLossRecord.reason == reason)
    rows = db.scalars(query.order_by(DamageLossRecord.created_at.desc())).all()
    return [
        {
            "date": row.created_at.isoformat() if row.created_at else None,
            "product_name": row.product.name if row.product else None,
            "reason": row.reason,
            "quantity": row.quantity,
            "cost_price": as_float(row.product.cost_price) if row.product else 0,
            "notes": row.notes,
        }
        for row in rows
    ]


@app.get("/api/inventory/stats/overview")
def inventory_stats(db: Session = Depends(get_db)):
    total_products = db.scalar(select(func.count(Product.product_id))) or 0
    active_products = db.scalar(select(func.count(Product.product_id)).where(Product.status == "active")) or 0
    low_stock = db.scalar(select(func.count(Product.product_id)).where(Product.status == "active", Product.stock_quantity < Product.reorder_level)) or 0
    expiring_soon = db.scalar(
        select(func.count(Product.product_id)).where(
            Product.expiry_date.is_not(None),
            Product.expiry_date >= date.today(),
            Product.expiry_date <= date.today() + timedelta(days=30),
        )
    ) or 0
    return {
        "total_products": total_products,
        "active_products": active_products,
        "low_stock": low_stock,
        "expiring_soon": expiring_soon,
    }


@app.get("/api/sales/products/search")
def search_products(q: str, db: Session = Depends(get_db)):
    like = f"%{q.lower()}%"
    rows = db.scalars(
        select(Product).where(Product.status == "active", or_(func.lower(Product.name).like(like), func.lower(func.coalesce(Product.sku, "")).like(like)))
    ).all()
    return [
        {
            "product_id": row.product_id,
            "name": row.name,
            "sku": row.sku,
            "barcode": row.barcode,
            "unit": row.unit,
            "price": as_float(row.price),
            "cost": as_float(row.cost_price),
            "stock": row.stock_quantity,
            "category_id": row.category_id,
            "status": row.status,
        }
        for row in rows
    ]


@app.get("/api/sales/products/{product_id}")
def get_sale_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {
        "product_id": product.product_id,
        "name": product.name,
        "sku": product.sku,
        "barcode": product.barcode,
        "unit": product.unit,
        "price": as_float(product.price),
        "cost": as_float(product.cost_price),
        "stock": product.stock_quantity,
        "category_id": product.category_id,
        "status": product.status,
    }


@app.get("/api/sales/products/barcode/{barcode}")
def get_product_by_barcode(barcode: str, db: Session = Depends(get_db)):
    product = db.scalar(select(Product).where(Product.barcode == barcode))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {
        "product_id": product.product_id,
        "name": product.name,
        "sku": product.sku,
        "barcode": product.barcode,
        "unit": product.unit,
        "price": as_float(product.price),
        "cost": as_float(product.cost_price),
        "stock": product.stock_quantity,
        "category_id": product.category_id,
        "status": product.status,
    }


@app.get("/api/sales/daily/summary")
def daily_summary(date: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    target_date = parse_iso_date(date)
    start = datetime.combine(target_date, datetime.min.time())
    end = datetime.combine(target_date, datetime.max.time())
    rows = db.scalars(select(Sale).where(Sale.bill_date >= start, Sale.bill_date <= end)).all()
    total_revenue = sum(as_float(row.total_amount) for row in rows)
    total_discount = sum(as_float(row.discount_amount) for row in rows)
    total_tax = sum(as_float(row.tax_amount) for row in rows)
    order_count = len(rows)
    payment_breakdown = {
        "cash": round(sum(as_float(row.total_amount) for row in rows if row.payment_method == "cash"), 2),
        "upi": round(sum(as_float(row.total_amount) for row in rows if row.payment_method == "upi"), 2),
        "credit": round(sum(as_float(row.total_amount) for row in rows if row.payment_method == "credit"), 2),
        "card": round(sum(as_float(row.total_amount) for row in rows if row.payment_method == "card"), 2),
    }
    return {
        "date": target_date.isoformat(),
        "total_sales": round(total_revenue, 2),
        "total_discount": round(total_discount, 2),
        "total_tax": round(total_tax, 2),
        "total_revenue": round(total_revenue, 2),
        "transaction_count": order_count,
        "order_count": order_count,
        "average_order_value": round(total_revenue / order_count, 2) if order_count else 0,
        "payment_breakdown": payment_breakdown,
    }


@app.post("/api/sales")
def create_sale(payload: SaleWrite, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="At least one sale item is required")
    if payload.payment_method == "credit" and not payload.customer_id:
        raise HTTPException(status_code=400, detail="Customer is required for credit sales")
    customer = db.get(Customer, payload.customer_id) if payload.customer_id else None
    if payload.customer_id and not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if customer and customer.status == "frozen" and payload.payment_method == "credit":
        raise HTTPException(status_code=400, detail="This customer's credit is frozen. Cannot process a credit sale.")

    total_tax = 0.0
    item_rows: list[tuple[Product, SaleItemWrite]] = []
    for item in payload.items:
        product = db.get(Product, item.product_id)
        if not product or product.status != "active":
            raise HTTPException(status_code=404, detail=f"Product ID {item.product_id} not found")
        if product.stock_quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for '{product.name}'")
        total_tax += item.tax_amount
        item_rows.append((product, item))

    total_amount = round(sum(item.subtotal for _, item in item_rows) - payload.discount_amount, 2)
    sale = Sale(
        customer_id=payload.customer_id,
        user_id=user.user_id,
        receipt_number=f"RCP-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}",
        bill_date=datetime.utcnow(),
        total_amount=total_amount,
        discount_amount=payload.discount_amount,
        tax_amount=round(total_tax, 2),
        payment_method=payload.payment_method,
        status="paid",
    )
    db.add(sale)
    db.flush()
    for product, item in item_rows:
        product.stock_quantity -= item.quantity
        db.add(
            SaleItem(
                bill_id=sale.bill_id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount=item.discount,
                tax_amount=item.tax_amount,
                subtotal=item.subtotal,
            )
        )
        create_stock_movement(db, product.product_id, "out", -item.quantity, f"Sale {sale.receipt_number}", user.user_id)

    if customer and payload.payment_method == "credit":
        customer.credit_balance = as_float(customer.credit_balance) + total_amount
        _, customer.risk_level = compute_risk_level(as_float(customer.credit_balance), as_float(customer.credit_limit))
        db.add(
            CreditTransaction(
                customer_id=customer.customer_id,
                sale_id=sale.bill_id,
                amount=total_amount,
                type="debit",
                status="pending",
                note=f"Sale #{sale.receipt_number}",
                due_date=date.today() + timedelta(days=30),
            )
        )

    db.commit()
    db.refresh(sale)
    return serialize_sale(sale)


@app.get("/api/sales")
def list_sales(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    payment_method: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    customer_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(Sale)
    if start_date:
        query = query.where(Sale.bill_date >= datetime.combine(parse_iso_date(start_date), datetime.min.time()))
    if end_date:
        query = query.where(Sale.bill_date <= datetime.combine(parse_iso_date(end_date), datetime.max.time()))
    if payment_method:
        query = query.where(Sale.payment_method == payment_method)
    if status_filter:
        query = query.where(Sale.status == status_filter)
    if customer_id:
        query = query.where(Sale.customer_id == customer_id)
    rows = db.scalars(query.order_by(Sale.bill_date.desc()).offset(skip).limit(limit)).all()
    return [
        {
            "bill_id": row.bill_id,
            "receipt_number": row.receipt_number,
            "customer_id": row.customer_id,
            "customer_name": row.customer.name if row.customer else "Walk-in",
            "bill_date": row.bill_date.isoformat() if row.bill_date else None,
            "total_amount": as_float(row.total_amount),
            "discount_amount": as_float(row.discount_amount),
            "tax_amount": as_float(row.tax_amount),
            "payment_method": row.payment_method,
            "status": row.status,
        }
        for row in rows
    ]


@app.get("/api/sales/{bill_id}")
def get_sale(bill_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    sale = db.get(Sale, bill_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return serialize_sale(sale)


@app.post("/api/sales/{bill_id}/reverse")
def reverse_sale(bill_id: int, reason: str = "Reversed from UI", db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sale = db.get(Sale, bill_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    if sale.status == "cancelled":
        raise HTTPException(status_code=400, detail="Sale is already reversed")
    for item in sale.items:
        product = db.get(Product, item.product_id)
        if product:
            product.stock_quantity += item.quantity
            create_stock_movement(db, product.product_id, "return", item.quantity, f"Sale reversal {sale.receipt_number}", user.user_id)
    sale.status = "cancelled"
    if sale.customer_id and sale.payment_method == "credit":
        customer = db.get(Customer, sale.customer_id)
        if customer:
            customer.credit_balance = max(0, as_float(customer.credit_balance) - as_float(sale.total_amount))
            _, customer.risk_level = compute_risk_level(as_float(customer.credit_balance), as_float(customer.credit_limit))
        debit_txn = db.scalar(select(CreditTransaction).where(CreditTransaction.sale_id == bill_id, CreditTransaction.type == "debit"))
        if debit_txn:
            debit_txn.status = "waived"
        db.add(
            CreditTransaction(
                customer_id=sale.customer_id,
                sale_id=bill_id,
                amount=0,
                type="reversal",
                status="waived",
                note=f"Sale #{sale.receipt_number} reversed by user {user.user_id}. Reason: {reason}",
            )
        )
    db.commit()
    return {"message": "Sale reversed successfully", "bill_id": bill_id, "receipt_number": sale.receipt_number, "reason": reason}


@app.get("/api/milk/subscribers")
def list_milk_subscribers(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(MilkSubscriber)
    if status_filter:
        query = query.where(MilkSubscriber.status == status_filter)
    if search:
        like = f"%{search.lower()}%"
        query = query.where(
            or_(
                func.lower(MilkSubscriber.name).like(like),
                func.lower(MilkSubscriber.phone).like(like),
            )
        )
    rows = db.scalars(query.order_by(MilkSubscriber.created_at.desc())).all()
    return [serialize_milk_subscriber(row) for row in rows]


@app.post("/api/milk/subscribers")
def create_milk_subscriber(payload: MilkSubscriberWrite, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    subscriber = MilkSubscriber(
        name=payload.name.strip(),
        phone=payload.phone.strip(),
        quantity=payload.quantity,
        frequency=payload.frequency,
        start_date=parse_iso_date(payload.start_date) or date.today(),
        status=payload.status,
        amount=payload.amount if payload.amount is not None else payload.quantity,
        address=payload.address,
        note=payload.note,
    )
    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)
    return serialize_milk_subscriber(subscriber)


@app.get("/api/milk/subscribers/{subscriber_id}")
def get_milk_subscriber(subscriber_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    subscriber = db.get(MilkSubscriber, subscriber_id)
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    return serialize_milk_subscriber(subscriber)


@app.put("/api/milk/subscribers/{subscriber_id}")
def update_milk_subscriber(
    subscriber_id: int,
    payload: MilkSubscriberWrite,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    subscriber = db.get(MilkSubscriber, subscriber_id)
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    subscriber.name = payload.name.strip()
    subscriber.phone = payload.phone.strip()
    subscriber.quantity = payload.quantity
    subscriber.frequency = payload.frequency
    subscriber.start_date = parse_iso_date(payload.start_date) or subscriber.start_date
    subscriber.status = payload.status
    subscriber.amount = payload.amount if payload.amount is not None else payload.quantity
    subscriber.address = payload.address
    subscriber.note = payload.note
    db.commit()
    db.refresh(subscriber)
    return serialize_milk_subscriber(subscriber)


@app.delete("/api/milk/subscribers/{subscriber_id}")
def delete_milk_subscriber(subscriber_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    subscriber = db.get(MilkSubscriber, subscriber_id)
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    subscriber.status = "inactive"
    db.commit()
    db.refresh(subscriber)
    return {"message": "Subscriber deactivated successfully", "subscriber": serialize_milk_subscriber(subscriber)}


@app.get("/api/milk/subscribers/{subscriber_id}/entries")
def list_milk_delivery_entries(
    subscriber_id: int,
    month: Optional[int] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    subscriber = db.get(MilkSubscriber, subscriber_id)
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    query = select(MilkDeliveryEntry).where(MilkDeliveryEntry.subscriber_id == subscriber_id)
    if month and year:
        start = date(year, month, 1)
        end = date(year + (1 if month == 12 else 0), 1 if month == 12 else month + 1, 1) - timedelta(days=1)
        query = query.where(MilkDeliveryEntry.entry_date >= start, MilkDeliveryEntry.entry_date <= end)
    rows = db.scalars(query.order_by(MilkDeliveryEntry.entry_date.asc())).all()
    return [serialize_milk_delivery_entry(row) for row in rows]


@app.post("/api/milk/subscribers/{subscriber_id}/entries")
def upsert_milk_delivery_entry(
    subscriber_id: int,
    payload: MilkDeliveryEntryWrite,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    subscriber = db.get(MilkSubscriber, subscriber_id)
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    entry_date = parse_iso_date(payload.entry_date)
    entry = db.scalar(
        select(MilkDeliveryEntry).where(
            MilkDeliveryEntry.subscriber_id == subscriber_id,
            MilkDeliveryEntry.entry_date == entry_date,
        )
    )
    if not entry:
        entry = MilkDeliveryEntry(subscriber_id=subscriber_id, entry_date=entry_date)
        db.add(entry)
    entry.quantity = payload.quantity
    entry.temperature = payload.temperature
    entry.quality = payload.quality
    entry.note = payload.note
    db.commit()
    db.refresh(entry)
    return serialize_milk_delivery_entry(entry)


@app.delete("/api/milk/subscribers/{subscriber_id}/entries/{entry_id}")
def delete_milk_delivery_entry(
    subscriber_id: int,
    entry_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    entry = db.get(MilkDeliveryEntry, entry_id)
    if not entry or entry.subscriber_id != subscriber_id:
        raise HTTPException(status_code=404, detail="Milk delivery entry not found")
    db.delete(entry)
    db.commit()
    return {"message": "Milk delivery entry deleted successfully", "entry_id": entry_id}


@app.post("/api/customers")
def create_customer(payload: CustomerWrite, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    customer = Customer(
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        address=payload.address,
        city=payload.city,
        credit_limit=payload.credit_limit,
        credit_balance=0,
        risk_level="low",
        status="active",
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return serialize_customer(customer)


@app.get("/api/customers")
def list_customers(
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(Customer)
    if status_filter:
        query = query.where(Customer.status == status_filter)
    if search:
        like = f"%{search.lower()}%"
        query = query.where(
            or_(
                func.lower(Customer.name).like(like),
                func.lower(func.coalesce(Customer.phone, "")).like(like),
                func.lower(func.coalesce(Customer.email, "")).like(like),
            )
        )
    rows = db.scalars(query.order_by(Customer.created_at.desc()).offset(skip).limit(limit)).all()
    return [serialize_customer(row) for row in rows]


@app.get("/api/customers/risk-assessment")
def risk_assessment(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.scalars(select(Customer).where(Customer.status == "active")).all()
    result = []
    for row in rows:
        usage, level = compute_risk_level(as_float(row.credit_balance), as_float(row.credit_limit))
        result.append(
            {
                "customer_id": row.customer_id,
                "name": row.name,
                "phone": row.phone,
                "credit_limit": as_float(row.credit_limit),
                "credit_balance": as_float(row.credit_balance),
                "risk_percentage": usage,
                "risk_level": level,
            }
        )
    return sorted(result, key=lambda item: item["risk_percentage"], reverse=True)


@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    txns = db.scalars(select(CreditTransaction).where(CreditTransaction.customer_id == customer_id)).all()
    total_purchases = sum(as_float(txn.amount) for txn in txns if txn.type == "debit")
    total_payments = sum(as_float(txn.amount) for txn in txns if txn.type in {"credit", "payment"})
    purchase_count = sum(1 for txn in txns if txn.type == "debit")
    response = serialize_customer(customer)
    response.update(
        {
            "total_purchases": round(total_purchases, 2),
            "total_payments": round(total_payments, 2),
            "outstanding_balance": round(total_purchases - total_payments, 2),
            "average_order_value": round(total_purchases / purchase_count, 2) if purchase_count else 0,
            "purchase_count": purchase_count,
        }
    )
    return response


@app.put("/api/customers/{customer_id}")
def update_customer(customer_id: int, payload: CustomerWrite, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer.name = payload.name
    customer.phone = payload.phone
    customer.email = payload.email
    customer.address = payload.address
    customer.city = payload.city
    customer.credit_limit = payload.credit_limit
    _, customer.risk_level = compute_risk_level(as_float(customer.credit_balance), as_float(customer.credit_limit))
    db.commit()
    db.refresh(customer)
    return serialize_customer(customer)


@app.put("/api/customers/{customer_id}/credit-limit")
def update_credit_limit(customer_id: int, payload: CreditLimitWrite, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    old_limit = as_float(customer.credit_limit)
    customer.credit_limit = payload.credit_limit
    _, customer.risk_level = compute_risk_level(as_float(customer.credit_balance), as_float(customer.credit_limit))
    db.add(
        CreditTransaction(
            customer_id=customer_id,
            amount=0,
            type="credit_limit_change",
            status="paid",
            note=f"Credit limit changed from {old_limit} to {payload.credit_limit}. Reason: {payload.reason}",
        )
    )
    db.commit()
    db.refresh(customer)
    return serialize_customer(customer)


@app.post("/api/customers/{customer_id}/payment")
def customer_payment(customer_id: int, payload: PaymentWrite, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer.credit_balance = max(0, as_float(customer.credit_balance) - payload.amount)
    _, customer.risk_level = compute_risk_level(as_float(customer.credit_balance), as_float(customer.credit_limit))
    db.add(
        CreditTransaction(
            customer_id=customer_id,
            amount=payload.amount,
            type="credit",
            status="paid",
            note=f"Payment received via {payload.mode}. Ref: {payload.reference or 'N/A'}",
        )
    )
    db.commit()
    return {"message": "Payment recorded successfully", "customer_id": customer_id, "amount_paid": payload.amount, "remaining_balance": as_float(customer.credit_balance)}


@app.post("/api/customers/{customer_id}/credit-freeze")
def customer_freeze(customer_id: int, payload: FreezeWrite, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer.status = "frozen"
    db.add(
        CreditTransaction(
            customer_id=customer_id,
            amount=0,
            type="credit_freeze",
            status="paid",
            note=f"Credit frozen for {payload.duration_days} days. Reason: {payload.reason}",
        )
    )
    db.commit()
    return {"message": "Credit frozen successfully", "customer_id": customer_id, "duration_days": payload.duration_days, "reason": payload.reason}


@app.delete("/api/customers/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if as_float(customer.credit_balance) > 0:
        raise HTTPException(status_code=400, detail="Cannot delete customer with an outstanding credit balance")
    db.delete(customer)
    db.commit()
    return {"message": "Customer deleted successfully"}


@app.get("/api/transactions/report/credit-aging")
def credit_aging_report(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    customers = db.scalars(select(Customer).where(Customer.credit_balance > 0)).all()
    today = date.today()
    result = []
    for customer in customers:
        txns = db.scalars(
            select(CreditTransaction).where(CreditTransaction.customer_id == customer.customer_id, CreditTransaction.type == "debit", CreditTransaction.status.in_(["pending", "overdue"]))
        ).all()
        buckets = defaultdict(float)
        for txn in txns:
            due_date = txn.due_date or today
            overdue_days = (today - due_date).days
            if overdue_days <= 0:
                buckets["current"] += as_float(txn.amount)
            elif overdue_days <= 30:
                buckets["overdue_30"] += as_float(txn.amount)
            elif overdue_days <= 60:
                buckets["overdue_60"] += as_float(txn.amount)
            else:
                buckets["overdue_90"] += as_float(txn.amount)
        total = sum(buckets.values())
        result.append(
            {
                "customer_id": customer.customer_id,
                "name": customer.name,
                "phone": customer.phone,
                "current": round(buckets["current"], 2),
                "overdue_30": round(buckets["overdue_30"], 2),
                "overdue_60": round(buckets["overdue_60"], 2),
                "overdue_90": round(buckets["overdue_90"], 2),
                "total_outstanding": round(total, 2),
            }
        )
    return sorted(result, key=lambda item: item["total_outstanding"], reverse=True)


@app.post("/api/transactions")
def add_transaction(payload: TransactionWrite, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    customer = db.get(Customer, payload.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if payload.type == "debit":
        customer.credit_balance = as_float(customer.credit_balance) + payload.amount
        status_value = "pending"
    else:
        customer.credit_balance = max(0, as_float(customer.credit_balance) - payload.amount)
        status_value = "paid"
    _, customer.risk_level = compute_risk_level(as_float(customer.credit_balance), as_float(customer.credit_limit))
    txn = CreditTransaction(
        customer_id=payload.customer_id,
        sale_id=payload.sale_id,
        amount=payload.amount,
        type=payload.type,
        status=status_value,
        note=payload.note,
        due_date=parse_iso_date(payload.due_date),
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return serialize_credit_transaction(txn)


@app.get("/api/transactions/{customer_id}")
def get_transactions(
    customer_id: int,
    type: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(CreditTransaction).where(CreditTransaction.customer_id == customer_id)
    if type:
        query = query.where(CreditTransaction.type == type)
    if status_filter:
        query = query.where(CreditTransaction.status == status_filter)
    rows = db.scalars(query.order_by(CreditTransaction.transaction_date.desc())).all()
    return [serialize_credit_transaction(row) for row in rows]


@app.patch("/api/transactions/{transaction_id}/waive")
def waive_transaction(transaction_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    txn = db.get(CreditTransaction, transaction_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    txn.status = "waived"
    customer = db.get(Customer, txn.customer_id)
    if customer and txn.type == "debit":
        customer.credit_balance = max(0, as_float(customer.credit_balance) - as_float(txn.amount))
        _, customer.risk_level = compute_risk_level(as_float(customer.credit_balance), as_float(customer.credit_limit))
    db.commit()
    return {"message": "Transaction waived", "transaction_id": transaction_id}


@app.post("/api/suppliers")
def create_supplier(payload: SupplierWrite, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    supplier = Supplier(**payload.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return serialize_supplier(supplier)


@app.get("/api/suppliers/payment-history/all")
def supplier_payment_history(
    supplier_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(SupplierPayment)
    if supplier_id:
        query = query.where(SupplierPayment.supplier_id == supplier_id)
    if start_date:
        query = query.where(SupplierPayment.created_at >= datetime.combine(parse_iso_date(start_date), datetime.min.time()))
    if end_date:
        query = query.where(SupplierPayment.created_at <= datetime.combine(parse_iso_date(end_date), datetime.max.time()))
    rows = db.scalars(query.order_by(SupplierPayment.created_at.desc())).all()
    return [
        {
            "payment_id": row.payment_id,
            "supplier_id": row.supplier_id,
            "amount": as_float(row.amount),
            "mode": row.mode,
            "po_id": row.po_id,
            "cheque_no": row.cheque_no,
            "status": row.status,
            "due_date": row.due_date.isoformat() if row.due_date else None,
            "paid_date": row.paid_date.isoformat() if row.paid_date else None,
            "note": row.note,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
        for row in rows
    ]


@app.get("/api/suppliers")
def list_suppliers(
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(Supplier)
    if status_filter:
        query = query.where(Supplier.status == status_filter)
    if search:
        like = f"%{search.lower()}%"
        query = query.where(or_(func.lower(Supplier.name).like(like), func.lower(Supplier.phone).like(like)))
    rows = db.scalars(query.order_by(Supplier.created_at.desc()).offset(skip).limit(limit)).all()
    result = []
    for row in rows:
        pending = db.scalar(select(func.sum(SupplierPayment.amount)).where(SupplierPayment.supplier_id == row.supplier_id, SupplierPayment.status == "pending")) or 0
        result.append(serialize_supplier(row, pending))
    return result


@app.get("/api/suppliers/{supplier_id}")
def get_supplier(supplier_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    supplier = db.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    pending = db.scalar(select(func.sum(SupplierPayment.amount)).where(SupplierPayment.supplier_id == supplier_id, SupplierPayment.status == "pending")) or 0
    return serialize_supplier(supplier, pending)


@app.put("/api/suppliers/{supplier_id}")
def update_supplier(supplier_id: int, payload: SupplierWrite, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    supplier = db.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    for key, value in payload.model_dump().items():
        setattr(supplier, key, value)
    db.commit()
    db.refresh(supplier)
    pending = db.scalar(select(func.sum(SupplierPayment.amount)).where(SupplierPayment.supplier_id == supplier_id, SupplierPayment.status == "pending")) or 0
    return serialize_supplier(supplier, pending)


@app.delete("/api/suppliers/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    supplier = db.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    supplier.status = "inactive"
    db.commit()
    return {"message": "Supplier deactivated successfully"}


@app.get("/api/suppliers/{supplier_id}/pending-payments")
def pending_supplier_payments(supplier_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.scalars(select(SupplierPayment).where(SupplierPayment.supplier_id == supplier_id, SupplierPayment.status == "pending")).all()
    return [
        {
            "payment_id": row.payment_id,
            "supplier_id": row.supplier_id,
            "amount": as_float(row.amount),
            "mode": row.mode,
            "po_id": row.po_id,
            "cheque_no": row.cheque_no,
            "status": row.status,
            "due_date": row.due_date.isoformat() if row.due_date else None,
            "paid_date": row.paid_date.isoformat() if row.paid_date else None,
            "note": row.note,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
        for row in rows
    ]


@app.post("/api/suppliers/{supplier_id}/payment")
def record_supplier_payment(supplier_id: int, payload: SupplierPaymentWrite, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    supplier = db.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    payment = SupplierPayment(
        supplier_id=supplier_id,
        amount=payload.amount,
        mode=payload.mode,
        po_id=payload.po_id,
        cheque_no=payload.cheque_no,
        note=payload.note,
        status="paid",
        paid_date=date.today(),
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return {
        "payment_id": payment.payment_id,
        "supplier_id": payment.supplier_id,
        "amount": as_float(payment.amount),
        "mode": payment.mode,
        "po_id": payment.po_id,
        "cheque_no": payment.cheque_no,
        "status": payment.status,
        "due_date": payment.due_date.isoformat() if payment.due_date else None,
        "paid_date": payment.paid_date.isoformat() if payment.paid_date else None,
        "note": payment.note,
        "created_at": payment.created_at.isoformat() if payment.created_at else None,
    }


@app.post("/api/expenses")
def create_expense(payload: ExpenseWrite, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    expense = Expense(
        title=payload.title,
        amount=payload.amount,
        category=payload.category,
        note=payload.note,
        expense_date=parse_iso_date(payload.expense_date) or date.today(),
        recurring=payload.recurring,
        created_by=user.user_id,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return serialize_expense(expense)


@app.get("/api/expenses")
def list_expenses(
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(Expense)
    if category:
        query = query.where(Expense.category == category)
    if start_date:
        query = query.where(Expense.expense_date >= parse_iso_date(start_date))
    if end_date:
        query = query.where(Expense.expense_date <= parse_iso_date(end_date))
    rows = db.scalars(query.order_by(Expense.expense_date.desc()).offset(skip).limit(limit)).all()
    return [serialize_expense(row) for row in rows]


@app.get("/api/expenses/summary")
def expense_summary(month: Optional[int] = None, year: Optional[int] = None, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    today = date.today()
    target_month = month or today.month
    target_year = year or today.year
    rows = db.scalars(select(Expense).where(func.strftime("%m", Expense.expense_date) == f"{target_month:02d}", func.strftime("%Y", Expense.expense_date) == str(target_year))).all()
    total = sum(as_float(row.amount) for row in rows)
    category_totals = defaultdict(lambda: {"total": 0.0, "count": 0})
    for row in rows:
        category_totals[row.category]["total"] += as_float(row.amount)
        category_totals[row.category]["count"] += 1
    prev_month = 12 if target_month == 1 else target_month - 1
    prev_year = target_year - 1 if target_month == 1 else target_year
    prev_rows = db.scalars(select(Expense).where(func.strftime("%m", Expense.expense_date) == f"{prev_month:02d}", func.strftime("%Y", Expense.expense_date) == str(prev_year))).all()
    prev_total = sum(as_float(row.amount) for row in prev_rows)
    return {
        "month": target_month,
        "year": target_year,
        "total_expenses": round(total, 2),
        "by_category": [
            {
                "category": key,
                "total": round(value["total"], 2),
                "count": value["count"],
                "percentage": round((value["total"] / total * 100), 2) if total else 0,
            }
            for key, value in category_totals.items()
        ],
        "previous_month_total": round(prev_total, 2),
        "change_percentage": round(((total - prev_total) / prev_total * 100), 2) if prev_total else 0,
    }


@app.get("/api/expenses/financial-report")
def financial_report(from_date: str, to_date: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    start = parse_iso_date(from_date)
    end = parse_iso_date(to_date)
    if start > end:
        raise HTTPException(status_code=400, detail="from_date must be before to_date")
    expenses = db.scalars(select(Expense).where(Expense.expense_date >= start, Expense.expense_date <= end)).all()
    sales = db.scalars(select(Sale).where(Sale.bill_date >= datetime.combine(start, datetime.min.time()), Sale.bill_date <= datetime.combine(end, datetime.max.time()), Sale.status == "paid")).all()
    total_revenue = sum(as_float(row.total_amount) for row in sales)
    total_expenses = sum(as_float(row.amount) for row in expenses)
    breakdown_map = defaultdict(lambda: {"total": 0.0, "count": 0})
    for row in expenses:
        breakdown_map[row.category]["total"] += as_float(row.amount)
        breakdown_map[row.category]["count"] += 1
    return {
        "from_date": start.isoformat(),
        "to_date": end.isoformat(),
        "total_revenue": round(total_revenue, 2),
        "total_expenses": round(total_expenses, 2),
        "net_profit": round(total_revenue - total_expenses, 2),
        "profit_margin_pct": round(((total_revenue - total_expenses) / total_revenue * 100), 2) if total_revenue else 0,
        "expense_breakdown": [
            {
                "category": key,
                "total": round(value["total"], 2),
                "count": value["count"],
                "percentage": round((value["total"] / total_expenses * 100), 2) if total_expenses else 0,
            }
            for key, value in breakdown_map.items()
        ],
    }


@app.delete("/api/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    expense = db.get(Expense, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
    return {"message": "Expense deleted successfully"}


@app.get("/api/dashboard/kpis")
def dashboard_kpis(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    today = date.today()
    month_start = today.replace(day=1)
    sales_today = db.scalars(select(Sale).where(Sale.bill_date >= datetime.combine(today, datetime.min.time()), Sale.bill_date <= datetime.combine(today, datetime.max.time()), Sale.status == "paid")).all()
    sales_month = db.scalars(select(Sale).where(Sale.bill_date >= datetime.combine(month_start, datetime.min.time()), Sale.status == "paid")).all()
    inventory_rows = db.scalars(select(Product).where(Product.status == "active")).all()
    low_stock = [row for row in inventory_rows if row.stock_quantity < row.reorder_level]
    expiring = [row for row in inventory_rows if row.expiry_date and row.expiry_date <= today + timedelta(days=7) and row.expiry_date >= today]
    today_sales_value = sum(as_float(row.total_amount) for row in sales_today)
    today_cost = sum(sum(as_float(item.product.cost_price) * item.quantity for item in row.items) for row in sales_today)
    monthly_revenue = sum(as_float(row.total_amount) for row in sales_month)
    outstanding_credit = db.scalar(select(func.sum(Customer.credit_balance))) or 0
    payment_breakdown = {
        "cash": round(sum(as_float(row.total_amount) for row in sales_today if row.payment_method == "cash"), 2),
        "upi": round(sum(as_float(row.total_amount) for row in sales_today if row.payment_method == "upi"), 2),
        "credit": round(sum(as_float(row.total_amount) for row in sales_today if row.payment_method == "credit"), 2),
        "card": round(sum(as_float(row.total_amount) for row in sales_today if row.payment_method == "card"), 2),
    }
    return {
        "date": today.isoformat(),
        "total_revenue": round(today_sales_value, 2),
        "total_discount": round(sum(as_float(row.discount_amount) for row in sales_today), 2),
        "total_tax": round(sum(as_float(row.tax_amount) for row in sales_today), 2),
        "order_count": len(sales_today),
        "average_order_value": round(today_sales_value / len(sales_today), 2) if sales_today else 0,
        "gross_profit": round(today_sales_value - today_cost, 2),
        "profit_margin_pct": round(((today_sales_value - today_cost) / today_sales_value * 100), 2) if today_sales_value else 0,
        "payment_breakdown": payment_breakdown,
        "today_sales": round(today_sales_value, 2),
        "today_profit": round(today_sales_value - today_cost, 2),
        "monthly_revenue": round(monthly_revenue, 2),
        "outstanding_credit": round(as_float(outstanding_credit), 2),
        "low_stock_count": len(low_stock),
        "expiring_count": len(expiring),
    }


@app.get("/api/dashboard/alerts")
def dashboard_alerts(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    low_stock = low_stock_alerts(db)
    expiring = expiring_alerts(7, db)
    customers = db.scalars(select(Customer).where(Customer.status == "active", Customer.credit_limit > 0, Customer.credit_balance > 0)).all()
    high_risk = []
    for customer in customers:
        usage, _ = compute_risk_level(as_float(customer.credit_balance), as_float(customer.credit_limit))
        if usage >= 80:
            high_risk.append(
                {
                    "customer_id": customer.customer_id,
                    "name": customer.name,
                    "phone": customer.phone,
                    "credit_limit": as_float(customer.credit_limit),
                    "credit_balance": as_float(customer.credit_balance),
                    "usage_pct": usage,
                }
            )
    return {
        "low_stock": low_stock,
        "expiring_soon": expiring,
        "high_risk_customers": high_risk,
        "alert_counts": {
            "low_stock": len(low_stock),
            "expiring_soon": len(expiring),
            "high_risk_customers": len(high_risk),
        },
    }


@app.get("/api/shifts/report")
def shift_report(
    report_date: Optional[str] = Query(None, alias="date"),
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target_date = parse_iso_date(report_date) if report_date else date.today()
    start_dt = datetime.combine(target_date, datetime.min.time())
    end_dt = datetime.combine(target_date, datetime.max.time())
    requested_user_id = current_user.user_id if current_user.role == "employee" else user_id

    query = select(Sale).where(
        Sale.bill_date >= start_dt,
        Sale.bill_date <= end_dt,
        Sale.user_id.is_not(None),
    )
    if requested_user_id:
        query = query.where(Sale.user_id == requested_user_id)

    rows = db.scalars(query.order_by(Sale.bill_date.asc())).all()
    users = {row.user_id: row for row in db.scalars(select(User)).all()}

    grouped: dict[tuple[int, str], dict] = {}
    for sale in rows:
        key = (sale.user_id, sale.bill_date.date().isoformat())
        user = users.get(sale.user_id)
        bucket = grouped.setdefault(
            key,
            {
                "user_id": sale.user_id,
                "employee": user.name if user else f"User {sale.user_id}",
                "designation": user.designation if user else None,
                "date": sale.bill_date.date().isoformat(),
                "first_sale_at": sale.bill_date,
                "last_sale_at": sale.bill_date,
                "sales": 0.0,
                "transactions": 0,
            },
        )
        bucket["first_sale_at"] = min(bucket["first_sale_at"], sale.bill_date)
        bucket["last_sale_at"] = max(bucket["last_sale_at"], sale.bill_date)
        bucket["sales"] += as_float(sale.total_amount)
        bucket["transactions"] += 1

    reports = []
    for index, bucket in enumerate(sorted(grouped.values(), key=lambda item: (item["date"], item["employee"]), reverse=True), start=1):
        duration_minutes = max(int((bucket["last_sale_at"] - bucket["first_sale_at"]).total_seconds() // 60), 0)
        performance = min(100, round((bucket["transactions"] * 12) + (bucket["sales"] / 250)))
        anomaly = None
        if bucket["transactions"] == 0:
            anomaly = "No Sales"
        elif bucket["sales"] < 1000:
            anomaly = "Low Sales"

        reports.append(
            {
                "id": index,
                "user_id": bucket["user_id"],
                "employee": bucket["employee"],
                "designation": bucket["designation"],
                "date": bucket["date"],
                "start_time": bucket["first_sale_at"].strftime("%H:%M"),
                "end_time": bucket["last_sale_at"].strftime("%H:%M"),
                "duration_minutes": duration_minutes,
                "sales": round(bucket["sales"], 2),
                "transactions": bucket["transactions"],
                "performance": performance,
                "anomaly": anomaly,
            }
        )

    if current_user.role == "employee" and not reports:
        reports.append(
            {
                "id": 1,
                "user_id": current_user.user_id,
                "employee": current_user.name,
                "designation": current_user.designation,
                "date": target_date.isoformat(),
                "start_time": None,
                "end_time": None,
                "duration_minutes": 0,
                "sales": 0.0,
                "transactions": 0,
                "performance": 0,
                "anomaly": "No Sales Yet",
            }
        )

    return reports


@app.get("/api/dashboard/quick-stats")
def quick_stats(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return {
        "total_customers": db.scalar(select(func.count(Customer.customer_id))) or 0,
        "active_customers": db.scalar(select(func.count(Customer.customer_id)).where(Customer.status == "active")) or 0,
        "total_users": db.scalar(select(func.count(User.user_id))) or 0,
        "active_products": db.scalar(select(func.count(Product.product_id)).where(Product.status == "active")) or 0,
        "pending_credit_sales": db.scalar(select(func.count(CreditTransaction.transaction_id)).where(CreditTransaction.type == "debit", CreditTransaction.status == "pending")) or 0,
    }


@app.get("/api/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    sales = db.scalars(select(Sale).where(Sale.status == "paid")).all()
    expenses = db.scalars(select(Expense)).all()
    recent_sales = db.scalars(select(Sale).order_by(Sale.bill_date.desc()).limit(5)).all()
    total_sales = sum(as_float(row.total_amount) for row in sales)
    total_expenses = sum(as_float(row.amount) for row in expenses)
    return {
        "total_sales": round(total_sales, 2),
        "total_expenses": round(total_expenses, 2),
        "profit": round(total_sales - total_expenses, 2),
        "total_bills": len(sales),
        "recent_sales": [
            {
                "bill_id": row.bill_id,
                "customer_name": row.customer.name if row.customer else "Walk-in",
                "bill_date": row.bill_date.isoformat() if row.bill_date else None,
                "total_amount": as_float(row.total_amount),
                "payment_method": row.payment_method,
            }
            for row in recent_sales
        ],
    }


@app.get("/api/dashboard/top-products")
def top_products(limit: int = 5, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.scalars(select(SaleItem)).all()
    stats = defaultdict(lambda: {"product_name": "", "total_sold": 0, "total_revenue": 0.0})
    for row in rows:
        key = row.product_id
        stats[key]["product_name"] = row.product.name if row.product else f"Product {row.product_id}"
        stats[key]["total_sold"] += row.quantity
        stats[key]["total_revenue"] += as_float(row.subtotal)
    sorted_rows = sorted(stats.values(), key=lambda item: item["total_sold"], reverse=True)
    return [
        {
            "product_name": row["product_name"],
            "total_sold": row["total_sold"],
            "total_revenue": round(row["total_revenue"], 2),
        }
        for row in sorted_rows[:limit]
    ]


@app.get("/api/dashboard/sales-overview")
def sales_overview(days: int = 30, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    start = date.today() - timedelta(days=days)
    sales = db.scalars(select(Sale).where(Sale.bill_date >= datetime.combine(start, datetime.min.time()), Sale.status == "paid")).all()
    stats = defaultdict(lambda: {"total_sales": 0.0, "order_count": 0})
    for sale in sales:
        key = sale.bill_date.date().isoformat()
        stats[key]["total_sales"] += as_float(sale.total_amount)
        stats[key]["order_count"] += 1
    return [
        {"date": key, "total_sales": round(value["total_sales"], 2), "order_count": value["order_count"]}
        for key, value in sorted(stats.items())
    ]
# =========================
# SUPPLIER APIs
# =========================

@app.post("/api/suppliers")
def create_supplier(payload: SupplierWrite, db: Session = Depends(get_db)):
    try:
        supplier = Supplier(
            name=payload.name,
            contact_person=payload.contact_person,
            phone=payload.phone,
            email=payload.email,
            address=payload.address,
            city=payload.city,
            rating=payload.rating,
            payment_terms=payload.payment_terms,
            status=payload.status,
        )

        db.add(supplier)
        db.commit()
        db.refresh(supplier)

        return {
            "message": "Supplier created successfully",
            "supplier": serialize_supplier(supplier)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/api/suppliers")
def get_suppliers(db: Session = Depends(get_db)):
    suppliers = db.scalars(select(Supplier)).all()

    return [serialize_supplier(s) for s in suppliers]



# Razorpay client helper
def get_razorpay_client() -> razorpay.Client:
    key_id = os.getenv("RAZORPAY_KEY_ID")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET")
    if not key_id or not key_secret:
        raise HTTPException(status_code=500, detail="Razorpay keys are not configured on the backend")
    return razorpay.Client(auth=(key_id, key_secret))

# -----------------------------
# CREATE ORDER
# -----------------------------
@app.post("/api/create-order")
def create_order(payload: RazorpayOrderRequest):
    client = get_razorpay_client()
    order = client.order.create(
        {
            "amount": int(round(payload.amount * 100)),
            "currency": "INR",
            "payment_capture": 1,
            "receipt": payload.receipt or f"rcpt_{uuid.uuid4().hex[:12]}",
            "notes": payload.notes or {},
        }
    )

    return {
        "order_id": order["id"],
        "amount": order["amount"],
        "currency": order["currency"],
        "key_id": os.getenv("RAZORPAY_KEY_ID"),
    }


# -----------------------------
# VERIFY PAYMENT
# -----------------------------
@app.post("/api/verify-payment")
async def verify_payment(request: Request):
    try:
        client = get_razorpay_client()
        data = await request.json()

        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")

        if not razorpay_order_id or not razorpay_payment_id or not razorpay_signature:
            raise HTTPException(status_code=400, detail="Missing payment fields")

        client.utility.verify_payment_signature(
            {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }
        )

        return {
            "status": "success",
            "message": "Payment verified successfully",
            "payment_id": razorpay_payment_id,
        }

    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature - payment tampered")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
