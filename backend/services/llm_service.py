"""
LLM service — wraps the openai SDK to target any OpenAI-compatible endpoint.
Settings (URL, token, model) are read on every call so UI changes take effect instantly.
"""
from typing import List, Dict

from openai import OpenAI

from config import settings


def _get_client() -> OpenAI:
    """Build a fresh client using current runtime settings."""
    return OpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_token or "no-key",
    )


def chat_completion(messages: List[Dict[str, str]]) -> str:
    """
    Send a list of messages to the configured LLM and return the response text.

    messages format: [{"role": "system"|"user"|"assistant", "content": "..."}]
    """
    client = _get_client()
    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,
        temperature=0.2,
    )
    return response.choices[0].message.content or ""
