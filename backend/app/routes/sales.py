from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from datetime import datetime, date as date_type
from typing import List, Optional

from app.database import get_db
from app.schemas.sale import (
    SaleCreate, SaleResponse, SalesHistoryFilter, SalesHistorySummary,
    DailySummaryResponse, ProductSearchResponse, SaleItemCreate
)
from app.services import sales_service
from app.models.user import User
from app.models.sale import Product
from decimal import Decimal

router = APIRouter(prefix="/api/sales", tags=["Sales"])


# =========================
# FETCHING USER_ID
# =========================

async def get_current_user(db: Session = Depends(get_db), user_id: int = Header(None)) -> int:
    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Missing X-User-ID header. Authentication required."
        )
    
    # Verify user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found or unauthorized"
        )
    
    return user_id


# =========================
# PRODUCT ENDPOINTS
# =========================

@router.get("/products/search", response_model=List[ProductSearchResponse])
def search_products(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    products = sales_service.search_products(db, q)
    return products


@router.get("/products/{product_id}", response_model=ProductSearchResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = sales_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# =========================
# DAILY SUMMARY 
# =========================

@router.get("/daily/summary", response_model=DailySummaryResponse)
def get_daily_summary(
    date: str = Query(..., description="ISO format date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    try:
        summary_date = date_type.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    summary = sales_service.get_daily_summary(db, summary_date)
    return DailySummaryResponse(**summary)


# =========================
# SALE CREATION & RETRIEVAL
# =========================

@router.post("", response_model=SaleResponse)
def create_sale(
    sale_data: SaleCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Request body:
    {
        "customer_id": 1 (optional, null for walk-in),
        "payment_method": "cash|card|upi|credit",
        "discount_amount": 0.00,
        "items": [
            {
                "product_id": 1,
                "quantity": 2,
                "unit_price": 99.99,
                "discount": 0.00,
                "tax_amount": 0.00,
                "subtotal": 199.98
            }
        ]
    }
    """
    sale, error = sales_service.create_sale(db, sale_data, user_id=current_user_id)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    # Refresh to get relationships loaded
    db.refresh(sale)
    return sale


@router.get("/{bill_id}", response_model=SaleResponse)
def get_sale_details(bill_id: int, db: Session = Depends(get_db)):
    """
    Get details of a single sale.
    """
    sale = sales_service.get_sale_by_id(db, bill_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale


@router.get("", response_model=List[SalesHistorySummary])
def get_sales_history(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    customer_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Query parameters:
    - start_date: ISO format date (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
    - end_date: ISO format date
    - payment_method: cash, card, upi, credit
    - status: paid, pending, cancelled
    - customer_id: specific customer
    - skip: offset
    - limit: limit
    """
    # Parse dates 
    start_dt = None
    end_dt = None
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except:
            raise HTTPException(status_code=400, detail="Invalid start_date format")
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except:
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
    
    # Convert to summary response
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
def reverse_sale(bill_id: int, db: Session = Depends(get_db)):
    success, error = sales_service.reverse_sale(db, bill_id)
    
    if not success:
        raise HTTPException(status_code=400, detail=error)
    
    return {
        "message": "Sale reversed successfully",
        "bill_id": bill_id
    }

# HEALTH CHECK
@router.get("/health/check", tags=["Health"])
def sales_health_check():
    return {"service": "sales", "status": "ok"}
