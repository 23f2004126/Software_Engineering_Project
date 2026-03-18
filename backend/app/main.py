from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import user, auth


# ✅ Create FastAPI app with metadata
app = FastAPI(
    title="Sonik API",
    description="Backend API for Retail Management System",
    version="1.0.0"
)


# ✅ CORS Configuration (VERY IMPORTANT)
origins = [
    "http://localhost:5173",   # Vue (Vite)
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # or ["*"] for testing
    allow_credentials=True,
    allow_methods=["*"],          # allow all methods (POST, GET, OPTIONS...)
    allow_headers=["*"],          # allow all headers
)


# ✅ Include Routers
app.include_router(auth.router)
app.include_router(user.router)


# ✅ Root route (health check)
@app.get("/")
def root():
    return {"message": "🚀 Sonik API is running"}


# ✅ Optional: Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}