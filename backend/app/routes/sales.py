from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, date as date_type
from typing import List, Optional
import uuid

from app.database import get_db
from app.schemas.sale import (
    SaleCreate, SaleResponse, SalesHistorySummary,
    DailySummaryResponse, ProductSearchResponse
)
from app.services import sales_service
from app.models.user import User, Customer, CreditTransaction
from app.models.sale import Sale, SaleItem, Product
from app.routes.deps import get_current_user

router = APIRouter(prefix="/api/sales", tags=["Sales"])


# =========================
# HELPERS
# =========================

def generate_receipt_number() -> str:
    today = datetime.utcnow().strftime("%Y%m%d")
    suffix = str(uuid.uuid4())[:6].upper()
    return f"RCP-{today}-{suffix}"


def calculate_tax(amount: float, tax_rate: float = 18.0) -> float:
    return round(amount * tax_rate / 100, 2)


# =========================
# PRODUCT SEARCH
# =========================

@router.get("/products/search", response_model=List[ProductSearchResponse])
def search_products(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    return sales_service.search_products(db, q)


@router.get("/products/{product_id}", response_model=ProductSearchResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = sales_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/products/barcode/{barcode}", response_model=ProductSearchResponse)
def get_product_by_barcode(barcode: str, db: Session = Depends(get_db)):
    from app.services import inventory_service
    product = inventory_service.get_product_by_barcode(db, barcode)
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with barcode '{barcode}' not found"
        )
    return product


# =========================
# DAILY SUMMARY
# =========================

@router.get("/daily/summary", response_model=DailySummaryResponse)
def get_daily_summary(
    date: str = Query(..., description="ISO format date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        summary_date = date_type.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    summary = sales_service.get_daily_summary(db, summary_date)
    return DailySummaryResponse(**summary)


# =========================
# CREATE SALE
# =========================

@router.post("", response_model=SaleResponse)
def create_sale(
    sale_data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if sale_data.customer_id:
        customer = db.query(Customer).filter(
            Customer.customer_id == sale_data.customer_id
        ).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        if sale_data.payment_method == "credit" and customer.status == "frozen":
            raise HTTPException(
                status_code=400,
                detail="This customer's credit is frozen. Cannot process a credit sale."
            )

    for item in sale_data.items:
        product = db.query(Product).filter(
            Product.product_id == item.product_id,
            Product.status == "active"
        ).first()
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product ID {item.product_id} not found or discontinued"
            )
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for '{product.name}'. Available: {product.stock}, Requested: {item.quantity}"
            )

    subtotal = sum(i.unit_price * i.quantity for i in sale_data.items)
    discount = sale_data.discount_amount or 0
    if discount > subtotal:
        raise HTTPException(
            status_code=400,
            detail="Discount cannot be greater than the subtotal amount"
        )

    taxable_amount = subtotal - discount
    tax_amount = calculate_tax(taxable_amount)
    total_amount = taxable_amount + tax_amount

    sale_data.receipt_number = generate_receipt_number()
    sale_data.tax_amount = tax_amount
    sale_data.total_amount = total_amount

    sale, error = sales_service.create_sale(db, sale_data, user_id=current_user.user_id)
    if error:
        raise HTTPException(status_code=400, detail=error)

    if sale_data.payment_method == "credit" and sale_data.customer_id:
        customer = db.query(Customer).filter(
            Customer.customer_id == sale_data.customer_id
        ).first()
        if customer:
            customer.credit_balance += total_amount

            if customer.credit_limit > 0:
                pct = customer.credit_balance / customer.credit_limit
                customer.risk_level = "low" if pct < 0.5 else ("medium" if pct < 0.8 else "high")

            txn = CreditTransaction(
                customer_id=sale_data.customer_id,
                sale_id=sale.bill_id,
                amount=total_amount,
                type="debit",
                status="pending",
                note=f"Sale #{sale_data.receipt_number}",
                transaction_date=datetime.utcnow()
            )
            db.add(txn)

        db.commit()

    db.refresh(sale)
    return sale


# =========================
# GET SALE BY ID
# =========================

@router.get("/{bill_id}", response_model=SaleResponse)
def get_sale_details(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sale = sales_service.get_sale_by_id(db, bill_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale


# =========================
# GET SALES HISTORY
# =========================

@router.get("", response_model=List[SalesHistorySummary])
def get_sales_history(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    customer_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    start_dt = None
    end_dt = None

    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid start_date format")

    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid end_date format")

    sales, total = sales_service.get_sales_history(
        db,
        start_date=start_dt,
        end_date=end_dt,
        payment_method=payment_method,
        status=status,
        customer_id=customer_id,
        skip=skip,
        limit=limit
    )

    response = []
    for sale in sales:
        customer_name = sale.customer.name if sale.customer else "Walk-in"
        response.append(
            SalesHistorySummary(
                bill_id=sale.bill_id,
                receipt_number=sale.receipt_number,
                customer_id=sale.customer_id,
                customer_name=customer_name,
                bill_date=sale.bill_date,
                total_amount=sale.total_amount,
                discount_amount=sale.discount_amount,
                tax_amount=sale.tax_amount,
                payment_method=sale.payment_method,
                status=sale.status
            )
        )

    return response


# =========================
# SALE REVERSAL
# =========================

@router.post("/{bill_id}/reverse")
def reverse_sale(
    bill_id: int,
    reason: str = Query(..., description="Reason for reversing this sale"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sale = sales_service.get_sale_by_id(db, bill_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    if sale.status == "reversed":
        raise HTTPException(status_code=400, detail="Sale is already reversed")

    if sale.payment_method == "credit" and sale.customer_id:
        customer = db.query(Customer).filter(
            Customer.customer_id == sale.customer_id
        ).first()
        if customer:
            customer.credit_balance = max(0, customer.credit_balance - sale.total_amount)
            if customer.credit_limit > 0:
                pct = customer.credit_balance / customer.credit_limit
                customer.risk_level = "low" if pct < 0.5 else ("medium" if pct < 0.8 else "high")

        txn = db.query(CreditTransaction).filter(
            CreditTransaction.sale_id == bill_id,
            CreditTransaction.type == "debit"
        ).first()
        if txn:
            txn.status = "waived"

    success, error = sales_service.reverse_sale(db, bill_id)
    if not success:
        raise HTTPException(status_code=400, detail=error)

    audit = CreditTransaction(
        customer_id=sale.customer_id,
        sale_id=bill_id,
        amount=0,
        type="reversal",
        status="waived",
        note=f"Sale #{sale.receipt_number} reversed by user {current_user.user_id}. Reason: {reason}",
        transaction_date=datetime.utcnow()
    )
    db.add(audit)
    db.commit()

    return {
        "message": "Sale reversed successfully",
        "bill_id": bill_id,
        "receipt_number": sale.receipt_number,
        "reason": reason
    }


# =========================
# HEALTH CHECK
# =========================

@router.get("/health/check", tags=["Health"])
def sales_health_check():
    return {"service": "sales", "status": "ok"}