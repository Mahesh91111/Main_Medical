
from functools import lru_cache

from langchain_groq import ChatGroq

from app.core.config import settings


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    """Initialize the Groq model once per application process."""

    if not settings.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    return ChatGroq(
        model=settings.GROQ_MODEL,
        temperature=0,
        api_key=settings.GROQ_API_KEY,
        max_retries=2,
    )
