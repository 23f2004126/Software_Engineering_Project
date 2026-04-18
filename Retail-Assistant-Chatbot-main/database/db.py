import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


load_dotenv()

CHATBOT_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = CHATBOT_ROOT.parent
DEFAULT_BACKEND_DB_URL = f"sqlite:///{(PROJECT_ROOT / 'backend' / 'data' / 'storefront_v2.db').as_posix()}"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_BACKEND_DB_URL)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, future=True, connect_args=connect_args)


def execute_query(sql: str):
    """
    Execute a read-only SQL query against the shared backend database.
    Returns a list of dict rows.
    """
    statement = sql.strip()
    if not statement.upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are permitted.")

    with engine.connect() as connection:
        result = connection.execute(text(statement))
        return [dict(row) for row in result.mappings().all()]
