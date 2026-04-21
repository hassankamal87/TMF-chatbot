"""
Router — POST /api/chat
"""
from fastapi import APIRouter, HTTPException

from models.schemas import ChatRequest, ChatResponse, SourceReference
from services.rag_pipeline import run_rag

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    try:
        answer, sources = run_rag(request.question)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}") from exc

    return ChatResponse(
        answer=answer,
        sources=[SourceReference(**s) for s in sources],
    )
