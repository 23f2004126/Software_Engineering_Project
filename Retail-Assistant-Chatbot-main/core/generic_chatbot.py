from core.llm import call_llm_with_history
from core.prompts import GENERIC_SYSTEM_PROMPT
from database.db import execute_query

# ── TABLE ROUTING ─────────────────────────────────────────────────────────────
# Maps keyword groups → a focused DB fetch function.
# Order matters: more specific topics first.

TABLE_ROUTES = [
    {
        "keywords": ["milk deliver", "milk subscription", "milk subscriber", "subscriber", "delivery entry", "milk route"],
        "fetch": "milk_delivery"
    },
    {
        "keywords": ["credit", "outstanding", "due", "credit balance", "credit transaction", "unpaid"],
        "fetch": "credit"
    },
    {
        "keywords": ["expense", "rent", "salary", "electricity", "overhead", "operating cost"],
        "fetch": "expenses"
    },
    {
        "keywords": ["supplier", "vendor", "purchase", "supplier payment", "po "],
        "fetch": "suppliers"
    },
    {
        "keywords": ["damage", "loss", "spoil", "expired", "waste"],
        "fetch": "damage"
    },
    {
        "keywords": ["stock movement", "restock", "stock in", "stock out", "adjustment"],
        "fetch": "stock_movements"
    },
    {
        "keywords": ["stock", "inventory", "reorder", "low stock", "out of stock"],
        "fetch": "inventory"
    },
    {
        "keywords": ["customer", "buyer", "client", "risk"],
        "fetch": "customers"
    },
    {
        "keywords": ["product", "item", "selling", "top sell", "best sell", "revenue", "sales", "profit",
                     "total sale", "how many sale", "performance", "trend", "month", "daily"],
        "fetch": "sales_summary"
    },
]

# General fallback triggers — if none of the above matched but query still needs data
GENERAL_TRIGGERS = [
    "how", "what", "which", "analyse", "analyze", "show", "list", "tell me", "give me",
    "total", "count", "how many", "worst", "best", "increase", "decrease"
]


# ── FOCUSED FETCH FUNCTIONS ───────────────────────────────────────────────────

def _fetch_milk_delivery() -> str:
    subscribers = execute_query("""
        SELECT name, phone, quantity, frequency, status, amount
        FROM milk_subscribers ORDER BY status;
    """)
    deliveries = execute_query("""
        SELECT ms.name, COUNT(mde.entry_id) as deliveries,
               ROUND(SUM(mde.quantity), 2) as total_qty
        FROM milk_delivery_entries mde
        JOIN milk_subscribers ms ON mde.subscriber_id = ms.subscriber_id
        GROUP BY ms.name ORDER BY total_qty DESC;
    """)
    return f"Milk subscribers:\n{subscribers}\n\nDelivery summary per subscriber:\n{deliveries}"


def _fetch_credit() -> str:
    transactions = execute_query("""
        SELECT c.name, ct.amount, ct.type, ct.status, ct.due_date
        FROM credit_transactions ct
        JOIN customers c ON ct.customer_id = c.customer_id
        ORDER BY ct.status, ct.due_date;
    """)
    totals = execute_query("""
        SELECT status, ROUND(SUM(amount), 2) as total
        FROM credit_transactions GROUP BY status;
    """)
    high_risk = execute_query("""
        SELECT name, credit_balance, credit_limit, risk_level
        FROM customers WHERE credit_balance > 0 ORDER BY credit_balance DESC;
    """)
    return (f"Credit transactions:\n{transactions}\n\n"
            f"Credit totals by status:\n{totals}\n\n"
            f"Customers with outstanding balance:\n{high_risk}")


def _fetch_expenses() -> str:
    expenses = execute_query("""
        SELECT title, amount, category, expense_date, recurring
        FROM expenses ORDER BY expense_date DESC;
    """)
    by_category = execute_query("""
        SELECT category, ROUND(SUM(amount), 2) as total
        FROM expenses GROUP BY category ORDER BY total DESC;
    """)
    return f"All expenses:\n{expenses}\n\nExpenses by category:\n{by_category}"


def _fetch_suppliers() -> str:
    suppliers = execute_query("""
        SELECT name, contact_person, phone, city, rating, payment_terms, status
        FROM suppliers ORDER BY rating DESC;
    """)
    payments = execute_query("""
        SELECT s.name, sp.amount, sp.mode, sp.status, sp.paid_date
        FROM supplier_payments sp
        JOIN suppliers s ON sp.supplier_id = s.supplier_id
        ORDER BY sp.paid_date DESC;
    """)
    return f"Suppliers:\n{suppliers}\n\nRecent supplier payments:\n{payments}"


