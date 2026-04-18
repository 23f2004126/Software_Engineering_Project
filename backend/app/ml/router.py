"""
ML Insights Router
Exposes 4 endpoints for AI Insights on the dashboard.
"""
from importlib import import_module

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import SessionLocal

router = APIRouter(prefix="/api/ml", tags=["ML Insights"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/sales-forecast")
def sales_forecast(db: Session = Depends(get_db)):
    try:
        from app.ml.sales_forecast import get_sales_forecast
        return get_sales_forecast(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sales forecast error: {str(e)}")


@router.get("/inventory-insights")
def inventory_insights(db: Session = Depends(get_db)):
    try:
        from app.ml.inventory_optimizer import get_inventory_insights
        return get_inventory_insights(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inventory insights error: {str(e)}")


@router.get("/cashflow-insights")
def cashflow_insights(db: Session = Depends(get_db)):
    try:
        from app.ml.cashflow_analyzer import get_cashflow_insights
        return get_cashflow_insights(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cashflow insights error: {str(e)}")


@router.get("/credit-risk")
def credit_risk(db: Session = Depends(get_db)):
    try:
        from app.ml.credit_risk import get_credit_risk_insights
        return get_credit_risk_insights(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Credit risk error: {str(e)}")


@router.get("/all-insights")
def all_insights(db: Session = Depends(get_db)):
    """Return all ML insights together while tolerating missing optional dependencies."""
    results = {}
    combined_insights = []

    for key, module_path, fn_name in [
        ("sales_forecast", "app.ml.sales_forecast", "get_sales_forecast"),
        ("inventory", "app.ml.inventory_optimizer", "get_inventory_insights"),
        ("cashflow", "app.ml.cashflow_analyzer", "get_cashflow_insights"),
        ("credit_risk", "app.ml.credit_risk", "get_credit_risk_insights"),
    ]:
        try:
            fn = getattr(import_module(module_path), fn_name)
            data = fn(db)
            results[key] = data
            combined_insights.extend(data.get("insights", []))
        except Exception as e:
            results[key] = {"error": str(e), "insights": []}

    return {
        "insights": combined_insights,
        "details": results,
    }
