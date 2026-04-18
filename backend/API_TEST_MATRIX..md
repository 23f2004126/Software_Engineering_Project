# API Test Matrix

This milestone matrix is aligned to the current FastAPI backend in [`backend/app/main.py`](/c:/Users/hp/Desktop/SE/Software_Engineering_Project/backend/app/main.py) and [`backend/app/ml/router.py`](/c:/Users/hp/Desktop/SE/Software_Engineering_Project/backend/app/ml/router.py).

## Summary

- Source route definitions: `80`
- Unique method/path combinations: `78`
- Protected unique routes (`X-User-ID` required): `54`
- Public unique routes: `24`
- Smoke inventory source: [`apitest.yaml`](/c:/Users/hp/Desktop/SE/Software_Engineering_Project/backend/apitest.yaml)
- Smoke runner: [`test_all_listed_apis.py`](/c:/Users/hp/Desktop/SE/Software_Engineering_Project/backend/test_all_listed_apis.py)
- Baseline drift check: [`test_api_baaseline_matrix.py`](/c:/Users/hp/Desktop/SE/Software_Engineering_Project/backend/test_api_baaseline_matrix.py)

## Duplicate Route Note

The backend currently defines duplicate route keys for:

- `GET /api/suppliers`
- `POST /api/suppliers`

The matrix documents the effective first-seen protected definitions, and the baseline test keeps those duplicates visible so route drift is not missed during the milestone review.

## Endpoint Coverage

### System and Auth

| Method | Path | Auth | Covered In Smoke Test |
|---|---|---|---|
| GET | `/` | No | Yes |
| GET | `/health` | No | Yes |
| POST | `/api/auth/login` | No | Yes |
| POST | `/api/users/register` | No | Yes |

### Categories and Inventory

| Method | Path | Auth | Covered In Smoke Test |
|---|---|---|---|
| GET | `/api/categories` | No | Yes |
| POST | `/api/categories` | Yes | Yes |
| GET | `/api/categories/{category_id}` | No | Yes |
| PUT | `/api/categories/{category_id}` | Yes | Yes |
| DELETE | `/api/categories/{category_id}` | Yes | Yes |
| POST | `/api/inventory` | Yes | Yes |
| GET | `/api/inventory` | No | Yes |
| GET | `/api/inventory/{product_id}` | No | Yes |
| PUT | `/api/inventory/{product_id}` | Yes | Yes |
| DELETE | `/api/inventory/{product_id}` | Yes | Yes |
| POST | `/api/inventory/stock-adjustment` | Yes | Yes |
| GET | `/api/inventory/{product_id}/movements` | No | Yes |
| GET | `/api/inventory/alerts/low-stock` | No | Yes |
| GET | `/api/inventory/alerts/expiring-soon` | No | Yes |
| GET | `/api/inventory/value/total` | No | Yes |
| POST | `/api/inventory/damage-loss` | Yes | Yes |
| GET | `/api/inventory/damage-loss/report` | No | Yes |
| GET | `/api/inventory/stats/overview` | No | Yes |

### Sales

| Method | Path | Auth | Covered In Smoke Test |
|---|---|---|---|
| GET | `/api/sales/products/search` | No | Yes |
| GET | `/api/sales/products/{product_id}` | No | Yes |
| GET | `/api/sales/products/barcode/{barcode}` | No | Yes |
| GET | `/api/sales/daily/summary` | Yes | Yes |
| POST | `/api/sales` | Yes | Yes |
| GET | `/api/sales` | Yes | Yes |
| GET | `/api/sales/{bill_id}` | Yes | Yes |
| POST | `/api/sales/{bill_id}/reverse` | Yes | Yes |

### Milk Subscription

