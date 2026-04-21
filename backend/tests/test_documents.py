"""
Tests for document upload endpoint.
"""
import io
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_upload_unsupported_type():
    resp = client.post(
        "/api/documents/upload",
        files={"file": ("test.csv", b"col1,col2\n1,2", "text/csv")},
    )
    assert resp.status_code == 415


@patch("routers.documents.embed_texts", return_value=[[0.1] * 384])
@patch("routers.documents.add_documents", return_value=["some-id"])
def test_upload_txt_success(mock_add, mock_embed):
    content = b"This is a test document with enough content to form at least one chunk."
    resp = client.post(
        "/api/documents/upload",
        files={"file": ("test.txt", content, "text/plain")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["document_name"] == "test.txt"
    assert data["chunk_count"] >= 1


@patch("routers.documents.list_documents")
def test_list_documents(mock_list):
    mock_list.return_value = [{"id": "abc", "name": "file.pdf", "chunk_count": 3}]
    resp = client.get("/api/documents")
    assert resp.status_code == 200
    assert len(resp.json()["documents"]) == 1
