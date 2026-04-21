"""
Tests for the chat / RAG pipeline endpoint.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app

client = TestClient(app)


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_chat_empty_question():
    resp = client.post("/api/chat", json={"question": "  "})
    assert resp.status_code == 400


@patch("routers.chat.run_rag")
def test_chat_success(mock_run_rag):
    mock_run_rag.return_value = (
        "The answer is 42.",
        [{"document_name": "test.pdf", "chunk_preview": "Some context text..."}],
    )
    resp = client.post("/api/chat", json={"question": "What is the answer?"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["answer"] == "The answer is 42."
    assert len(data["sources"]) == 1
    assert data["sources"][0]["document_name"] == "test.pdf"


@patch("routers.chat.run_rag")
def test_chat_llm_error(mock_run_rag):
    mock_run_rag.side_effect = Exception("Connection refused")
    resp = client.post("/api/chat", json={"question": "What happened?"})
    assert resp.status_code == 502
