import re
from core.llm import call_llm
from core.prompts import SQL_SYSTEM_PROMPT
from database.db import execute_query

def clean_sql(raw: str) -> str:
    """
    Remove any markdown code fences the model may have added despite instructions.
    e.g. ```sql SELECT ... ``` → SELECT ...
    """
    raw = re.sub(r"```(?:sql)?", "", raw, flags=re.IGNORECASE)
    raw = raw.replace("```", "")
    return raw.strip()

def handle_sql_query(user_query: str) -> dict:
    """
    1. Send the user question to Groq to generate a SQL query.
    2. Clean and validate the output.
    3. Execute the SQL against MySQL.
    4. Return the generated SQL and the query result.
    """
    raw_output = call_llm(SQL_SYSTEM_PROMPT, user_query)

    # Model flagged the question as non-retail
    if "NOT_RETAIL_QUERY" in raw_output:
        return {
            "generated_sql": None,
            "result": None,
            "message": "I can only answer questions related to the retail database."
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
