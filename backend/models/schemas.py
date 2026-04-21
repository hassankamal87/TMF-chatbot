from pydantic import BaseModel
from typing import List, Optional


# ── Chat ─────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None


class SourceReference(BaseModel):
    document_name: str
    chunk_preview: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceReference]


# ── Documents ─────────────────────────────────────────────────────────────────

class DocumentInfo(BaseModel):
    id: str
    name: str
    chunk_count: int


class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo]


# ── Settings ──────────────────────────────────────────────────────────────────

class SettingsRead(BaseModel):
    llm_base_url: str
    llm_token: str        # masked
    llm_model: str


class SettingsUpdate(BaseModel):
    llm_base_url: Optional[str] = None
    llm_token: Optional[str] = None
    llm_model: Optional[str] = None
