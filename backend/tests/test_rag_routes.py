import pytest
import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

client = TestClient(app)

def test_query_endpoint():
    """Testa endpoint principal de query"""
    response = client.post(
        "/api/v1/query",
        json={"question": "Quanto custa o tomate?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data

def test_sync_database():
    """Testa sincronização do banco de dados"""
    response = client.post("/api/v1/sync-database")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

def test_add_documents_valid():
    """Testa adição de documentos com dados válidos"""
    response = client.post(
        "/api/v1/add-documents",
        json={
            "texts": ["Teste de documento RAG"],
            "metadatas": [{"title": "Teste"}]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "count" in data

def test_document_count():
    """Testa contagem de documentos no sistema"""
    response = client.get("/api/v1/documents/count")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert isinstance(data["count"], int)