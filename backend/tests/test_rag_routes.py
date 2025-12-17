import pytest
import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

client = TestClient(app)

def test_rag_query():
    """Testa consulta RAG"""
    response = client.post(
        "/api/v1/rag-query",
        json={"question": "O que é Python?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert data["type"] == "rag"

def test_hybrid_query_auto():
    """Testa consulta híbrida modo auto"""
    response = client.post(
        "/api/v1/hybrid-query",
        json={"question": "Quantos produtos tem?", "mode": "auto"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "type" in data

def test_add_documents():
    """Testa adição de documentos"""
    response = client.post(
        "/api/v1/add-documents",
        json={
            "texts": ["Teste de documento para RAG"],
            "metadatas": [{"title": "Teste"}]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

def test_query_stats():
    """Testa estatísticas de queries"""
    response = client.get("/api/v1/query-stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_queries" in data
    assert "recent_queries" in data