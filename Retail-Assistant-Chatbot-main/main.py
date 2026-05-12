import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from api.routes.query import router

load_dotenv()

app = FastAPI(
    title="Retail Assistant Chatbot API",
    description="AI-powered retail assistant using Groq (Llama3) + MySQL",
    version="2.0.0"
)

frontend_urls = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
if os.getenv("FRONTEND_URL"):
    frontend_urls.append(os.getenv("FRONTEND_URL").rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_urls,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/query")

@app.get("/")
def root():
    return {"message": "Retail Assistant Chatbot is running."}
