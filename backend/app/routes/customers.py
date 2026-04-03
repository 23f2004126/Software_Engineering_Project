from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime, date
import re

from app.database import get_db
from app.models.user import Customer, CreditTransaction, User
from app.routes.deps import get_current_user

router = APIRouter(prefix="/api/customers", tags=["Customers"])


# =========================
# SCHEMAS
# =========================

class CustomerCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    credit_limit: float = 0.0

    @validator("phone")
    def validate_phone(cls, v):
        if not re.fullmatch(r"\d{10}", v):
            raise ValueError("Phone number must be exactly 10 digits")
        return v

    @validator("credit_limit")
    def credit_limit_positive(cls, v):
        if v < 0:
            raise ValueError("Credit limit cannot be negative")
        return v


class CreditLimitUpdate(BaseModel):
    credit_limit: float
    reason: str

    @validator("credit_limit")
    def must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Credit limit must be greater than 0")
        return v


class PaymentCreate(BaseModel):
    amount: float
    mode: str
    reference: Optional[str] = None

    @validator("amount")
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("Payment amount must be greater than 0")
        return v

    @validator("mode")
    def valid_mode(cls, v):
        if v not in ("cash", "upi", "cheque", "transfer"):
            raise ValueError("Payment mode must be cash, upi, cheque, or transfer")
        return v


class CreditFreezeRequest(BaseModel):
    reason: str
    duration_days: int

    @validator("duration_days")
    def positive_duration(cls, v):
        if v <= 0:
            raise ValueError("Duration must be at least 1 day")
        return v


class CustomerResponse(BaseModel):
    customer_id: int
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    credit_limit: float
    credit_balance: float
    risk_level: Optional[str] = None
    status: str = "active"

    class Config:
        from_attributes = True


class CustomerDetailResponse(CustomerResponse):
    total_purchases: float = 0.0
    total_payments: float = 0.0
    outstanding_balance: float = 0.0
    average_order_value: float = 0.0
    purchase_count: int = 0


class RiskCustomerResponse(BaseModel):
    customer_id: int
    name: str
    phone: str
    credit_limit: float
    credit_balance: float
    risk_percentage: float
    risk_level: str


# =========================
# HELPER
# =========================

def compute_risk_level(credit_balance: float, credit_limit: float) -> tuple:
    if credit_limit <= 0:
        return 0.0, "low"
    pct = (credit_balance / credit_limit) * 100
    if pct < 50:
        level = "low"
    elif pct < 80:
        level = "medium"
    else:
        level = "high"
    return round(pct, 2), level


# =========================
# POST /api/customers/
# =========================