def _fetch_damage() -> str:
    records = execute_query("""
        SELECT p.name, dlr.quantity, dlr.reason, dlr.estimated_loss, dlr.notes, dlr.created_at
        FROM damage_loss_records dlr
        JOIN products p ON dlr.product_id = p.product_id
        ORDER BY dlr.created_at DESC;
    """)
    total_loss = execute_query("SELECT ROUND(SUM(estimated_loss), 2) as total FROM damage_loss_records;")
    return f"Damage/loss records:\n{records}\n\nTotal estimated loss: {total_loss[0]['total']}"


def _fetch_stock_movements() -> str:
    movements = execute_query("""
        SELECT p.name, sm.movement_type, sm.quantity_change, sm.notes, sm.created_at
        FROM stock_movements sm
        JOIN products p ON sm.product_id = p.product_id
        ORDER BY sm.created_at DESC LIMIT 20;
    """)
    return f"Recent stock movements:\n{movements}"


def _fetch_inventory() -> str:
    low_stock = execute_query("""
        SELECT name, stock_quantity, reorder_level, max_stock, status
        FROM products WHERE stock_quantity <= reorder_level AND status = 'active';
    """)
    all_stock = execute_query("""
        SELECT p.name, c.category_name, p.stock_quantity, p.price, p.status
        FROM products p LEFT JOIN categories c ON p.category_id = c.category_id
        ORDER BY p.stock_quantity ASC;
    """)
    return f"Low stock products:\n{low_stock}\n\nFull inventory:\n{all_stock}"


def _fetch_customers() -> str:
    customers = execute_query("""
        SELECT name, phone, city, credit_balance, credit_limit, risk_level, status
        FROM customers ORDER BY risk_level DESC, credit_balance DESC;
    """)
    return f"Customer list:\n{customers}"


def _fetch_sales_summary() -> str:
    total = execute_query("SELECT COUNT(*) as bills, ROUND(SUM(total_amount),2) as revenue FROM sales;")
    by_method = execute_query("""
        SELECT payment_method, COUNT(*) as count, ROUND(SUM(total_amount),2) as total
        FROM sales GROUP BY payment_method;
    """)
    top_products = execute_query("""
        SELECT p.name, SUM(si.quantity) as units_sold, ROUND(SUM(si.subtotal),2) as revenue
        FROM sale_items si JOIN products p ON si.product_id = p.product_id
        GROUP BY p.name ORDER BY units_sold DESC LIMIT 5;
    """)
    recent = execute_query("""
        SELECT DATE(bill_date) as date, ROUND(SUM(total_amount),2) as daily_revenue
        FROM sales GROUP BY DATE(bill_date) ORDER BY date DESC LIMIT 7;
    """)
    return (f"Sales overview: {total}\n\nBy payment method:\n{by_method}\n\n"
            f"Top 5 products:\n{top_products}\n\nLast 7 days:\n{recent}")


FETCH_MAP = {
    "milk_delivery":   _fetch_milk_delivery,
    "credit":          _fetch_credit,
    "expenses":        _fetch_expenses,
    "suppliers":       _fetch_suppliers,
    "damage":          _fetch_damage,
    "stock_movements": _fetch_stock_movements,
    "inventory":       _fetch_inventory,
    "customers":       _fetch_customers,
    "sales_summary":   _fetch_sales_summary,
}


# ── ROUTING LOGIC ─────────────────────────────────────────────────────────────

def _resolve_fetch_key(query: str) -> str | None:
    """Return the best-matching fetch key for the query, or None."""
    q = query.lower()
    for route in TABLE_ROUTES:
        if any(kw in q for kw in route["keywords"]):
            return route["fetch"]
    # fallback: if general trigger words present, use sales summary
    if any(t in q for t in GENERAL_TRIGGERS):
        return "sales_summary"
    return None


def _fetch_db_context(query: str) -> str:
    """Fetch focused DB data based on what the query is actually about."""
    key = _resolve_fetch_key(query)
    if key is None:
        return ""
    try:
        return FETCH_MAP[key]()
    except Exception as e:
        return f"(Database context unavailable: {str(e)})"


# ── MAIN HANDLER ──────────────────────────────────────────────────────────────

def handle_chat_query(user_query: str, history: list[dict] | None = None) -> dict:
    """
    Handle a business/retail question with conversation history.

    `history` is a list of prior turns:
        [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
    The frontend should pass the full history on every request.
    """
    if history is None:
        history = []

    # Fetch focused DB context for this specific query
    db_context = _fetch_db_context(user_query)

    # Build the current user message — inject DB data inline if available
    if db_context:
        current_message = (
            f"{user_query}\n\n"
            f"[Relevant live store data for your analysis — use this, not general assumptions:]\n"
            f"{db_context}"
        )
    else:
        current_message = user_query

    # Append current turn to history and send the full conversation
    full_history = history + [{"role": "user", "content": current_message}]

    answer = call_llm_with_history(GENERIC_SYSTEM_PROMPT, full_history)

    return {
        "answer": answer,
        # Return the clean history (without injected DB data) for the frontend to store
        "history": history + [
            {"role": "user",      "content": user_query},
            {"role": "assistant", "content": answer}
        ]
    }
