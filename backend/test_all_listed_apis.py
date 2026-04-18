import importlib
import json
import os
import sys
import types
import uuid
from datetime import date
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent
MATRIX_PATH = ROOT / "apitest.yaml"


def _install_razorpay_stub() -> None:
    razorpay = types.ModuleType("razorpay")

    class DummyClient:
        def __init__(self, *args, **kwargs):
            self.order = types.SimpleNamespace(
                create=lambda payload: {
                    "id": "order_test_stub",
                    "amount": payload["amount"],
                    "currency": "INR",
                }
            )
            self.utility = types.SimpleNamespace(verify_payment_signature=lambda payload: True)

    class DummyErrors:
        class SignatureVerificationError(Exception):
            pass

    razorpay.Client = DummyClient
    razorpay.errors = DummyErrors
    sys.modules["razorpay"] = razorpay


def _purge_app_modules() -> None:
    for module_name in [name for name in sys.modules if name == "app" or name.startswith("app.")]:
        sys.modules.pop(module_name, None)


def _load_matrix() -> dict:
    return json.loads(MATRIX_PATH.read_text(encoding="utf-8"))


def _extract_nested(payload: dict, *paths: tuple[str, ...]):
    for path in paths:
        current = payload
        for key in path:
            if not isinstance(current, dict) or key not in current:
                current = None
                break
            current = current[key]
        if current is not None:
            return current
    return None


