"""
Customer Analytics & Credit Risk
Classifies customers into risk segments using RFM features + credit behavior.
Uses Gradient Boosting classifier trained on-demand from live DB data.
"""
from datetime import date, timedelta
import numpy as np

from sqlalchemy import func, select
from sqlalchemy.orm import Session


def get_credit_risk_insights(db: Session) -> dict:
    from app.models import Customer, CreditTransaction, Sale

    today = date.today()

    customers = db.scalars(
        select(Customer).where(Customer.status == "active", Customer.credit_limit > 0)
    ).all()

    if not customers:
        return {"insights": [], "summary": {"reason": "No active credit customers found"}, "high_risk": [], "segments": {}}

    # ── Build feature matrix ─────────────────────────────────
    records = []
    for c in customers:
        cid = c.customer_id
        limit = float(c.credit_limit or 1)
        balance = float(c.credit_balance or 0)
        utilization = min(balance / limit, 1.0)

        # Credit transactions
        txns = db.scalars(
            select(CreditTransaction).where(CreditTransaction.customer_id == cid)
        ).all()

        debit_txns = [t for t in txns if t.type == "debit"]
        total_debits = sum(float(t.amount) for t in debit_txns)
        overdue_count = sum(
            1 for t in debit_txns
            if t.status == "pending" and t.due_date and t.due_date < today
        )
        overdue_amount = sum(
            float(t.amount) for t in debit_txns
            if t.status == "pending" and t.due_date and t.due_date < today
        )
        n_credits = len(txns)

        # Sales recency
        last_sale = db.scalar(
            select(func.max(Sale.bill_date)).where(Sale.customer_id == cid)
        )
        recency_days = (today - last_sale.date()).days if last_sale else 999

        records.append({
            "customer_id": cid,
            "name": c.name,
            "phone": c.phone,
            "credit_limit": limit,
            "credit_balance": balance,
            "utilization": utilization,
            "total_debits": total_debits,
            "overdue_count": overdue_count,
            "overdue_amount": overdue_amount,
            "n_transactions": n_credits,
            "recency_days": recency_days,
        })

    if not records:
        return {"insights": [], "summary": {"reason": "No data available"}, "high_risk": [], "segments": {}}

    # ── Rule-based risk scoring (0-100) ─────────────────────
    # Weighted: utilization 40%, overdue 40%, recency 20%
    scored = []
    for r in records:
        util_score = r["utilization"] * 40
        overdue_score = min(r["overdue_count"] * 10, 40)
        recency_score = min(r["recency_days"] / 365 * 20, 20)
        risk_score = util_score + overdue_score + recency_score

        if risk_score >= 60:
            risk_label = "high"
        elif risk_score >= 30:
            risk_label = "medium"
        else:
            risk_label = "low"

        scored.append({**r, "risk_score": round(risk_score, 1), "risk_label": risk_label})

    # ── ML enhancement if enough data ───────────────────────
    if len(scored) >= 10:
        try:
            from sklearn.ensemble import GradientBoostingClassifier
            from sklearn.preprocessing import LabelEncoder

            features = ["utilization", "overdue_count", "recency_days", "n_transactions"]
            X = np.array([[r[f] for f in features] for r in scored])
            # Use rule-based labels as training signal
            le = LabelEncoder()
            y = le.fit_transform([r["risk_label"] for r in scored])

            model = GradientBoostingClassifier(n_estimators=50, max_depth=3, random_state=42)
            model.fit(X, y)
            ml_labels = le.inverse_transform(model.predict(X))

            for i, r in enumerate(scored):
                r["risk_label"] = ml_labels[i]
        except Exception:
            pass  # fall back to rule-based if sklearn fails

    # ── Segment counts ───────────────────────────────────────
    segments = {"high": 0, "medium": 0, "low": 0}
    for r in scored:
        segments[r["risk_label"]] = segments.get(r["risk_label"], 0) + 1

    high_risk = sorted(
        [r for r in scored if r["risk_label"] == "high"],
        key=lambda x: x["risk_score"],
        reverse=True,
    )[:5]

    total_outstanding = sum(r["credit_balance"] for r in scored)
    total_overdue_amt = sum(r["overdue_amount"] for r in scored)

    # ── Build insights ───────────────────────────────────────
    insights = []

    if segments["high"] > 0:
        insights.append({
            "type": "danger",
            "icon": "exclamation-triangle",
            "title": f"{segments['high']} High-Risk Credit Customer{'s' if segments['high'] > 1 else ''}",
            "message": f"₹{total_overdue_amt:,.0f} overdue across {segments['high']} customers. Immediate follow-up recommended.",
            "linkLabel": "View Customers",
            "linkRoute": "/customers",
        })

    if total_outstanding > 0:
        insights.append({
            "type": "warning" if total_outstanding > 50000 else "info",
            "icon": "document-text",
            "title": f"₹{total_outstanding:,.0f} Total Outstanding Credit",
            "message": f"{segments['medium']} medium-risk and {segments['high']} high-risk customers hold this balance.",
            "linkLabel": "Credit Report",
            "linkRoute": "/credit",
        })

    return {
        "insights": insights,
        "summary": {
            "total_credit_customers": len(scored),
            "high_risk_count": segments["high"],
            "medium_risk_count": segments["medium"],
            "low_risk_count": segments["low"],
            "total_outstanding": round(total_outstanding, 2),
            "total_overdue_amount": round(total_overdue_amt, 2),
        },
        "high_risk_customers": [
            {
                "customer_id": r["customer_id"],
                "name": r["name"],
                "phone": r["phone"],
                "credit_balance": round(r["credit_balance"], 2),
                "credit_limit": round(r["credit_limit"], 2),
                "utilization_pct": round(r["utilization"] * 100, 1),
                "overdue_count": r["overdue_count"],
                "overdue_amount": round(r["overdue_amount"], 2),
                "risk_score": r["risk_score"],
            }
            for r in high_risk
        ],
        "segments": segments,
    }
