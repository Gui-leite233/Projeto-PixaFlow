import pytest
import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

client = TestClient(app)

def test_health_check():
    """Testa endpoint de health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_root():
    """Testa endpoint raiz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "status" in data

def test_create_query():
    """Testa criação de query com RAG"""
    response = client.post(
        "/api/v1/query",
        json={"question": "O que é Python?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert data["answer"] is not None

def test_get_queries():
    """Testa listagem de queries"""
    response = client.get("/api/v1/queries")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_add_documents():
    """Testa adição de documentos"""
    response = client.post(
        "/api/v1/add-documents",
        json={
            "texts": ["Teste de documento para RAG"],
            "metadatas": None
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["count"] == 1

def test_document_count():
    """Testa contagem de documentos"""
    response = client.get("/api/v1/documents/count")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert isinstance(data["count"], int)