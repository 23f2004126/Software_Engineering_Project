"""
Service layer for dashboard.py routes.
All KPI computations, alert queries, quick stats, and trend data.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import date, timedelta

from app.models.user import User, Customer, Expense
from app.models.sale import Sale, SaleItem, Product


# =========================
# KPIs
# =========================

def get_daily_kpis(db: Session, target_date: date) -> dict:
    """
    Full KPI breakdown for a given date:
    revenue, discount, tax, order count, average order value,
    gross profit, profit margin, and payment-method breakdown.
    """
    sales = db.query(Sale).filter(
        func.date(Sale.bill_date) == target_date,
        Sale.status == "completed",
    ).all()

    total_revenue = sum(s.total_amount for s in sales)
    total_discount = sum(s.discount_amount or 0 for s in sales)
    total_tax = sum(s.tax_amount or 0 for s in sales)
    order_count = len(sales)
    avg_order_value = (total_revenue / order_count) if order_count > 0 else 0.0

    cash_total = sum(s.total_amount for s in sales if s.payment_method == "cash")
    upi_total = sum(s.total_amount for s in sales if s.payment_method == "upi")
    credit_total = sum(s.total_amount for s in sales if s.payment_method == "credit")

    # Cost of Goods Sold for profit calculation
    cogs = 0.0
    for sale in sales:
        items = db.query(SaleItem).filter(SaleItem.bill_id == sale.bill_id).all()
        for item in items:
            product = db.query(Product).filter(Product.product_id == item.product_id).first()
            if product:
                cogs += (product.cost or 0) * item.quantity

    profit = total_revenue - cogs
    profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0.0

    return {
        "date": str(target_date),
        "total_revenue": round(total_revenue, 2),
        "total_discount": round(total_discount, 2),
        "total_tax": round(total_tax, 2),
        "order_count": order_count,
        "average_order_value": round(avg_order_value, 2),
        "gross_profit": round(profit, 2),
        "profit_margin_pct": round(profit_margin, 2),
        "payment_breakdown": {
            "cash": round(cash_total, 2),
            "upi": round(upi_total, 2),
            "credit": round(credit_total, 2),
        },
    }


# =========================
# ALERTS
# =========================

def get_dashboard_alerts(db: Session) -> dict:
    """
    Return actionable alerts:
    - Products below reorder level
    - Products expiring within 7 days
    - Customers with credit usage >= 80%
    """
    today = date.today()
    expiry_threshold = today + timedelta(days=7)

    low_stock = db.query(Product).filter(
        Product.status == "active",
        Product.stock < Product.reorder_level,
    ).all()

    expiring = db.query(Product).filter(
        Product.status == "active",
        Product.expiry_date.isnot(None),
        Product.expiry_date <= expiry_threshold,
        Product.expiry_date >= today,
    ).all()

    customers = db.query(Customer).filter(
        Customer.status == "active",
        Customer.credit_limit > 0,
        Customer.credit_balance > 0,
    ).all()

    high_risk = [
        {
            "customer_id": c.customer_id,
            "name": c.name,
            "phone": c.phone,
            "credit_limit": c.credit_limit,
            "credit_balance": c.credit_balance,
            "usage_pct": round(c.credit_balance / c.credit_limit * 100, 1),
        }
        for c in customers
        if (c.credit_balance / c.credit_limit) >= 0.80
    ]

    return {
        "low_stock": [
            {
                "product_id": p.product_id,
                "name": p.name,
                "current_stock": p.stock,
                "reorder_level": p.reorder_level,
            }
            for p in low_stock
        ],
        "expiring_soon": [
            {
                "product_id": p.product_id,
                "name": p.name,
                "expiry_date": str(p.expiry_date),
                "days_left": (p.expiry_date - today).days,
                "stock": p.stock,
            }
            for p in expiring
        ],
        "high_risk_customers": high_risk,
        "alert_counts": {
            "low_stock": len(low_stock),
            "expiring_soon": len(expiring),
            "high_risk_customers": len(high_risk),
        },
    }


# =========================
# QUICK STATS
# =========================

def get_quick_stats(db: Session) -> dict:
    """Aggregate counts for the dashboard header cards."""
    total_customers = db.query(func.count(Customer.customer_id)).scalar()
    active_customers = db.query(func.count(Customer.customer_id)).filter(
        Customer.status == "active"
    ).scalar()
    total_users = db.query(func.count(User.user_id)).scalar()
    active_products = db.query(func.count(Product.product_id)).filter(
        Product.status == "active"
    ).scalar()
    pending_credit = db.query(func.count(Sale.bill_id)).filter(
        Sale.payment_method == "credit",
        Sale.status == "completed",
    ).scalar()

    return {
        "total_customers": total_customers,
        "active_customers": active_customers,
        "total_users": total_users,
        "active_products": active_products,
        "pending_credit_sales": pending_credit,
    }


# =========================
# SUMMARY (backward compat)
# =========================

def get_summary(db: Session) -> dict:
    """All-time totals for sales, expenses, and profit."""
    total_sales = db.query(func.sum(Sale.total_amount)).filter(
        Sale.status == "completed"
    ).scalar() or 0

    total_expenses = db.query(func.sum(Expense.amount)).scalar() or 0
    total_bills = db.query(func.count(Sale.bill_id)).filter(
        Sale.status == "completed"
    ).scalar()
    profit = float(total_sales) - float(total_expenses)

    return {
        "total_sales": round(float(total_sales), 2),
        "total_expenses": round(float(total_expenses), 2),
        "profit": round(profit, 2),
        "total_bills": total_bills,
    }


# =========================
# TOP PRODUCTS
# =========================

def get_top_products(db: Session, limit: int = 5) -> List[dict]:
    results = (
        db.query(
            Product.name,
            func.sum(SaleItem.quantity).label("total_sold"),
            func.sum(SaleItem.total).label("total_revenue"),
        )
        .join(SaleItem, Product.product_id == SaleItem.product_id)
        .group_by(Product.product_id, Product.name)
        .order_by(func.sum(SaleItem.quantity).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "product_name": r[0],
            "total_sold": int(r[1]),
            "total_revenue": round(float(r[2]), 2),
        }
        for r in results
    ]


# =========================
# SALES OVERVIEW (chart data)
# =========================

def get_sales_overview(db: Session, days: int = 30) -> List[dict]:
    """Daily sales totals over the past N days, suitable for charting."""
    from_date = date.today() - timedelta(days=days)

    results = (
        db.query(
            func.date(Sale.bill_date).label("sale_date"),
            func.sum(Sale.total_amount).label("total"),
            func.count(Sale.bill_id).label("orders"),
        )
        .filter(
            func.date(Sale.bill_date) >= from_date,
            Sale.status == "completed",
        )
        .group_by(func.date(Sale.bill_date))
        .order_by(func.date(Sale.bill_date).asc())
        .all()
    )

    return [
        {
            "date": str(r[0]),
            "total_sales": round(float(r[1]), 2),
            "order_count": int(r[2]),
        }
        for r in results
    ]