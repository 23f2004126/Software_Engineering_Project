from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime, date, timedelta

from app.database import get_db
from app.models.user import CreditTransaction, Customer, User
from app.routes.deps import get_current_user

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


# =========================
# SCHEMAS
# =========================

class TransactionCreate(BaseModel):
    customer_id: int
    amount: float
    type: str                           # debit / credit
    sale_id: Optional[int] = None
    note: Optional[str] = None
    due_date: Optional[date] = None

    @validator("amount")
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v

    @validator("type")
    def valid_type(cls, v):
        if v not in ("debit", "credit"):
            raise ValueError("Type must be 'debit' (purchase) or 'credit' (payment)")
        return v


class TransactionResponse(BaseModel):
    transaction_id: int
    customer_id: int
    sale_id: Optional[int] = None
    amount: float
    type: str
    status: str
    note: Optional[str] = None
    due_date: Optional[date] = None
    transaction_date: datetime

    class Config:
        from_attributes = True


class CreditReportItem(BaseModel):
    customer_id: int
    name: str
    phone: str
    current: float
    overdue_30: float
    overdue_60: float
    overdue_90: float
    total_outstanding: float


# =========================
# POST /api/transactions/
# =========================

@router.post("/", response_model=TransactionResponse)
def add_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = db.query(Customer).filter(
        Customer.customer_id == data.customer_id
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if customer.status == "frozen" and data.type == "debit":
        raise HTTPException(
            status_code=400,
            detail="Cannot add a debit transaction — this customer's credit is frozen"
        )

    if data.type == "debit":
        if customer.credit_limit > 0 and (customer.credit_balance + data.amount) > customer.credit_limit:
            raise HTTPException(
                status_code=400,
                detail=f"Transaction would exceed credit limit. Available: {customer.credit_limit - customer.credit_balance}"
            )
        customer.credit_balance += data.amount
        status = "pending"
        due = data.due_date or (date.today() + timedelta(days=30))

    else:  # credit (payment)
        # FIFO: apply payment to oldest unpaid debits first
        unpaid = db.query(CreditTransaction).filter(
            CreditTransaction.customer_id == data.customer_id,
            CreditTransaction.type == "debit",
            CreditTransaction.status == "pending"
        ).order_by(CreditTransaction.transaction_date.asc()).all()

        remaining = data.amount
        for txn in unpaid:
            if remaining <= 0:
                break
            if remaining >= txn.amount:
                remaining -= txn.amount
                txn.status = "paid"
            else:
                txn.amount -= remaining
                remaining = 0

        customer.credit_balance = max(0, customer.credit_balance - data.amount)
        status = "paid"
        due = None

    transaction = CreditTransaction(
        customer_id=data.customer_id,
        sale_id=data.sale_id,
        amount=data.amount,
        type=data.type,
        status=status,
        note=data.note,
        due_date=due,
        transaction_date=datetime.utcnow()
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


# =========================
# GET /api/transactions/:customer_id
# =========================

@router.get("/{customer_id}", response_model=List[TransactionResponse])
def get_transactions(
    customer_id: int,
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    query = db.query(CreditTransaction).filter(
        CreditTransaction.customer_id == customer_id
    )

    if type:
        query = query.filter(CreditTransaction.type == type)
    if status:
        query = query.filter(CreditTransaction.status == status)

    return query.order_by(CreditTransaction.transaction_date.desc()).all()


# =========================
# GET /api/transactions/report/credit-aging
# =========================

@router.get("/report/credit-aging", response_model=List[CreditReportItem])
def credit_aging_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customers = db.query(Customer).filter(
        Customer.credit_balance > 0
    ).all()

    today = date.today()
    result = []

    for c in customers:
        pending_txns = db.query(CreditTransaction).filter(
            CreditTransaction.customer_id == c.customer_id,
            CreditTransaction.type == "debit",
            CreditTransaction.status.in_(["pending", "overdue"])
        ).all()

        current = 0.0
        o30 = 0.0
        o60 = 0.0
        o90 = 0.0

        for t in pending_txns:
            due = t.due_date or (t.transaction_date.date() + timedelta(days=30))
            days_overdue = (today - due).days

            if days_overdue <= 0:
                current += t.amount
            elif days_overdue <= 30:
                o30 += t.amount
            elif days_overdue <= 60:
                o60 += t.amount
            else:
                o90 += t.amount

        result.append(CreditReportItem(
            customer_id=c.customer_id,
            name=c.name,
            phone=c.phone,
            current=round(current, 2),
            overdue_30=round(o30, 2),
            overdue_60=round(o60, 2),
            overdue_90=round(o90, 2),
            total_outstanding=round(current + o30 + o60 + o90, 2)
        ))

    result.sort(key=lambda x: x.overdue_90 + x.overdue_60, reverse=True)
    return result


# =========================
# PATCH /api/transactions/:transaction_id/waive
# =========================

@router.patch("/{transaction_id}/waive")
def waive_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    txn = db.query(CreditTransaction).filter(
        CreditTransaction.transaction_id == transaction_id
    ).first()

    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if txn.status not in ("pending", "overdue"):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot waive a transaction with status '{txn.status}'"
        )

    customer = db.query(Customer).filter(
        Customer.customer_id == txn.customer_id
    ).first()
    if customer:
        customer.credit_balance = max(0, customer.credit_balance - txn.amount)

    txn.status = "waived"
    db.commit()

    return {"message": "Transaction waived", "transaction_id": transaction_id}