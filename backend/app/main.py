from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.routes import user, auth, sales, inventory, customers, supplier, expenses, transactions, dashboard, categories


# Create FastAPI app with metadata
app = FastAPI(
    title="Sonik API",
    description="Backend API for Retail Management System",
    version="1.0.0",
)


# CORS Configuration 
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include Routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(sales.router)
app.include_router(inventory.router)
app.include_router(customers.router)
app.include_router(supplier.router)
app.include_router(expenses.router)
app.include_router(transactions.router)
app.include_router(dashboard.router)
app.include_router(categories.router)


@app.get("/")
def root():
    return {"message": "🚀 Sonik API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
