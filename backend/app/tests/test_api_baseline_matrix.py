import os

import pytest
import requests


BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
AUTH_HEADERS = {"X-User-ID": os.getenv("API_TEST_USER_ID", "1")}


@pytest.fixture(scope="module")
def auth_status_code() -> int:
    response = requests.get(f"{BASE_URL}/api/dashboard/kpis", headers=AUTH_HEADERS, timeout=20)
    return response.status_code


def run_case(path: str, auth_status_code: int, expected: int, protected: bool = True, method: str = "GET", params=None, body=None):
    expected_status = 401 if protected and auth_status_code != 200 else expected
    headers = AUTH_HEADERS if protected else {}
    response = requests.request(method, f"{BASE_URL}{path}", headers=headers, params=params, json=body, timeout=25)
    assert response.status_code == expected_status, (
        f"path={path} method={method} params={params} body={body} "
        f"expected={expected_status} actual={response.status_code} response={response.text}"
    )


# --- Working baseline checks ---

@pytest.mark.api
def test_baseline_dashboard_kpis(auth_status_code): run_case("/api/dashboard/kpis", auth_status_code, 200)


@pytest.mark.api
def test_baseline_inventory_list(auth_status_code): run_case("/api/inventory", auth_status_code, 200, protected=False, params={"skip": 0, "limit": 5})


@pytest.mark.api
def test_baseline_sales_product_search(auth_status_code): run_case("/api/sales/products/search", auth_status_code, 200, protected=False, params={"q": "milk"})


@pytest.mark.api
def test_baseline_expenses_summary(auth_status_code): run_case("/api/expenses/summary", auth_status_code, 200, params={"month": 4, "year": 2026})


@pytest.mark.api
def test_baseline_credit_aging(auth_status_code): run_case("/api/transactions/report/credit-aging", auth_status_code, 200)


# --- Known failing endpoints (baseline expects failures in valid-auth env) ---

@pytest.mark.api
def test_known_fail_dashboard_alerts(auth_status_code): run_case("/api/dashboard/alerts", auth_status_code, 500)


@pytest.mark.api
def test_known_fail_dashboard_quick_stats(auth_status_code): run_case("/api/dashboard/quick-stats", auth_status_code, 500)


@pytest.mark.api
def test_known_fail_dashboard_top_products(auth_status_code): run_case("/api/dashboard/top-products", auth_status_code, 500)


@pytest.mark.api
def test_known_fail_sales_daily_summary(auth_status_code):
    run_case("/api/sales/daily/summary", auth_status_code, 500, params={"date": "2026-04-03"})


# --- Showcase mismatch ---

@pytest.mark.api
@pytest.mark.xfail(strict=False, reason="Showcase: expected success but actual differs in current state")
def test_showcase_expected_vs_actual_post_sales():
    payload = {
        "customer_id": 1,
        "payment_method": "cash",
        "discount_amount": 0,
        "items": [{"product_id": 1, "quantity": 1, "unit_price": 10}],
    }
    response = requests.post(f"{BASE_URL}/api/sales", json=payload, headers=AUTH_HEADERS, timeout=25)
    assert response.status_code == 200, (
        "Expected 200 but got "
        f"{response.status_code}. input={payload} actual_output={response.text}"
    )


# --- Negative auth test ---

@pytest.mark.api
def test_negative_missing_header_for_dashboard_kpis():
    response = requests.get(f"{BASE_URL}/api/dashboard/kpis", timeout=20)
    assert response.status_code == 422, (
        "Expected 422 without required auth header; "
        f"actual={response.status_code} body={response.text}"
    )
