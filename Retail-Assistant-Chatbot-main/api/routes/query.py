import traceback
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.sql_chatbot import handle_sql_query
from core.generic_chatbot import handle_chat_query

router = APIRouter()


class QueryRequest(BaseModel):
    query: str


class ChatRequest(BaseModel):
    query: str
    # Frontend passes back the history it received from the previous response
    history: list[dict] = []


@router.post("/sql")
def sql_endpoint(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        return handle_sql_query(request.query)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
def chat_endpoint(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        return handle_chat_query(request.query, request.history)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
