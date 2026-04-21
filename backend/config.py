"""
Runtime-mutable settings for the RAG chatbot.
Defaults come from .env; can be overridden via /api/settings at any time.
Changes are persisted to settings.json so they survive restarts.
"""
import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

_SETTINGS_FILE = Path(os.getenv("SETTINGS_FILE", "./settings.json"))
_CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")


def _load_persisted() -> dict:
    if _SETTINGS_FILE.exists():
        try:
            return json.loads(_SETTINGS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _build_defaults() -> dict:
    return {
        "llm_base_url": os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
        "llm_token": os.getenv("LLM_TOKEN", ""),
        "llm_model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
    }


class _Settings:
    def __init__(self):
        defaults = _build_defaults()
        persisted = _load_persisted()
        self._data: dict = {**defaults, **persisted}

    # ── getters ──────────────────────────────────────────────────────────────
    @property
    def llm_base_url(self) -> str:
        return self._data["llm_base_url"]

    @property
    def llm_token(self) -> str:
        return self._data["llm_token"]

    @property
    def llm_model(self) -> str:
        return self._data["llm_model"]

    @property
    def chroma_persist_dir(self) -> str:
        return _CHROMA_PERSIST_DIR

    # ── update ────────────────────────────────────────────────────────────────
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key in self._data and value is not None:
                self._data[key] = value
        self._persist()

    def as_dict(self, mask_token: bool = True) -> dict:
        d = dict(self._data)
        if mask_token and d.get("llm_token"):
            d["llm_token"] = d["llm_token"][:6] + "..." if len(d["llm_token"]) > 6 else "***"
        return d

    def _persist(self):
        _SETTINGS_FILE.write_text(
            json.dumps(self._data, indent=2, ensure_ascii=False), encoding="utf-8"
        )


# Singleton used across the app
settings = _Settings()
