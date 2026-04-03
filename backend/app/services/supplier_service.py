"""
Service layer for supplier.py routes.
Handles supplier CRUD and payment management.
"""

from sqlalchemy.orm import Session
from typing import Optional, Tuple, List
from datetime import datetime, date

from app.models.user import Supplier
from app.models.supplier import SupplierPayment


# =========================
# SUPPLIER CRUD
# =========================

def get_supplier_by_id(db: Session, supplier_id: int) -> Optional[Supplier]:
    return db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()


def get_suppliers(
    db: Session,
    search: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[Supplier]:
    query = db.query(Supplier)
    if search:
        query = query.filter(
            Supplier.name.ilike(f"%{search}%") |
            Supplier.phone.ilike(f"%{search}%")
        )
    if status:
        query = query.filter(Supplier.status == status)
    return query.offset(skip).limit(limit).all()


def create_supplier(
    db: Session,
    name: str,
    contact_person: Optional[str],
    phone: str,
    email: Optional[str],
    address: Optional[str],
    city: Optional[str],
    rating: float,
    payment_terms: int,
    status: str
) -> Supplier:
    supplier = Supplier(
        name=name,
        contact_person=contact_person,
        phone=phone,
        email=email,
        address=address,
        city=city,
        rating=rating,
        payment_terms=payment_terms,
        status=status,
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


def update_supplier(
    db: Session,
    supplier_id: int,
    name: str,
    contact_person: Optional[str],
    phone: str,
    email: Optional[str],
    address: Optional[str],
    city: Optional[str],
    rating: float,
    payment_terms: int,
    status: str
) -> Tuple[Optional[Supplier], Optional[str]]:
    supplier = get_supplier_by_id(db, supplier_id)
    if not supplier:
        return None, "Supplier not found"

    supplier.name = name
    supplier.contact_person = contact_person
    supplier.phone = phone
    supplier.email = email
    supplier.address = address
    supplier.city = city
    supplier.rating = rating
    supplier.payment_terms = payment_terms
    supplier.status = status

    db.commit()
    db.refresh(supplier)
    return supplier, None


def deactivate_supplier(db: Session, supplier_id: int) -> Tuple[bool, Optional[str]]:
    """Soft delete — sets status to 'inactive'."""
    supplier = get_supplier_by_id(db, supplier_id)
    if not supplier:
        return False, "Supplier not found"

    supplier.status = "inactive"
    db.commit()
    return True, None


def get_supplier_with_pending(db: Session, supplier_id: int) -> Tuple[Optional[dict], Optional[str]]:
    """Return supplier data with total pending payment amount."""
    supplier = get_supplier_by_id(db, supplier_id)
    if not supplier:
        return None, "Supplier not found"

    pending = db.query(SupplierPayment).filter(
        SupplierPayment.supplier_id == supplier_id,
        SupplierPayment.status == "pending"
    ).all()
    total_pending = sum(p.amount for p in pending)

    return {"supplier": supplier, "pending_amount": total_pending}, None


# =========================
# SUPPLIER PAYMENTS
# =========================

def get_pending_payments(db: Session, supplier_id: int) -> Tuple[Optional[List[SupplierPayment]], Optional[str]]:
    supplier = get_supplier_by_id(db, supplier_id)
    if not supplier:
        return None, "Supplier not found"

    payments = db.query(SupplierPayment).filter(
        SupplierPayment.supplier_id == supplier_id,
        SupplierPayment.status == "pending"
    ).order_by(SupplierPayment.due_date.asc()).all()

    return payments, None


def record_supplier_payment(
    db: Session,
    supplier_id: int,
    amount: float,
    mode: str,
    po_id: Optional[int],
    cheque_no: Optional[str],
    note: Optional[str]
) -> Tuple[Optional[SupplierPayment], Optional[str]]:
    supplier = get_supplier_by_id(db, supplier_id)
    if not supplier:
        return None, "Supplier not found"

    payment = SupplierPayment(
        supplier_id=supplier_id,
        amount=amount,
        mode=mode,
        po_id=po_id,
        cheque_no=cheque_no,
        note=note,
        status="paid",
        paid_date=date.today(),
        created_at=datetime.utcnow(),
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment, None


def get_payment_history(
    db: Session,
    supplier_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[SupplierPayment]:
    query = db.query(SupplierPayment)
    if supplier_id:
        query = query.filter(SupplierPayment.supplier_id == supplier_id)
    if start_date:
        query = query.filter(SupplierPayment.created_at >= start_date)
    if end_date:
        query = query.filter(SupplierPayment.created_at <= end_date)
    return query.order_by(SupplierPayment.created_at.desc()).all()