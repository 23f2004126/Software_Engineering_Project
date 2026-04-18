# Retail Assistant Chatbot

An AI-powered retail business assistant built with FastAPI + Groq (Llama 3). It exposes two endpoints:

- `/query/sql` - converts natural language into SQL queries and returns live data
- `/query/chat` - a conversational business advisor with memory, backed by live store data

---

## Project Structure

```text
Retail-Assistant-Chatbot/
|-- api/
|   `-- routes/
|       `-- query.py          # FastAPI route handlers
|-- core/
|   |-- llm.py                # Groq client, single-turn + multi-turn calls
|   |-- prompts.py            # System prompts for both chatbots
|   |-- sql_chatbot.py        # NL -> SQL pipeline
|   `-- generic_chatbot.py    # Conversational chatbot with table routing + history
|-- database/
|   `-- db.py                 # Shared backend DB connection + read-only query executor
|-- main.py                   # FastAPI app entry point
|-- requirements.txt
|-- .env                      # API key + DATABASE_URL (not committed)
`-- .gitignore
```

---

## Setup

**1. Install dependencies**

```bash
pip install -r requirements.txt
```

**2. Configure environment**

Create a `.env` file in the project root:

```env
DATABASE_URL=sqlite:///../backend/data/storefront_v2.db
GROQ_API_KEY=your_groq_api_key_here
```

Get a free Groq API key at https://console.groq.com

If `DATABASE_URL` is not set, the chatbot defaults to the backend database at `../backend/data/storefront_v2.db`.
The chatbot does not maintain a separate app database; it reads from the shared backend database.

**3. Start the server**

```bash
uvicorn main:app --reload
```

API is now live at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

---

## API Reference

### POST `/query/sql`

Converts a natural language question into a SQL query and returns the result.

**Request**

```json
{ "query": "Which products have low stock?" }
```

**Response**

```json
{
  "generated_sql": "SELECT name, stock_quantity FROM products WHERE stock_quantity <= reorder_level;",
  "result": []
}
```

### POST `/query/chat`

Conversational business advisor. Accepts conversation history for multi-turn dialogue.

**Request**

```json
{
  "query": "How are our milk subscribers doing?",
  "history": []
}
```

**Response**

```json
{
  "answer": "You have 4 active milk subscribers...",
  "history": [
    { "role": "user", "content": "How are our milk subscribers doing?" },
    { "role": "assistant", "content": "You have 4 active milk subscribers..." }
  ]
}
```

On the next turn, pass back the `history` array you received. The backend is stateless and the frontend owns the conversation history.
