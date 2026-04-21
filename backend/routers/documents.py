"""
Router — POST /api/documents/upload, GET /api/documents, DELETE /api/documents/{id}
"""
import io
import uuid
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter

from models.schemas import DocumentInfo, DocumentListResponse
from services.embedding_service import embed_texts
from services.vector_store import add_documents, list_documents, delete_document

router = APIRouter(prefix="/api/documents", tags=["documents"])

_ALLOWED_TYPES = {
    "application/pdf",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
_ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
)


# ── helpers ───────────────────────────────────────────────────────────────────

def _extract_text(filename: str, data: bytes) -> str:
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext == ".txt":
        return data.decode("utf-8", errors="replace")
    elif ext == ".pdf":
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    elif ext == ".docx":
        import docx
        doc = docx.Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


# ── endpoints ─────────────────────────────────────────────────────────────────

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename or "unknown"
    ext = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""

    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(_ALLOWED_EXTENSIONS)}",
        )

    raw = await file.read()
    try:
        text = _extract_text(filename, raw)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Failed to parse file: {exc}") from exc

    if not text.strip():
        raise HTTPException(status_code=422, detail="Document appears to be empty or unreadable.")

    # Chunk
    chunks: List[str] = _splitter.split_text(text)
    if not chunks:
        raise HTTPException(status_code=422, detail="No text chunks could be extracted.")

    # Embed
    try:
        embeddings = embed_texts(chunks)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {exc}") from exc

    # Build metadata
    document_id = str(uuid.uuid4())
    metadatas = [
        {
            "document_id": document_id,
            "document_name": filename,
            "chunk_index": i,
        }
        for i in range(len(chunks))
    ]

    # Store
    add_documents(chunks, embeddings, metadatas)

    return {
        "message": "Document uploaded and indexed successfully.",
        "document_id": document_id,
        "document_name": filename,
        "chunk_count": len(chunks),
    }


@router.get("", response_model=DocumentListResponse)
async def get_documents():
    docs = list_documents()
    return DocumentListResponse(documents=[DocumentInfo(**d) for d in docs])


@router.delete("/{document_id}")
async def remove_document(document_id: str):
    count = delete_document(document_id)
    if count == 0:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"message": f"Deleted {count} chunk(s) for document '{document_id}'."}
