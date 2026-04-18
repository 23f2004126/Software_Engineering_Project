import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama-3.1-8b-instant"

# Max turns of history to keep (each turn = 1 user + 1 assistant message)
MAX_HISTORY_TURNS = 10

def call_llm(system_prompt: str, user_message: str) -> str:
    """Single-turn call — used by the SQL chatbot."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message}
        ],
        temperature=0,
        max_tokens=512,
    )
    return response.choices[0].message.content.strip()


def call_llm_with_history(system_prompt: str, history: list[dict]) -> str:
    """
    Multi-turn call — used by the generic chatbot.
    `history` is a list of {"role": "user"|"assistant", "content": "..."} dicts.
    The last item must be the current user message (already appended by the caller).
    History is trimmed to MAX_HISTORY_TURNS to stay within context limits.
    """
    # Keep only the most recent N turns (2 messages per turn)
    trimmed = history[-(MAX_HISTORY_TURNS * 2):]

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system_prompt}] + trimmed,
        temperature=0.3,   # slight creativity for conversational replies
        max_tokens=600,
    )
    return response.choices[0].message.content.strip()
