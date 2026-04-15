"""
Cash Flow & Expense Intelligence
Detects anomalies in daily cash flow and flags unusual expense categories.
Uses Z-score anomaly detection + Gradient Boosting for cash difference prediction.
"""
from datetime import date, timedelta
from typing import Optional
import numpy as np

from sqlalchemy import func, select
from sqlalchemy.orm import Session


def get_cashflow_insights(db: Session) -> dict:
    from app.models import Sale, Expense

    today = date.today()
    # Use last 90 days of data for analysis
    window_start = today - timedelta(days=90)

    # ── Daily sales aggregation ──────────────────────────────
    sales_rows = db.execute(
        select(
            func.date(Sale.bill_date).label("day"),
            func.sum(Sale.total_amount).label("total_sales"),
            func.sum(Sale.discount_amount).label("total_discount"),
            func.count(Sale.bill_id).label("bill_count"),
        )
        .where(Sale.bill_date >= window_start)
        .group_by(func.date(Sale.bill_date))
    ).fetchall()

    # ── Daily expense aggregation ────────────────────────────
    expense_rows = db.execute(
        select(
            Expense.expense_date.label("day"),
            func.sum(Expense.amount).label("total_expenses"),
        )
        .where(Expense.expense_date >= window_start)
        .group_by(Expense.expense_date)
    ).fetchall()

    # ── Expense by category (last 30 days) ───────────────────
    cat_rows = db.execute(
        select(
            Expense.category,
            func.sum(Expense.amount).label("total"),
            func.count(Expense.expense_id).label("count"),
        )
        .where(Expense.expense_date >= today - timedelta(days=30))
        .group_by(Expense.category)
    ).fetchall()

    # Build daily maps
    sales_map = {str(r.day): {"sales": float(r.total_sales or 0), "discount": float(r.total_discount or 0), "bills": r.bill_count} for r in sales_rows}
    expense_map = {str(r.day): float(r.total_expenses or 0) for r in expense_rows}

    all_days = sorted(set(list(sales_map.keys()) + list(expense_map.keys())))

    if len(all_days) < 7:
        return _empty_response("Not enough data for cashflow analysis (need at least 7 days)")

    daily_sales = np.array([sales_map.get(d, {}).get("sales", 0) for d in all_days])
    daily_expenses = np.array([expense_map.get(d, 0) for d in all_days])
    net_cash = daily_sales - daily_expenses

    # ── Z-score anomaly detection ────────────────────────────
    mean_net = np.mean(net_cash)
    std_net = np.std(net_cash) if np.std(net_cash) > 0 else 1
    z_scores = (net_cash - mean_net) / std_net

    anomaly_days = []
    for i, z in enumerate(z_scores):
        if abs(z) > 2.0:
            anomaly_days.append({
                "date": all_days[i],
                "net_cash": round(float(net_cash[i]), 2),
                "z_score": round(float(z), 2),
                "direction": "surplus" if z > 0 else "deficit",
            })

    # ── Expense category analysis ────────────────────────────
    category_insights = []
    if cat_rows:
        cat_amounts = [float(r.total) for r in cat_rows]
        cat_mean = np.mean(cat_amounts)
        cat_std = np.std(cat_amounts) if np.std(cat_amounts) > 0 else 1
        for r in cat_rows:
            amt = float(r.total)
            z = (amt - cat_mean) / cat_std
            if z > 1.5:
                category_insights.append({
                    "category": r.category,
                    "total": round(amt, 2),
                    "z_score": round(float(z), 2),
                    "flag": "unusually_high",
                })

    # ── 7-day forecast using simple linear trend ─────────────
    if len(net_cash) >= 14:
        try:
            from sklearn.linear_model import LinearRegression
            X = np.arange(len(net_cash)).reshape(-1, 1)
            model = LinearRegression().fit(X, net_cash)
            future_X = np.arange(len(net_cash), len(net_cash) + 7).reshape(-1, 1)
            forecast = model.predict(future_X)
            predicted_trend = "positive" if forecast[-1] > forecast[0] else "negative"
            avg_forecast = round(float(np.mean(forecast)), 2)
        except Exception:
            predicted_trend = "unknown"
            avg_forecast = round(float(mean_net), 2)
    else:
        predicted_trend = "unknown"
        avg_forecast = round(float(mean_net), 2)

    # ── Summary stats ────────────────────────────────────────
    recent_7 = net_cash[-7:] if len(net_cash) >= 7 else net_cash
    avg_daily_net = round(float(np.mean(recent_7)), 2)
    total_sales_30d = round(float(np.sum(daily_sales[-30:])), 2)
    total_expenses_30d = round(float(np.sum(daily_expenses[-30:])), 2)

    insights = []

    if len(anomaly_days) > 0:
        recent_anomaly = anomaly_days[-1]
        insights.append({
            "type": "danger" if recent_anomaly["direction"] == "deficit" else "warning",
            "icon": "exclamation-triangle",
            "title": f"Cash Flow Anomaly Detected ({recent_anomaly['date']})",
            "message": f"Net cash was ₹{abs(recent_anomaly['net_cash']):,.0f} — {recent_anomaly['direction']} (Z={recent_anomaly['z_score']}). {len(anomaly_days)} anomalous days in last 90 days.",
            "linkLabel": "View Finance",
            "linkRoute": "/finance",
        })

    for cat in category_insights[:2]:
        insights.append({
            "type": "warning",
            "icon": "currency-rupee",
            "title": f"High Spend: {cat['category']}",
            "message": f"₹{cat['total']:,.0f} spent this month — unusually high compared to other categories.",
            "linkLabel": "View Expenses",
            "linkRoute": "/finance",
        })

    if predicted_trend == "negative":
        insights.append({
            "type": "warning",
            "icon": "arrow-trending-down",
            "title": "Declining Cash Flow Trend",
            "message": f"7-day forecast shows a downward trend. Avg projected net: ₹{avg_forecast:,.0f}/day.",
            "linkLabel": "View Finance",
            "linkRoute": "/finance",
        })

    return {
        "insights": insights,
        "summary": {
            "avg_daily_net_cash_7d": avg_daily_net,
            "total_sales_30d": total_sales_30d,
            "total_expenses_30d": total_expenses_30d,
            "anomaly_count_90d": len(anomaly_days),
            "predicted_trend": predicted_trend,
            "avg_forecast_daily_net": avg_forecast,
        },
        "anomaly_days": anomaly_days[-5:],
        "high_spend_categories": category_insights,
    }


def _empty_response(reason: str) -> dict:
    return {
        "insights": [],
        "summary": {"reason": reason},
        "anomaly_days": [],
        "high_spend_categories": [],
    }
