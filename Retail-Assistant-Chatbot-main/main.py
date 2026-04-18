from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.query import router

app = FastAPI(
    title="Retail Assistant Chatbot API",
    description="AI-powered retail assistant using Groq (Llama3) + MySQL",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/query")

@app.get("/")
def root():
    return {"message": "Retail Assistant Chatbot is running."}
