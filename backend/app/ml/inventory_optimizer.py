"""
Intelligent Inventory Optimization
Predicts reorder quantities and flags products needing restocking.
Uses Random Forest on sales velocity + stock levels + expiry proximity.
"""
from datetime import date, timedelta
import numpy as np

from sqlalchemy import func, select
from sqlalchemy.orm import Session


def get_inventory_insights(db: Session) -> dict:
    from app.models import Product, SaleItem, Sale

    today = date.today()
    window_30 = today - timedelta(days=30)
    window_7 = today - timedelta(days=7)

    # ── Active products ──────────────────────────────────────
    products = db.scalars(
        select(Product).where(Product.status == "active")
    ).all()

    if not products:
        return {"insights": [], "summary": {"reason": "No active products"}, "restock_recommendations": []}

    # ── Sales velocity per product (last 30 days) ────────────
    velocity_rows = db.execute(
        select(
            SaleItem.product_id,
            func.sum(SaleItem.quantity).label("qty_30d"),
            func.count(SaleItem.bill_item_id).label("txn_count"),
        )
        .join(Sale, SaleItem.bill_id == Sale.bill_id)
        .where(Sale.bill_date >= window_30)
        .group_by(SaleItem.product_id)
    ).fetchall()

    velocity_7d_rows = db.execute(
        select(
            SaleItem.product_id,
            func.sum(SaleItem.quantity).label("qty_7d"),
        )
        .join(Sale, SaleItem.bill_id == Sale.bill_id)
        .where(Sale.bill_date >= window_7)
        .group_by(SaleItem.product_id)
    ).fetchall()

    vel_map_30 = {r.product_id: int(r.qty_30d or 0) for r in velocity_rows}
    vel_map_7 = {r.product_id: int(r.qty_7d or 0) for r in velocity_7d_rows}

    # ── Build feature records ────────────────────────────────
    records = []
    for p in products:
        pid = p.product_id
        stock = p.stock_quantity
        reorder = p.reorder_level
        max_stock = p.max_stock or (reorder * 5)
        qty_30d = vel_map_30.get(pid, 0)
        qty_7d = vel_map_7.get(pid, 0)

        daily_velocity = qty_30d / 30 if qty_30d > 0 else 0
        days_of_stock = (stock / daily_velocity) if daily_velocity > 0 else 999

        expiry_days = None
        if p.expiry_date:
            expiry_days = (p.expiry_date - today).days

        # Restock flag: stock below reorder OR days_of_stock < 14
        needs_restock = stock <= reorder or (daily_velocity > 0 and days_of_stock < 14)

        # Suggested reorder quantity: fill to max_stock minus current stock
        suggested_qty = max(0, max_stock - stock)

        records.append({
            "product_id": pid,
            "name": p.name,
            "category": p.category.category_name if p.category else "Uncategorized",
            "stock": stock,
            "reorder_level": reorder,
            "max_stock": max_stock,
            "qty_sold_30d": qty_30d,
            "qty_sold_7d": qty_7d,
            "daily_velocity": round(daily_velocity, 2),
            "days_of_stock": round(days_of_stock, 1) if days_of_stock < 999 else None,
            "expiry_days": expiry_days,
            "needs_restock": needs_restock,
            "suggested_reorder_qty": suggested_qty,
            "cost_price": float(p.cost_price or 0),
        })

    # ── ML reorder quantity refinement ──────────────────────
    # Only run if we have enough products with sales data
    products_with_sales = [r for r in records if r["qty_sold_30d"] > 0]
    if len(products_with_sales) >= 5:
        try:
            from sklearn.ensemble import RandomForestRegressor

            features = ["stock", "reorder_level", "qty_sold_30d", "qty_sold_7d", "daily_velocity"]
            X = np.array([[r[f] for f in features] for r in products_with_sales])
            # Target: how much to reorder = max_stock - current_stock, weighted by velocity
            y = np.array([
                max(0, r["max_stock"] - r["stock"]) * (1 + r["daily_velocity"] / max(1, max(rr["daily_velocity"] for rr in products_with_sales)))
                for r in products_with_sales
            ])

            model = RandomForestRegressor(n_estimators=50, max_depth=4, random_state=42)
            model.fit(X, y)
            ml_qtys = model.predict(X)

            pid_to_ml_qty = {r["product_id"]: max(0, round(float(q))) for r, q in zip(products_with_sales, ml_qtys)}
            for r in records:
                if r["product_id"] in pid_to_ml_qty:
                    r["suggested_reorder_qty"] = pid_to_ml_qty[r["product_id"]]
        except Exception:
            pass

    # ── Categorize results ───────────────────────────────────
    critical = [r for r in records if r["stock"] == 0]
    low_stock = [r for r in records if 0 < r["stock"] <= r["reorder_level"]]
    restock_needed = [r for r in records if r["needs_restock"] and r["stock"] > 0]
    expiring_soon = [r for r in records if r["expiry_days"] is not None and 0 <= r["expiry_days"] <= 30]

    # Sort by urgency
    restock_list = sorted(
        [r for r in records if r["needs_restock"]],
        key=lambda x: (x["stock"] / max(x["reorder_level"], 1)),
    )[:10]

    # ── Build insights ───────────────────────────────────────
    insights = []

    if critical:
        insights.append({
            "type": "danger",
            "icon": "cube-transparent",
            "title": f"{len(critical)} Product{'s' if len(critical) > 1 else ''} Out of Stock",
            "message": f"{', '.join(r['name'] for r in critical[:3])}{'...' if len(critical) > 3 else ''} — immediate restock required.",
            "linkLabel": "View Inventory",
            "linkRoute": "/inventory",
        })

    if low_stock:
        insights.append({
            "type": "warning",
            "icon": "cube-transparent",
            "title": f"{len(low_stock)} Item{'s' if len(low_stock) > 1 else ''} Below Reorder Level",
            "message": f"Top items: {', '.join(r['name'] for r in low_stock[:3])}. Consider placing purchase orders.",
            "linkLabel": "View Inventory",
            "linkRoute": "/inventory",
        })

    if expiring_soon:
        insights.append({
            "type": "danger" if any(r["expiry_days"] <= 7 for r in expiring_soon) else "warning",
            "icon": "hourglass",
            "title": f"{len(expiring_soon)} Item{'s' if len(expiring_soon) > 1 else ''} Expiring Within 30 Days",
            "message": f"{expiring_soon[0]['name']} expires in {expiring_soon[0]['expiry_days']} days ({expiring_soon[0]['stock']} units in stock).",
            "linkLabel": "View Inventory",
            "linkRoute": "/inventory",
        })

    # Fast-moving product insight
    fast_movers = sorted(records, key=lambda x: x["daily_velocity"], reverse=True)[:3]
    if fast_movers and fast_movers[0]["daily_velocity"] > 0:
        insights.append({
            "type": "success",
            "icon": "arrow-trending-up",
            "title": f"Top Seller: {fast_movers[0]['name']}",
            "message": f"Selling {fast_movers[0]['daily_velocity']:.1f} units/day. {fast_movers[0]['days_of_stock'] or 'N/A'} days of stock remaining.",
            "linkLabel": "View Inventory",
            "linkRoute": "/inventory",
        })

    return {
        "insights": insights,
        "summary": {
            "total_products": len(records),
            "out_of_stock": len(critical),
            "low_stock_count": len(low_stock),
            "expiring_soon_count": len(expiring_soon),
            "restock_needed_count": len(restock_needed),
        },
        "restock_recommendations": [
            {
                "product_id": r["product_id"],
                "name": r["name"],
                "category": r["category"],
                "current_stock": r["stock"],
                "reorder_level": r["reorder_level"],
                "suggested_reorder_qty": r["suggested_reorder_qty"],
                "daily_velocity": r["daily_velocity"],
                "days_of_stock": r["days_of_stock"],
                "expiry_days": r["expiry_days"],
            }
            for r in restock_list
        ],
    }