@router.post("/", response_model=CustomerResponse)
def create_customer(
    data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if db.query(Customer).filter(Customer.phone == data.phone).first():
        raise HTTPException(status_code=400, detail="Phone number already registered")

    _, risk = compute_risk_level(0, data.credit_limit)

    new_customer = Customer(
        name=data.name,
        phone=data.phone,
        email=data.email,
        address=data.address,
        city=data.city,
        credit_limit=data.credit_limit,
        credit_balance=0.0,
        risk_level=risk,
        status="active",
        join_date=date.today()
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer


# =========================
# GET /api/customers/
# =========================

@router.get("/", response_model=List[CustomerResponse])
def get_customers(
    search: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Customer)

    if search:
        query = query.filter(
            Customer.name.ilike(f"%{search}%") |
            Customer.phone.ilike(f"%{search}%") |
            Customer.email.ilike(f"%{search}%")
        )
    if city:
        query = query.filter(Customer.city == city)
    if status:
        query = query.filter(Customer.status == status)

    return query.offset(skip).limit(limit).all()


# =========================
# GET /api/customers/risk-assessment
# =========================

@router.get("/risk-assessment", response_model=List[RiskCustomerResponse])
def get_risk_assessment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customers = db.query(Customer).filter(Customer.status == "active").all()
    result = []

    for c in customers:
        pct, level = compute_risk_level(c.credit_balance, c.credit_limit)
        result.append(RiskCustomerResponse(
            customer_id=c.customer_id,
            name=c.name,
            phone=c.phone,
            credit_limit=c.credit_limit,
            credit_balance=c.credit_balance,
            risk_percentage=pct,
            risk_level=level
        ))

    result.sort(key=lambda x: x.risk_percentage, reverse=True)
    return result


# =========================
# GET /api/customers/:customer_id
# =========================

@router.get("/{customer_id}", response_model=CustomerDetailResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    txns = db.query(CreditTransaction).filter(
        CreditTransaction.customer_id == customer_id
    ).all()

    total_debits = sum(t.amount for t in txns if t.type == "debit")
    total_payments = sum(t.amount for t in txns if t.type == "credit")
    purchase_count = sum(1 for t in txns if t.type == "debit")
    avg_order = (total_debits / purchase_count) if purchase_count > 0 else 0.0

    return CustomerDetailResponse(
        customer_id=customer.customer_id,
        name=customer.name,
        phone=customer.phone,
        email=customer.email,
        address=customer.address,
        city=customer.city,
        credit_limit=customer.credit_limit,
        credit_balance=customer.credit_balance,
        risk_level=customer.risk_level,
        status=customer.status,
        total_purchases=total_debits,
        total_payments=total_payments,
        outstanding_balance=total_debits - total_payments,
        average_order_value=round(avg_order, 2),
        purchase_count=purchase_count
    )


# =========================
# PUT /api/customers/:customer_id
# =========================

@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    conflict = db.query(Customer).filter(
        Customer.phone == data.phone,
        Customer.customer_id != customer_id
    ).first()
    if conflict:
        raise HTTPException(status_code=400, detail="Phone number already in use")

    customer.name = data.name
    customer.phone = data.phone
    customer.email = data.email
    customer.address = data.address
    customer.city = data.city
    customer.credit_limit = data.credit_limit
    # Single source of truth: always compute risk after credit_limit is updated
    _, customer.risk_level = compute_risk_level(customer.credit_balance, customer.credit_limit)

    db.commit()
    db.refresh(customer)

    return customer


# =========================
# PUT /api/customers/:customer_id/credit-limit
# =========================

@router.put("/{customer_id}/credit-limit", response_model=CustomerResponse)
def update_credit_limit(
    customer_id: int,
    data: CreditLimitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    old_limit = customer.credit_limit
    customer.credit_limit = data.credit_limit
    _, customer.risk_level = compute_risk_level(customer.credit_balance, data.credit_limit)

    audit = CreditTransaction(
        customer_id=customer_id,
        amount=0,
        type="credit_limit_change",
        note=f"Credit limit changed from {old_limit} to {data.credit_limit}. Reason: {data.reason}",
        transaction_date=datetime.utcnow()
    )
    db.add(audit)
    db.commit()
    db.refresh(customer)

    return customer


# =========================
# POST /api/customers/:customer_id/payment
# =========================

@router.post("/{customer_id}/payment")
def record_payment(
    customer_id: int,
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if data.amount > customer.credit_balance:
        raise HTTPException(
            status_code=400,
            detail=f"Payment ({data.amount}) exceeds outstanding balance ({customer.credit_balance})"
        )

    customer.credit_balance -= data.amount
    _, customer.risk_level = compute_risk_level(customer.credit_balance, customer.credit_limit)

    transaction = CreditTransaction(
        customer_id=customer_id,
        amount=data.amount,
        type="credit",
        note=f"Payment received via {data.mode}. Ref: {data.reference or 'N/A'}",
        transaction_date=datetime.utcnow()
    )

    db.add(transaction)
    db.commit()

    return {
        "message": "Payment recorded successfully",
        "customer_id": customer_id,
        "amount_paid": data.amount,
        "remaining_balance": customer.credit_balance
    }


# =========================
# POST /api/customers/:customer_id/credit-freeze
# =========================

@router.post("/{customer_id}/credit-freeze")
def freeze_credit(
    customer_id: int,
    data: CreditFreezeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if customer.status == "frozen":
        raise HTTPException(status_code=400, detail="Customer credit is already frozen")

    customer.status = "frozen"

    audit = CreditTransaction(
        customer_id=customer_id,
        amount=0,
        type="credit_freeze",
        note=f"Credit frozen for {data.duration_days} days. Reason: {data.reason}",
        transaction_date=datetime.utcnow()
    )
    db.add(audit)
    db.commit()

    return {
        "message": "Credit frozen successfully",
        "customer_id": customer_id,
        "duration_days": data.duration_days,
        "reason": data.reason
    }


# =========================
# DELETE /api/customers/:customer_id
# =========================

@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if customer.credit_balance > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete customer with an outstanding credit balance"
        )

    db.delete(customer)
    db.commit()

    return {"message": "Customer deleted successfully"}