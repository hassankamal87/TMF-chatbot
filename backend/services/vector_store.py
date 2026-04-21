"""
ChromaDB vector store wrapper.
"""
import uuid
from typing import List, Dict, Any, Tuple

import chromadb
from chromadb.config import Settings as ChromaSettings

from config import settings

_client = None
_COLLECTION_NAME = "rag_documents"


def _get_collection():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _client.get_or_create_collection(
        name=_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def add_documents(
    chunks: List[str],
    embeddings: List[List[float]],
    metadatas: List[Dict[str, Any]],
) -> List[str]:
    """
    Persist chunks with their embeddings and metadata.
    Returns the list of generated IDs.
    """
    collection = _get_collection()
    ids = [str(uuid.uuid4()) for _ in chunks]
    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    return ids


def query_similar(
    embedding: List[float],
    top_k: int = 5,
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Find the top-k most similar chunks.
    Returns (documents, metadatas).
    """
    collection = _get_collection()
    results = collection.query(
        query_embeddings=[embedding],
        n_results=min(top_k, collection.count() or 1),
        include=["documents", "metadatas"],
    )
    docs = results["documents"][0] if results["documents"] else []
    metas = results["metadatas"][0] if results["metadatas"] else []
    return docs, metas


def list_documents() -> List[Dict[str, Any]]:
    """
    Return a summary of all ingested documents grouped by source file.
    """
    collection = _get_collection()
    total = collection.count()
    if total == 0:
        return []

    # Fetch everything (metadata only — no embeddings)
    all_items = collection.get(include=["metadatas"])
    metas = all_items.get("metadatas") or []

    grouped: Dict[str, Dict] = {}
    for meta in metas:
        doc_id = meta.get("document_id", "unknown")
        doc_name = meta.get("document_name", "unknown")
        if doc_id not in grouped:
            grouped[doc_id] = {"id": doc_id, "name": doc_name, "chunk_count": 0}
        grouped[doc_id]["chunk_count"] += 1

    return list(grouped.values())


def delete_document(document_id: str) -> int:
    """Delete all chunks belonging to a given document_id. Returns number deleted."""
    collection = _get_collection()
    results = collection.get(where={"document_id": document_id}, include=[])
    ids_to_delete = results.get("ids") or []
    if ids_to_delete:
        collection.delete(ids=ids_to_delete)
    return len(ids_to_delete)
