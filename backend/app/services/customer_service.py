"""
Service layer for customers.py and transactions.py routes.
Handles customer CRUD, credit management, payments, and transaction logic.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, Tuple, List
from datetime import datetime, date, timedelta

from app.models.user import Customer, CreditTransaction


# =========================
# HELPERS
# =========================

def compute_risk_level(credit_balance: float, credit_limit: float) -> Tuple[float, str]:
    """Return (risk_percentage, risk_level) for a customer."""
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
# CUSTOMER CRUD
# =========================

def get_customer_by_id(db: Session, customer_id: int) -> Optional[Customer]:
    return db.query(Customer).filter(Customer.customer_id == customer_id).first()


def get_customers(
    db: Session,
    search: Optional[str] = None,
    city: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[Customer]:
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


def create_customer(
    db: Session,
    name: str,
    phone: str,
    email: Optional[str],
    address: Optional[str],
    city: Optional[str],
    credit_limit: float
) -> Tuple[Optional[Customer], Optional[str]]:
    if db.query(Customer).filter(Customer.phone == phone).first():
        return None, "Phone number already registered"

    _, risk = compute_risk_level(0, credit_limit)

    customer = Customer(
        name=name,
        phone=phone,
        email=email,
        address=address,
        city=city,
        credit_limit=credit_limit,
        credit_balance=0.0,
        risk_level=risk,
        status="active",
        join_date=date.today(),
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer, None


def update_customer(
    db: Session,
    customer_id: int,
    name: str,
    phone: str,
    email: Optional[str],
    address: Optional[str],
    city: Optional[str],
    credit_limit: float
) -> Tuple[Optional[Customer], Optional[str]]:
    customer = get_customer_by_id(db, customer_id)
    if not customer:
        return None, "Customer not found"

    conflict = db.query(Customer).filter(
        Customer.phone == phone,
        Customer.customer_id != customer_id
    ).first()
    if conflict:
        return None, "Phone number already in use"

    customer.name = name
    customer.phone = phone
    customer.email = email
    customer.address = address
    customer.city = city
    customer.credit_limit = credit_limit
    _, customer.risk_level = compute_risk_level(customer.credit_balance, credit_limit)

    db.commit()
    db.refresh(customer)
    return customer, None


def delete_customer(db: Session, customer_id: int) -> Tuple[bool, Optional[str]]:
    customer = get_customer_by_id(db, customer_id)
    if not customer:
        return False, "Customer not found"
    if customer.credit_balance > 0:
        return False, "Cannot delete customer with an outstanding credit balance"

    db.delete(customer)
    db.commit()
    return True, None


# =========================
# CUSTOMER DETAIL / STATS
# =========================

def get_customer_detail(db: Session, customer_id: int) -> Optional[dict]:
    """Return enriched customer dict with transaction stats."""
    customer = get_customer_by_id(db, customer_id)
    if not customer:
        return None

    txns = db.query(CreditTransaction).filter(
        CreditTransaction.customer_id == customer_id
    ).all()

    total_debits = sum(t.amount for t in txns if t.type == "debit")
    total_payments = sum(t.amount for t in txns if t.type == "credit")
    purchase_count = sum(1 for t in txns if t.type == "debit")
    avg_order = (total_debits / purchase_count) if purchase_count > 0 else 0.0

    return {
        "customer": customer,
        "total_purchases": total_debits,
        "total_payments": total_payments,
        "outstanding_balance": round(total_debits - total_payments, 2),
        "average_order_value": round(avg_order, 2),
        "purchase_count": purchase_count,
    }


# =========================
# CREDIT MANAGEMENT
# =========================

def update_credit_limit(
    db: Session,
    customer_id: int,
    new_limit: float,
    reason: str
) -> Tuple[Optional[Customer], Optional[str]]:
    customer = get_customer_by_id(db, customer_id)
    if not customer:
        return None, "Customer not found"

    old_limit = customer.credit_limit
    customer.credit_limit = new_limit
    _, customer.risk_level = compute_risk_level(customer.credit_balance, new_limit)

    audit = CreditTransaction(
        customer_id=customer_id,
        amount=0,
        type="credit_limit_change",
        note=f"Credit limit changed from {old_limit} to {new_limit}. Reason: {reason}",
        transaction_date=datetime.utcnow(),
    )
    db.add(audit)
    db.commit()
    db.refresh(customer)
    return customer, None


def record_payment(
    db: Session,
    customer_id: int,
    amount: float,
    mode: str,
    reference: Optional[str]
) -> Tuple[Optional[dict], Optional[str]]:
    customer = get_customer_by_id(db, customer_id)
    if not customer:
        return None, "Customer not found"
    if amount > customer.credit_balance:
        return None, f"Payment ({amount}) exceeds outstanding balance ({customer.credit_balance})"

    customer.credit_balance -= amount
    _, customer.risk_level = compute_risk_level(customer.credit_balance, customer.credit_limit)

    transaction = CreditTransaction(
        customer_id=customer_id,
        amount=amount,
        type="credit",
        note=f"Payment received via {mode}. Ref: {reference or 'N/A'}",
        transaction_date=datetime.utcnow(),
    )
    db.add(transaction)
    db.commit()

    return {
        "message": "Payment recorded successfully",
        "customer_id": customer_id,
        "amount_paid": amount,
        "remaining_balance": customer.credit_balance,
    }, None


def freeze_credit(
    db: Session,
    customer_id: int,
    reason: str,
    duration_days: int
) -> Tuple[Optional[dict], Optional[str]]:
    customer = get_customer_by_id(db, customer_id)
    if not customer:
        return None, "Customer not found"
    if customer.status == "frozen":
        return None, "Customer credit is already frozen"

    customer.status = "frozen"

    audit = CreditTransaction(
        customer_id=customer_id,
        amount=0,
        type="credit_freeze",
        note=f"Credit frozen for {duration_days} days. Reason: {reason}",
        transaction_date=datetime.utcnow(),
    )
    db.add(audit)
    db.commit()

    return {
        "message": "Credit frozen successfully",
        "customer_id": customer_id,
        "duration_days": duration_days,
        "reason": reason,
    }, None


# =========================
# RISK ASSESSMENT
# =========================

def get_risk_assessment(db: Session) -> List[dict]:
    """Return all active customers sorted by risk percentage descending."""
    customers = db.query(Customer).filter(Customer.status == "active").all()
    result = []
    for c in customers:
        pct, level = compute_risk_level(c.credit_balance, c.credit_limit)
        result.append({
            "customer_id": c.customer_id,
            "name": c.name,
            "phone": c.phone,
            "credit_limit": c.credit_limit,
            "credit_balance": c.credit_balance,
            "risk_percentage": pct,
            "risk_level": level,
        })
    result.sort(key=lambda x: x["risk_percentage"], reverse=True)
    return result


# =========================
# TRANSACTIONS
# =========================

def get_transactions(
    db: Session,
    customer_id: int,
    type_filter: Optional[str] = None,
    status_filter: Optional[str] = None
) -> Tuple[Optional[List[CreditTransaction]], Optional[str]]:
    customer = get_customer_by_id(db, customer_id)
    if not customer:
        return None, "Customer not found"

    query = db.query(CreditTransaction).filter(
        CreditTransaction.customer_id == customer_id
    )
    if type_filter:
        query = query.filter(CreditTransaction.type == type_filter)
    if status_filter:
        query = query.filter(CreditTransaction.status == status_filter)

    return query.order_by(CreditTransaction.transaction_date.desc()).all(), None


def add_transaction(
    db: Session,
    customer_id: int,
    amount: float,
    txn_type: str,
    sale_id: Optional[int],
    note: Optional[str],
    due_date: Optional[date]
) -> Tuple[Optional[CreditTransaction], Optional[str]]:
    customer = get_customer_by_id(db, customer_id)
    if not customer:
        return None, "Customer not found"

    if customer.status == "frozen" and txn_type == "debit":
        return None, "Cannot add a debit transaction — this customer's credit is frozen"

    if txn_type == "debit":
        if customer.credit_limit > 0 and (customer.credit_balance + amount) > customer.credit_limit:
            available = customer.credit_limit - customer.credit_balance
            return None, f"Transaction would exceed credit limit. Available: {available}"
        customer.credit_balance += amount
        status = "pending"
        effective_due = due_date or (date.today() + timedelta(days=30))

    else:  # credit (payment) — FIFO settlement
        unpaid = db.query(CreditTransaction).filter(
            CreditTransaction.customer_id == customer_id,
            CreditTransaction.type == "debit",
            CreditTransaction.status == "pending"
        ).order_by(CreditTransaction.transaction_date.asc()).all()

        remaining = amount
        for txn in unpaid:
            if remaining <= 0:
                break
            if remaining >= txn.amount:
                remaining -= txn.amount
                txn.status = "paid"
            else:
                txn.amount -= remaining
                remaining = 0

        customer.credit_balance = max(0, customer.credit_balance - amount)
        status = "paid"
        effective_due = None

    transaction = CreditTransaction(
        customer_id=customer_id,
        sale_id=sale_id,
        amount=amount,
        type=txn_type,
        status=status,
        note=note,
        due_date=effective_due,
        transaction_date=datetime.utcnow(),
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction, None


def waive_transaction(
    db: Session,
    transaction_id: int
) -> Tuple[bool, Optional[str]]:
    txn = db.query(CreditTransaction).filter(
        CreditTransaction.transaction_id == transaction_id
    ).first()
    if not txn:
        return False, "Transaction not found"
    if txn.status not in ("pending", "overdue"):
        return False, f"Cannot waive a transaction with status '{txn.status}'"

    customer = get_customer_by_id(db, txn.customer_id)
    if customer:
        customer.credit_balance = max(0, customer.credit_balance - txn.amount)

    txn.status = "waived"
    db.commit()
    return True, None


# =========================
# CREDIT AGING REPORT
# =========================

def get_credit_aging_report(db: Session) -> List[dict]:
    """Break outstanding customer debt into current / 30 / 60 / 90+ day buckets."""
    customers = db.query(Customer).filter(Customer.credit_balance > 0).all()
    today = date.today()
    result = []

    for c in customers:
        pending_txns = db.query(CreditTransaction).filter(
            CreditTransaction.customer_id == c.customer_id,
            CreditTransaction.type == "debit",
            CreditTransaction.status.in_(["pending", "overdue"])
        ).all()

        current = o30 = o60 = o90 = 0.0

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

        result.append({
            "customer_id": c.customer_id,
            "name": c.name,
            "phone": c.phone,
            "current": round(current, 2),
            "overdue_30": round(o30, 2),
            "overdue_60": round(o60, 2),
            "overdue_90": round(o90, 2),
            "total_outstanding": round(current + o30 + o60 + o90, 2),
        })

    result.sort(key=lambda x: x["overdue_90"] + x["overdue_60"], reverse=True)
    return result