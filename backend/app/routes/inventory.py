from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, date as date_type, timedelta
from typing import List, Optional

from app.database import get_db
from app.routes.deps import get_current_user
from app.schemas.inventory import (
    ProductCreate, ProductUpdate, ProductResponse, ProductDetailResponse,
    StockMovementResponse, StockAdjustmentRequest,
    DamageLossCreate, DamageLossResponse, InventoryValueResponse,
    DamageLossReport, LowStockAlert, ExpiryAlert
)
from app.models.sale import Product
from app.models.inventory import StockMovement, DamageLossRecord
from app.services import inventory_service

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])


# =========================
# PRODUCT ENDPOINTS
# =========================

@router.post("", response_model=ProductResponse)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    product, error = inventory_service.create_product(db, product_data)

    if error:
        raise HTTPException(status_code=400, detail=error)

    response = ProductResponse(**product.__dict__)
    response.profit_margin = inventory_service.calculate_profit_margin(product.price, product.cost)
    response.inventory_value = product.cost * product.stock

    return response


@router.get("", response_model=List[ProductResponse])
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query("active"),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    products, total = inventory_service.get_products_paginated(
        db,
        skip=skip,
        limit=limit,
        category=category,
        status=status,
        search=search
    )

    response = []
    for product in products:
        product_resp = ProductResponse(**product.__dict__)
        product_resp.profit_margin = inventory_service.calculate_profit_margin(product.price, product.cost)
        product_resp.inventory_value = product.cost * product.stock
        response.append(product_resp)

    return response


@router.get("/{product_id}", response_model=ProductDetailResponse)
def get_product_detail(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = inventory_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    movements, _ = inventory_service.get_stock_movements_for_product(
        db, product_id, skip=0, limit=100
    )
    movements_response = [StockMovementResponse(**m.__dict__) for m in movements]

    low_stock = product.stock < product.reorder_level
    expiring_soon = (
        product.expiry_date and
        product.expiry_date <= date_type.today() + timedelta(days=30)
    )

    response = ProductDetailResponse(
        **product.__dict__,
        stock_movements=movements_response,
        low_stock_alert=low_stock,
        expiring_soon_alert=expiring_soon
    )
    response.profit_margin = inventory_service.calculate_profit_margin(product.price, product.cost)
    response.inventory_value = product.cost * product.stock

    return response


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    product, error = inventory_service.update_product(db, product_id, product_data)

    if error:
        raise HTTPException(status_code=400, detail=error)

    response = ProductResponse(**product.__dict__)
    response.profit_margin = inventory_service.calculate_profit_margin(product.price, product.cost)
    response.inventory_value = product.cost * product.stock

    return response


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    success, error = inventory_service.delete_product(db, product_id)

    if not success:
        raise HTTPException(status_code=400, detail=error)

    return {"message": "Product discontinued successfully", "product_id": product_id}


# =========================
# STOCK MANAGEMENT
# =========================

@router.post("/stock-adjustment", response_model=dict)
def adjust_stock(
    adjustment: StockAdjustmentRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    success, error = inventory_service.adjust_stock(
        db,
        product_id=adjustment.product_id,
        quantity_change=adjustment.quantity,
        movement_type="adjustment",
        notes=adjustment.reason,
        created_by=current_user.user_id
    )

    if not success:
        raise HTTPException(status_code=400, detail=error)

    product = inventory_service.get_product_by_id(db, adjustment.product_id)
    return {
        "message": "Stock adjusted successfully",
        "product_id": adjustment.product_id,
        "new_stock": product.stock,
        "change": adjustment.quantity
    }


@router.get("/{product_id}/movements", response_model=List[StockMovementResponse])
def get_stock_movements(
    product_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    product = inventory_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    movements, total = inventory_service.get_stock_movements_for_product(
        db,
        product_id=product_id,
        skip=skip,
        limit=limit
    )

    return [StockMovementResponse(**m.__dict__) for m in movements]


# =========================
# ALERTS & REPORTS
# =========================

@router.get("/alerts/low-stock", response_model=List[LowStockAlert])
def get_low_stock_products(db: Session = Depends(get_db)):
    return inventory_service.get_low_stock_products(db)


@router.get("/alerts/expiring-soon", response_model=List[ExpiryAlert])
def get_expiring_soon(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    return inventory_service.get_expiring_soon_products(db, days=days)


# =========================
# BARCODE LOOKUP
# =========================

@router.get("/barcode/{barcode}", response_model=ProductResponse)
def get_product_by_barcode(barcode: str, db: Session = Depends(get_db)):
    product = inventory_service.get_product_by_barcode(db, barcode)
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with barcode '{barcode}' not found"
        )

    response = ProductResponse(**product.__dict__)
    response.profit_margin = inventory_service.calculate_profit_margin(product.price, product.cost)
    response.inventory_value = product.cost * product.stock

    return response


# =========================
# INVENTORY VALUE
# =========================

@router.get("/value/total", response_model=InventoryValueResponse)
def get_total_inventory_value(db: Session = Depends(get_db)):
    total_value = inventory_service.calculate_inventory_value(db)
    products_count = db.query(Product).filter(Product.status == "active").count()
    avg_value = total_value / products_count if products_count > 0 else 0

    return InventoryValueResponse(
        total_inventory_value=total_value,
        number_of_products=products_count,
        average_product_value=avg_value
    )


# =========================
# DAMAGE & LOSS
# =========================

@router.post("/damage-loss", response_model=DamageLossResponse)
def log_damage_loss(
    damage_data: DamageLossCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    record, error = inventory_service.log_damage_loss(
        db,
        damage_data=damage_data,
        reported_by=current_user.user_id
    )

    if error:
        raise HTTPException(status_code=400, detail=error)

    return DamageLossResponse(**record.__dict__)


@router.get("/damage-loss/report", response_model=DamageLossReport)
def get_damage_loss_report(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    reason: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    start_dt = None
    end_dt = None

    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use ISO format.")

    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use ISO format.")

    report = inventory_service.get_damage_loss_report(
        db,
        start_date=start_dt,
        end_date=end_dt,
        reason=reason
    )

    return DamageLossReport(**report)


# =========================
# STATISTICS
# =========================

@router.get("/stats/overview", response_model=dict)
def get_inventory_statistics(db: Session = Depends(get_db)):
    return inventory_service.get_inventory_statistics(db)


# =========================
# HEALTH CHECK
# =========================

@router.get("/health/check", tags=["Health"])
def inventory_health_check():
    return {"service": "inventory", "status": "ok"}