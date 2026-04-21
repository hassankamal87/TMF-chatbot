"""
RAG pipeline — ties together retrieval (ChromaDB) and generation (LLM).
"""
from typing import List, Tuple, Dict, Any

from services.embedding_service import embed_query
from services.vector_store import query_similar
from services.llm_service import chat_completion

_SYSTEM_PROMPT = """You are a helpful assistant that answers questions strictly based on the provided context documents.
If the answer cannot be found in the context, say so clearly.
Always be concise and accurate."""


def _build_context(chunks: List[str]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(f"[Context {i}]\n{chunk}")
    return "\n\n".join(parts)


def run_rag(question: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Full RAG pipeline:
      1. Embed the question.
      2. Retrieve top-k relevant chunks from ChromaDB.
      3. Build a prompt and call the LLM.
      4. Return (answer, source_metadata_list).
    """
    # 1. Embed query
    query_embedding = embed_query(question)

    # 2. Retrieve
    chunks, metas = query_similar(query_embedding, top_k=5)

    if not chunks:
        return (
            "I don't have any documents to search through yet. "
            "Please upload some documents first.",
            [],
        )

    # 3. Build messages
    context_text = _build_context(chunks)
    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Context:\n{context_text}\n\n"
                f"Question: {question}\n\n"
                "Answer based only on the context above."
            ),
        },
    ]

    # 4. Generate
    answer = chat_completion(messages)

    # Build source references with dedup
    seen = set()
    sources = []
    for chunk, meta in zip(chunks, metas):
        doc_name = meta.get("document_name", "unknown")
        if doc_name not in seen:
            seen.add(doc_name)
            sources.append(
                {
                    "document_name": doc_name,
                    "chunk_preview": chunk[:200] + ("…" if len(chunk) > 200 else ""),
                }
            )

    return answer, sources
