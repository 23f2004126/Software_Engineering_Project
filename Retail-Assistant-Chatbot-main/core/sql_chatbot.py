import re
from core.llm import call_llm
from core.prompts import EMPLOYEE_STORE_ONLY_SQL_SYSTEM_PROMPT, SQL_SYSTEM_PROMPT
from database.db import execute_query

EMPLOYEE_RESTRICTED_KEYWORDS = [
    "user",
    "users",
    "employee",
    "employees",
    "staff",
    "login",
    "password",
    "profile",
    "account",
    "credential",
    "credentials",
    "email",
    "phone number",
    "designation",
    "role",
]


def _is_employee_scope(scope: str | None) -> bool:
    return (scope or "").strip().lower() == "employee_store_only"


def _is_user_related_query(query: str) -> bool:
    q = query.lower()
    return any(keyword in q for keyword in EMPLOYEE_RESTRICTED_KEYWORDS)

def clean_sql(raw: str) -> str:
    """
    Remove any markdown code fences the model may have added despite instructions.
    e.g. ```sql SELECT ... ``` → SELECT ...
    """
    raw = re.sub(r"```(?:sql)?", "", raw, flags=re.IGNORECASE)
    raw = raw.replace("```", "")
    return raw.strip()

def handle_sql_query(user_query: str, scope: str = "default") -> dict:
    """
    1. Send the user question to Groq to generate a SQL query.
    2. Clean and validate the output.
    3. Execute the SQL against MySQL.
    4. Return the generated SQL and the query result.
    """
    if _is_employee_scope(scope) and _is_user_related_query(user_query):
        return {
            "generated_sql": None,
            "result": None,
            "message": "This query converter can only help with store-related questions. User-related or employee-account questions are not allowed here."
        }

    system_prompt = EMPLOYEE_STORE_ONLY_SQL_SYSTEM_PROMPT if _is_employee_scope(scope) else SQL_SYSTEM_PROMPT
    raw_output = call_llm(system_prompt, user_query)

    # Model flagged the question as non-retail
    if "NOT_RETAIL_QUERY" in raw_output:
        return {
            "generated_sql": None,
            "result": None,
            "message": "I can only answer questions related to the retail database."
        }

    if "NOT_ALLOWED_FOR_EMPLOYEE_SCOPE" in raw_output:
        return {
            "generated_sql": None,
            "result": None,
            "message": "This query converter can only help with store-related questions. User-related or employee-account questions are not allowed here."
        }

    sql = clean_sql(raw_output)

    # Safety guard: only allow SELECT queries — no INSERT, UPDATE, DROP, etc.
    if not sql.upper().startswith("SELECT"):
        return {
            "generated_sql": sql,
            "result": None,
            "message": "Only SELECT queries are permitted for safety."
        }

    try:
        result = execute_query(sql)
        return {
            "generated_sql": sql,
            "result": result
        }
    except Exception as e:
        return {
            "generated_sql": sql,
            "result": None,
            "error": f"SQL execution failed: {str(e)}"
        }