| Method | Path | Auth | Covered In Smoke Test |
|---|---|---|---|
| GET | `/api/milk/subscribers` | Yes | Yes |
| POST | `/api/milk/subscribers` | Yes | Yes |
| GET | `/api/milk/subscribers/{subscriber_id}` | Yes | Yes |
| PUT | `/api/milk/subscribers/{subscriber_id}` | Yes | Yes |
| DELETE | `/api/milk/subscribers/{subscriber_id}` | Yes | Yes |
| GET | `/api/milk/subscribers/{subscriber_id}/entries` | Yes | Yes |
| POST | `/api/milk/subscribers/{subscriber_id}/entries` | Yes | Yes |
| DELETE | `/api/milk/subscribers/{subscriber_id}/entries/{entry_id}` | Yes | Yes |

### Customers and Transactions

| Method | Path | Auth | Covered In Smoke Test |
|---|---|---|---|
| POST | `/api/customers` | Yes | Yes |
| GET | `/api/customers` | Yes | Yes |
| GET | `/api/customers/risk-assessment` | Yes | Yes |
| GET | `/api/customers/{customer_id}` | Yes | Yes |
| PUT | `/api/customers/{customer_id}` | Yes | Yes |
| PUT | `/api/customers/{customer_id}/credit-limit` | Yes | Yes |
| POST | `/api/customers/{customer_id}/payment` | Yes | Yes |
| POST | `/api/customers/{customer_id}/credit-freeze` | Yes | Yes |
| DELETE | `/api/customers/{customer_id}` | Yes | Yes |
| GET | `/api/transactions/report/credit-aging` | Yes | Yes |
| POST | `/api/transactions` | Yes | Yes |
| GET | `/api/transactions/{customer_id}` | Yes | Yes |
| PATCH | `/api/transactions/{transaction_id}/waive` | Yes | Yes |

### Suppliers and Expenses

| Method | Path | Auth | Covered In Smoke Test |
|---|---|---|---|
| POST | `/api/suppliers` | Yes | Yes |
| GET | `/api/suppliers` | Yes | Yes |
| GET | `/api/suppliers/payment-history/all` | Yes | Yes |
| GET | `/api/suppliers/{supplier_id}` | Yes | Yes |
| PUT | `/api/suppliers/{supplier_id}` | Yes | Yes |
| DELETE | `/api/suppliers/{supplier_id}` | Yes | Yes |
| GET | `/api/suppliers/{supplier_id}/pending-payments` | Yes | Yes |
| POST | `/api/suppliers/{supplier_id}/payment` | Yes | Yes |
| POST | `/api/expenses` | Yes | Yes |
| GET | `/api/expenses` | Yes | Yes |
| GET | `/api/expenses/summary` | Yes | Yes |
| GET | `/api/expenses/financial-report` | Yes | Yes |
| DELETE | `/api/expenses/{expense_id}` | Yes | Yes |

### Dashboard and Shift

| Method | Path | Auth | Covered In Smoke Test |
|---|---|---|---|
| GET | `/api/dashboard/kpis` | Yes | Yes |
| GET | `/api/dashboard/alerts` | Yes | Yes |
| GET | `/api/shifts/report` | Yes | Yes |
| GET | `/api/dashboard/quick-stats` | Yes | Yes |
| GET | `/api/dashboard/summary` | Yes | Yes |
| GET | `/api/dashboard/top-products` | Yes | Yes |
| GET | `/api/dashboard/sales-overview` | Yes | Yes |

### Payments and ML

| Method | Path | Auth | Covered In Smoke Test |
|---|---|---|---|
| POST | `/api/create-order` | No | Yes |
| POST | `/api/verify-payment` | No | Yes |
| GET | `/api/ml/sales-forecast` | No | Yes |
| GET | `/api/ml/inventory-insights` | No | Yes |
| GET | `/api/ml/cashflow-insights` | No | Yes |
| GET | `/api/ml/credit-risk` | No | Yes |
| GET | `/api/ml/all-insights` | No | Yes |

## Baseline Expectations

- CRUD and reporting endpoints are expected to return `200` in the isolated test database.
- `/api/create-order` may return `500` when Razorpay keys are not configured.
- `/api/verify-payment` may return `400` for invalid payment signatures or `500` when Razorpay keys are absent.
- `/api/ml/*` endpoints may return `500` when optional ML dependencies or runtime assumptions are not satisfied in the local environment.
