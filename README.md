# Sonik Smart Retail Management System

Sonik is a full-stack retail management application for small stores and supermarkets. It combines a Vue 3 frontend, a FastAPI backend, and an optional AI chatbot service that can answer business questions using live store data.

This repository contains three main parts:

- `backend/` - FastAPI API, SQLite database, demo seed data, ML insights, Razorpay integration
- `frontend/` - Vue 3 + Vite web app for store owners and employees
- `Retail-Assistant-Chatbot-main/` - separate FastAPI service for SQL/chat-based AI assistance

## What The App Includes

- Dashboard with KPIs, alerts, charts, and ML-based insights
- POS billing and sales history
- Inventory management with stock, expiry, and damage/loss tracking
- Customer credit tracking and payment history
- Milk subscriber management and delivery entries
- Supplier management and supplier payments
- Employee login and shift reporting
- Financial reports
- Optional AI assistant connected to the shared store database

## Project Structure

```text
Software_Engineering_Project/
|-- backend/
|-- frontend/
|-- Retail-Assistant-Chatbot-main/
|-- README.md
`-- .gitignore
```

## Tech Stack

- Frontend: Vue 3, Vite, Pinia, Vue Router, Axios, Tailwind CSS, Chart.js
- Backend: FastAPI, SQLAlchemy, SQLite, Pydantic
- ML/Analytics: NumPy, Pandas, scikit-learn
- Payments: Razorpay
- AI Assistant: FastAPI + Groq + SQL-backed context

## Prerequisites

Install these before running the project:

- Node.js 18+ and npm
- Python 3.12 recommended
- Git

## How The System Works

The frontend talks to the main backend on port `8000`.

- Frontend default URL: `http://127.0.0.1:5173`
- Backend default URL: `http://127.0.0.1:8000`
- Chatbot default URL: `http://127.0.0.1:8001`

The chatbot is a separate service. It does not own a separate app database. It reads from the same backend database by default.

## 1. Clone The Repository

```bash
git clone https://github.com/23f2004126/Software_Engineering_Project.git
cd Software_Engineering_Project
```

## 2. Backend Setup

Open a terminal in `backend/`.

### Create and activate a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install backend dependencies

```bash
pip install -r requirements.txt
```

### Create `backend/.env`

Example:

```env
DATABASE_URL=sqlite:///./data/storefront_v2.db
ADMIN_EMAIL=admin@gmail.com
ADMIN_PASSWORD=admin@123
EMPLOYEE_EMAIL=employee@gmail.com
EMPLOYEE_PASSWORD=employee@123
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

Notes:

- If `DATABASE_URL` is not changed, the backend uses `backend/data/storefront_v2.db`
- On startup, the backend creates tables and seeds demo data automatically if the database is empty
- Razorpay is optional for local development, but payment endpoints need valid keys

### Run the backend

```bash
uvicorn app.main:app --reload
```

Backend URLs:

- API root: `http://127.0.0.1:8000/`
- Health check: `http://127.0.0.1:8000/health`
- Swagger docs: `http://127.0.0.1:8000/docs`

### Demo login credentials

These are seeded automatically from `backend/.env`:

- Admin: `admin@gmail.com` / `admin@123`
- Employee: `employee@gmail.com` / `employee@123`

## 3. Frontend Setup

Open another terminal in `frontend/`.

### Install frontend dependencies

```bash
npm install
```

### Create `frontend/.env`

```env
VITE_API_URL=http://127.0.0.1:8000
VITE_CHATBOT_API_URL=http://127.0.0.1:8001
```

### Run the frontend

```bash
npm run dev
```

Frontend URL:

- App: `http://127.0.0.1:5173`

## 4. Chatbot Setup

This service is optional but required if you want the AI assistant and query-convertor features to work fully.

Open another terminal in `Retail-Assistant-Chatbot-main/`.

### Create and activate a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install chatbot dependencies

```bash
pip install -r requirements.txt
```

### Create `Retail-Assistant-Chatbot-main/.env`

```env
DATABASE_URL=sqlite:///../backend/data/storefront_v2.db
GROQ_API_KEY=your_groq_api_key
```

Notes:

- If `DATABASE_URL` is omitted, the chatbot already defaults to the backend SQLite database
- A valid `GROQ_API_KEY` is required for `/query/chat` and `/query/sql`

### Run the chatbot

```bash
uvicorn main:app --reload --port 8001
```

Chatbot URLs:

- API root: `http://127.0.0.1:8001/`
- Docs: `http://127.0.0.1:8001/docs`

## Recommended Startup Order

1. Start the backend
2. Start the chatbot
3. Start the frontend
4. Open `http://127.0.0.1:5173`

If you only want the core retail system without AI features, you can skip the chatbot service.

## Main Frontend Modules

- `/dashboard` - KPIs, charts, alerts, AI/ML insights
- `/billing` - POS and checkout
- `/sales` - sales history and sale details
- `/inventory` - product management
- `/damage-loss` - damaged stock entries
- `/credit` and `/customers` - credit and customer management
- `/milk` - milk subscribers and delivery entries
- `/suppliers` and `/purchase-orders` - supplier workflows
- `/finance` and `/reports` - financial and business reporting
- `/employees` and `/shift-report` - employee and shift management

## Important Development Notes

- The frontend automatically sends the `X-User-ID` header after login
- The backend allows frontend CORS from `localhost:5173` and `127.0.0.1:5173`
- The backend seeds demo records only when the database is empty
- The ML insights endpoints depend on the backend Python packages from `backend/requirements.txt`
- The chatbot uses a separate FastAPI server, but it reads from the shared backend database

## Optional: Seed More ML-Oriented Data

If you want richer ML insight responses, run this after the backend environment is ready:

```bash
python seed_ml_data.py
```

Run it from inside `backend/`.

## Troubleshooting

### Backend starts but login or data looks empty

- Make sure `backend/.env` is present
- Delete `backend/data/storefront_v2.db` only if you intentionally want a fresh reseed
- Restart the backend so startup seeding runs again

### `/api/ml/all-insights` fails

- Install backend dependencies again with `pip install -r backend/requirements.txt`
- Make sure the backend virtual environment is active

### Frontend cannot reach backend

- Check `frontend/.env`
- Make sure backend is running on port `8000`
- Restart Vite after changing `.env`

### Frontend cannot reach chatbot

- Check `frontend/.env` and `Retail-Assistant-Chatbot-main/.env`
- Make sure the chatbot is running on port `8001`
- Restart the frontend after env changes

### Chatbot starts but returns AI errors

- Verify `GROQ_API_KEY`
- Make sure the chatbot service can see the backend database path

## API Quick Links

- Backend docs: `http://127.0.0.1:8000/docs`
- Chatbot docs: `http://127.0.0.1:8001/docs`

## Security Note

Do not commit real secrets to git. Keep actual values for:

- `RAZORPAY_KEY_ID`
- `RAZORPAY_KEY_SECRET`
- `GROQ_API_KEY`

Use local `.env` files with placeholder values in documentation.