@pytest.fixture(scope="module")
def app_context(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("api-smoke-db")
    db_path = tmp_dir / "apitest.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"

    _install_razorpay_stub()
    _purge_app_modules()

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    db_module = importlib.import_module("app.db")
    seed_module = importlib.import_module("app.seed")
    models_module = importlib.import_module("app.models")
    main_module = importlib.import_module("app.main")

    seed_module.init_db()
    with db_module.SessionLocal() as db:
        seed_module.seed_data(db)

        admin = db.query(models_module.User).filter(models_module.User.role == "admin").first()
        category = db.query(models_module.Category).first()
        product = db.query(models_module.Product).first()
        customer = db.query(models_module.Customer).first()
        sale = db.query(models_module.Sale).first()
        subscriber = db.query(models_module.MilkSubscriber).first()
        supplier = db.query(models_module.Supplier).first()
        expense = db.query(models_module.Expense).first()

    from fastapi.testclient import TestClient

    state = {
        "admin_user_id": admin.user_id,
        "base_category_id": category.category_id,
        "category_id": category.category_id,
        "product_id": product.product_id,
        "product_barcode": product.barcode,
        "customer_id": customer.customer_id,
        "sale_id": sale.bill_id,
        "subscriber_id": subscriber.subscriber_id,
        "supplier_id": supplier.supplier_id,
        "expense_id": expense.expense_id,
        "today": date.today().isoformat(),
    }

    client = TestClient(main_module.app, raise_server_exceptions=False)
    return {"client": client, "state": state}


def _auth_headers(state: dict, requires_auth: bool) -> dict:
    if not requires_auth:
        return {}
    return {"X-User-ID": str(state["admin_user_id"])}


def _body_from_ref(body_ref: str | None, state: dict) -> dict | None:
    unique = uuid.uuid4().hex[:8]
    if body_ref is None:
        return None

    bodies = {
        "login_admin": {"email": "admin@gmail.com", "password": "admin@123"},
        "register_user": {
            "name": f"API Test User {unique}",
            "email": f"apitest_{unique}@example.com",
            "password": "StrongPass123",
            "phone": "9000000001",
            "role": "Cashier",
        },
        "category_create": {"category_name": f"API Test Category {unique}"},
        "category_update": {"category_name": f"API Updated Category {unique}"},
        "product_create": {
            "name": f"API Test Product {unique}",
            "category_id": state["base_category_id"],
            "unit": "Piece",
            "cost_price": 10.0,
            "selling_price": 15.0,
            "quantity": 25,
            "reorder_level": 5,
            "max_stock": 100,
            "expiry_date": None,
            "hsn_code": "HSN123",
            "description": "Generated during API smoke tests",
            "sku": f"SKU-{unique}",
            "barcode": f"90000{unique[:7]}",
        },
        "product_update": {
            "name": f"API Updated Product {unique}",
            "category_id": state["base_category_id"],
            "unit": "Piece",
            "cost_price": 12.0,
            "selling_price": 18.0,
            "quantity": 20,
            "reorder_level": 4,
            "max_stock": 110,
            "expiry_date": None,
            "hsn_code": "HSN999",
            "description": "Updated by smoke test",
            "sku": f"UPD-{unique}",
            "barcode": f"91000{unique[:7]}",
        },
        "stock_adjustment": {"product_id": state["product_id"], "quantity": 1, "reason": "smoke-test-adjustment"},
        "damage_loss": {
            "product_id": state["product_id"],
            "quantity": 1,
            "reason": "damaged",
            "date": state["today"],
            "notes": "smoke test damage-loss entry",
            "estimated_loss": 10.0,
        },
        "sale_create": {
            "customer_id": state["customer_id"],
            "payment_method": "cash",
            "discount_amount": 0,
            "items": [
                {
                    "product_id": state["product_id"],
                    "quantity": 1,
                    "unit_price": 55.0,
                    "discount": 0,
                    "tax_amount": 2.5,
                    "subtotal": 55.0,
                }
            ],
        },
        "milk_subscriber_create": {
            "name": f"Milk Subscriber {unique}",
            "phone": f"98{unique[:8]}",
            "quantity": 1.0,
            "frequency": "daily",
            "start_date": state["today"],
            "status": "active",
            "amount": 70.0,
            "address": "API Test Address",
            "note": "Created by smoke test",
        },
        "milk_subscriber_update": {
            "name": f"Milk Subscriber Updated {unique}",
            "phone": f"97{unique[:8]}",
            "quantity": 1.5,
            "frequency": "daily",
            "start_date": state["today"],
            "status": "active",
            "amount": 90.0,
            "address": "Updated API Test Address",
            "note": "Updated by smoke test",
        },
        "milk_entry_upsert": {
            "entry_date": state["today"],
            "quantity": 1.0,
            "temperature": 4.0,
            "quality": "A+",
            "note": "Smoke test delivery entry",
        },
        "customer_create": {
            "name": f"Customer {unique}",
            "phone": f"96{unique[:8]}",
            "email": f"customer_{unique}@example.com",
            "address": "Smoke Test Street",
            "city": "Pune",
            "credit_limit": 5000.0,
        },
        "customer_update": {
            "name": f"Customer Updated {unique}",
            "phone": f"95{unique[:8]}",
            "email": f"customer_updated_{unique}@example.com",
            "address": "Updated Smoke Test Street",
            "city": "Mumbai",
            "credit_limit": 6500.0,
        },
        "credit_limit_update": {"credit_limit": 7000.0, "reason": "smoke-test-credit-limit"},
        "customer_payment": {"amount": 100.0, "mode": "upi", "reference": f"PAY-{unique}"},
        "customer_freeze": {"reason": "smoke-test-freeze", "duration_days": 7},
        "transaction_create": {
            "customer_id": state["customer_id"],
            "amount": 250.0,
            "type": "debit",
            "sale_id": None,
            "note": "Smoke test transaction",
            "due_date": state["today"],
        },
        "supplier_create": {
            "name": f"Supplier {unique}",
            "contact_person": "API Tester",
            "phone": f"94{unique[:8]}",
            "email": f"supplier_{unique}@example.com",
            "address": "Supplier Test Address",
            "city": "Pune",
            "rating": 4.2,
            "payment_terms": 21,
            "status": "active",
        },
        "supplier_update": {
            "name": f"Supplier Updated {unique}",
            "contact_person": "API Tester Updated",
            "phone": f"93{unique[:8]}",
            "email": f"supplier_updated_{unique}@example.com",
            "address": "Updated Supplier Address",
            "city": "Mumbai",
            "rating": 4.5,
            "payment_terms": 30,
            "status": "active",
        },
        "supplier_payment": {"amount": 500.0, "mode": "bank_transfer", "po_id": 101, "cheque_no": None, "note": "Smoke test supplier payment"},
        "expense_create": {
            "title": f"Expense {unique}",
            "amount": 250.0,
            "category": "utilities",
            "note": "Smoke test expense",
            "expense_date": state["today"],
            "recurring": False,
        },
        "create_order": {"amount": 1.0, "receipt": f"rcpt_{unique}", "notes": {"source": "smoke-test"}},
        "verify_payment": {
            "razorpay_order_id": "order_test",
            "razorpay_payment_id": "pay_test",
            "razorpay_signature": "sig_test",
        },
    }
    return bodies[body_ref]


def _query_from_ref(query_ref: str | None, state: dict) -> dict | None:
    if query_ref is None:
        return None

    queries = {
        "inventory_list": {"search": "Amul"},
        "inventory_movements": {"limit": 5},
        "expiring_soon": {"days": 7},
        "sales_product_search": {"q": "Amul"},
        "sales_daily_summary": {"date": state["today"]},
        "sales_list": {"limit": 10},
        "sale_reverse": {"reason": "Smoke test reverse"},
        "milk_entries": {"month": int(state["today"][5:7]), "year": int(state["today"][:4])},
        "customers_list": {"limit": 10},
        "transactions_list": {"status": "pending"},
        "supplier_payment_history": {"supplier_id": state["supplier_id"]},
        "expenses_list": {"limit": 10},
        "expenses_summary": {"month": int(state["today"][5:7]), "year": int(state["today"][:4])},
        "financial_report": {"from_date": state["today"], "to_date": state["today"]},
        "shift_report": {"date": state["today"]},
        "top_products": {"limit": 5},
        "sales_overview": {"days": 30},
    }
    return queries[query_ref]


def _resolve_path(path_template: str, state: dict) -> str:
    resolved = path_template
    for token, state_key in {
        "{category_id}": "category_id",
        "{product_id}": "product_id",
        "{bill_id}": "sale_id",
        "{subscriber_id}": "subscriber_id",
        "{entry_id}": "entry_id",
        "{customer_id}": "customer_id",
        "{transaction_id}": "transaction_id",
        "{supplier_id}": "supplier_id",
        "{expense_id}": "expense_id",
        "{barcode}": "product_barcode",
    }.items():
        if token in resolved and state_key in state:
            resolved = resolved.replace(token, str(state[state_key]))
    return resolved


def _capture_response_state(case_id: str, response_json: dict, state: dict) -> None:
    if case_id == "create_category":
        state["category_id"] = response_json["category_id"]
    elif case_id == "create_product":
        state["product_id"] = response_json["product_id"]
        state["product_barcode"] = response_json.get("barcode")
    elif case_id == "update_product":
        state["product_barcode"] = response_json.get("barcode")
    elif case_id == "create_sale":
        state["sale_id"] = response_json["bill_id"]
    elif case_id == "create_milk_subscriber":
        state["subscriber_id"] = response_json["subscriber_id"]
    elif case_id == "create_milk_entry":
        state["entry_id"] = response_json["entry_id"]
    elif case_id == "create_customer":
        state["customer_id"] = response_json["customer_id"]
    elif case_id == "create_transaction":
        state["transaction_id"] = response_json["transaction_id"]
    elif case_id == "create_supplier":
        supplier_id = _extract_nested(response_json, ("supplier_id",), ("supplier", "supplier_id"))
        state["supplier_id"] = supplier_id
    elif case_id == "create_expense":
        state["expense_id"] = response_json["expense_id"]


def test_all_listed_apis_smoke(app_context):
    matrix = _load_matrix()
    client = app_context["client"]
    state = dict(app_context["state"])
    failures = []

    for case in matrix["endpoints"]:
        method = case["method"]
        path = _resolve_path(case["path"], state)
        headers = _auth_headers(state, case["auth"])
        params = _query_from_ref(case.get("query_ref"), state)
        body = _body_from_ref(case.get("body_ref"), state)

        response = client.request(method, path, headers=headers, params=params, json=body)
        if response.status_code not in case["expected_statuses"]:
            failures.append(
                f'{case["id"]}: {method} {path} returned {response.status_code}, '
                f'expected one of {case["expected_statuses"]}, body={response.text}'
            )
            continue

        try:
            payload = response.json()
        except Exception:
            payload = None

        if response.status_code == 200 and isinstance(payload, dict):
            _capture_response_state(case["id"], payload, state)

    assert not failures, "API smoke test failures:\n" + "\n".join(failures)
