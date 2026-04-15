"""
Sales Forecasting
Predicts next 7 days of total daily revenue using lag features + seasonality.
Uses Gradient Boosting trained on historical daily sales from the live DB.
"""
from datetime import date, timedelta
import numpy as np

from sqlalchemy import func, select
from sqlalchemy.orm import Session


def get_sales_forecast(db: Session) -> dict:
    from app.models import Sale, SaleItem, Product

    today = date.today()
    # Need at least 60 days of history for meaningful lag features
    window_start = today - timedelta(days=120)

    # ── Daily revenue aggregation ────────────────────────────
    rows = db.execute(
        select(
            func.date(Sale.bill_date).label("day"),
            func.sum(Sale.total_amount).label("revenue"),
            func.count(Sale.bill_id).label("bill_count"),
            func.sum(Sale.discount_amount).label("discounts"),
        )
        .where(Sale.bill_date >= window_start)
        .group_by(func.date(Sale.bill_date))
        .order_by(func.date(Sale.bill_date))
    ).fetchall()

    if len(rows) < 14:
        return _empty_response("Not enough sales history for forecasting (need at least 14 days)")

    dates = [str(r.day) for r in rows]
    revenues = np.array([float(r.revenue or 0) for r in rows])
    bill_counts = np.array([int(r.bill_count or 0) for r in rows])

    # ── Feature engineering ──────────────────────────────────
    from datetime import datetime

    def make_features(date_str, rev_series, idx):
        d = datetime.strptime(date_str, "%Y-%m-%d")
        lag1 = rev_series[idx - 1] if idx >= 1 else 0
        lag7 = rev_series[idx - 7] if idx >= 7 else 0
        lag14 = rev_series[idx - 14] if idx >= 14 else 0
        rolling7 = np.mean(rev_series[max(0, idx - 7):idx]) if idx > 0 else 0
        rolling14 = np.mean(rev_series[max(0, idx - 14):idx]) if idx > 0 else 0
        return [
            d.weekday(),           # day of week (0=Mon)
            d.month,               # month
            int(d.weekday() >= 5), # is_weekend
            lag1,
            lag7,
            lag14,
            rolling7,
            rolling14,
        ]

    # Build training set (skip first 14 rows — not enough lag history)
    X, y = [], []
    for i in range(14, len(revenues)):
        X.append(make_features(dates[i], revenues, i))
        y.append(revenues[i])

    if len(X) < 5:
        return _empty_response("Insufficient data after feature engineering")

    X = np.array(X)
    y = np.array(y)

    # ── Train model ──────────────────────────────────────────
    try:
        from sklearn.ensemble import GradientBoostingRegressor
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_absolute_error

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        model = GradientBoostingRegressor(n_estimators=100, max_depth=3, learning_rate=0.1, random_state=42)
        model.fit(X_train, y_train)

        mae = mean_absolute_error(y_test, model.predict(X_test)) if len(X_test) > 0 else None

        # ── Forecast next 7 days ─────────────────────────────
        forecast_revenues = list(revenues.copy())
        forecast_dates = []
        forecast_values = []

        for offset in range(1, 8):
            future_date = today + timedelta(days=offset)
            future_date_str = future_date.strftime("%Y-%m-%d")
            idx = len(forecast_revenues)
            feats = make_features(future_date_str, np.array(forecast_revenues), idx)
            pred = max(0, float(model.predict([feats])[0]))
            forecast_revenues.append(pred)
            forecast_dates.append(future_date_str)
            forecast_values.append(round(pred, 2))

    except Exception as e:
        # Fallback: 7-day rolling average
        avg = float(np.mean(revenues[-7:]))
        forecast_dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 8)]
        forecast_values = [round(avg, 2)] * 7
        mae = None

    # ── Historical trend ─────────────────────────────────────
    last_7_avg = round(float(np.mean(revenues[-7:])), 2)
    prev_7_avg = round(float(np.mean(revenues[-14:-7])), 2) if len(revenues) >= 14 else last_7_avg
    trend_pct = round(((last_7_avg - prev_7_avg) / max(prev_7_avg, 1)) * 100, 1)

    # ── Best/worst day prediction ────────────────────────────
    best_day_idx = int(np.argmax(forecast_values))
    worst_day_idx = int(np.argmin(forecast_values))

    # ── Build insights ───────────────────────────────────────
    insights = []

    total_forecast = sum(forecast_values)
    insights.append({
        "type": "success" if trend_pct >= 0 else "warning",
        "icon": "arrow-trending-up" if trend_pct >= 0 else "arrow-trending-down",
        "title": f"7-Day Revenue Forecast: ₹{total_forecast:,.0f}",
        "message": f"Avg ₹{round(total_forecast/7):,}/day. Trend: {'▲' if trend_pct >= 0 else '▼'} {abs(trend_pct)}% vs previous week.",
        "linkLabel": "View Reports",
        "linkRoute": "/reports",
    })

    insights.append({
        "type": "info",
        "icon": "calendar",
        "title": f"Peak Day: {forecast_dates[best_day_idx]}",
        "message": f"Projected revenue ₹{forecast_values[best_day_idx]:,.0f}. Stock up before this day.",
        "linkLabel": "View Inventory",
        "linkRoute": "/inventory",
    })

    return {
        "insights": insights,
        "summary": {
            "last_7d_avg_revenue": last_7_avg,
            "prev_7d_avg_revenue": prev_7_avg,
            "trend_pct": trend_pct,
            "forecast_total_7d": round(total_forecast, 2),
            "model_mae": round(mae, 2) if mae else None,
        },
        "forecast": [
            {"date": d, "predicted_revenue": v}
            for d, v in zip(forecast_dates, forecast_values)
        ],
    }


def _empty_response(reason: str) -> dict:
    return {
        "insights": [],
        "summary": {"reason": reason},
        "forecast": [],
    }
