from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime, date

from app.database import get_db
from app.models.user import Supplier, User
from app.models.supplier import SupplierPayment
from app.routes.deps import get_current_user

router = APIRouter(prefix="/api/suppliers", tags=["Suppliers"])


# =========================
# SCHEMAS
# =========================

class SupplierCreate(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    rating: float = 0.0
    payment_terms: int = 30
    status: str = "active"

    @validator("rating")
    def valid_rating(cls, v):
        if not (0 <= v <= 5):
            raise ValueError("Rating must be between 0 and 5")
        return v

    @validator("status")
    def valid_status(cls, v):
        if v not in ("active", "inactive"):
            raise ValueError("Status must be 'active' or 'inactive'")
        return v


class SupplierResponse(BaseModel):
    supplier_id: int
    name: str
    contact_person: Optional[str] = None
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    rating: float
    payment_terms: int
    status: str
    pending_amount: Optional[float] = None

    class Config:
        from_attributes = True


class SupplierPaymentCreate(BaseModel):
    amount: float
    mode: str
    po_id: Optional[int] = None
    cheque_no: Optional[str] = None
    note: Optional[str] = None

    @validator("amount")
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("Payment amount must be greater than 0")
        return v

    @validator("mode")
    def valid_mode(cls, v):
        if v not in ("cash", "cheque", "transfer", "upi"):
            raise ValueError("Mode must be cash, cheque, transfer, or upi")
        return v


class SupplierPaymentResponse(BaseModel):
    payment_id: int
    supplier_id: int
    amount: float
    mode: str
    po_id: Optional[int] = None
    cheque_no: Optional[str] = None
    status: str
    due_date: Optional[date] = None
    paid_date: Optional[date] = None
    note: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# POST /api/suppliers/
# =========================

@router.post("/", response_model=SupplierResponse)
def create_supplier(
    data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    supplier = Supplier(
        name=data.name,
        contact_person=data.contact_person,
        phone=data.phone,
        email=data.email,
        address=data.address,
        city=data.city,
        rating=data.rating,
        payment_terms=data.payment_terms,
        status=data.status
    )

    db.add(supplier)
    db.commit()
    db.refresh(supplier)

    return supplier


# =========================
# GET /api/suppliers/
# =========================

@router.get("/", response_model=List[SupplierResponse])
def get_suppliers(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Supplier)

    if search:
        query = query.filter(
            Supplier.name.ilike(f"%{search}%") |
            Supplier.phone.ilike(f"%{search}%")
        )
    if status:
        query = query.filter(Supplier.status == status)

    return query.offset(skip).limit(limit).all()


# =========================
# GET /api/suppliers/:supplier_id
# =========================

@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    pending = db.query(SupplierPayment).filter(
        SupplierPayment.supplier_id == supplier_id,
        SupplierPayment.status == "pending"
    ).all()
    total_pending = sum(p.amount for p in pending)

    result = SupplierResponse.from_orm(supplier)
    result.pending_amount = total_pending
    return result


# =========================
# PUT /api/suppliers/:supplier_id
# =========================

@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    supplier.name = data.name
    supplier.contact_person = data.contact_person
    supplier.phone = data.phone
    supplier.email = data.email
    supplier.address = data.address
    supplier.city = data.city
    supplier.rating = data.rating
    supplier.payment_terms = data.payment_terms
    supplier.status = data.status

    db.commit()
    db.refresh(supplier)

    return supplier


# =========================
# DELETE /api/suppliers/:supplier_id  (soft delete)
# =========================

@router.delete("/{supplier_id}")
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    supplier.status = "inactive"
    db.commit()

    return {"message": "Supplier deactivated successfully"}


# =========================
# GET /api/suppliers/:supplier_id/pending-payments
# =========================

@router.get("/{supplier_id}/pending-payments", response_model=List[SupplierPaymentResponse])
def get_pending_payments(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    payments = db.query(SupplierPayment).filter(
        SupplierPayment.supplier_id == supplier_id,
        SupplierPayment.status == "pending"
    ).order_by(SupplierPayment.due_date.asc()).all()

    return payments


# =========================
# POST /api/suppliers/:supplier_id/payment
# =========================

@router.post("/{supplier_id}/payment", response_model=SupplierPaymentResponse)
def record_supplier_payment(
    supplier_id: int,
    data: SupplierPaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    payment = SupplierPayment(
        supplier_id=supplier_id,
        amount=data.amount,
        mode=data.mode,
        po_id=data.po_id,
        cheque_no=data.cheque_no,
        note=data.note,
        status="paid",
        paid_date=date.today(),
        created_at=datetime.utcnow()
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


# =========================
# GET /api/suppliers/payment-history/all
# =========================

@router.get("/payment-history/all", response_model=List[SupplierPaymentResponse])
def get_payment_history(
    supplier_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(SupplierPayment)

    if supplier_id:
        query = query.filter(SupplierPayment.supplier_id == supplier_id)

    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(SupplierPayment.created_at >= start_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format")

    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(SupplierPayment.created_at <= end_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format")

    return query.order_by(SupplierPayment.created_at.desc()).all()