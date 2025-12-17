import pytest
import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "status" in data

def test_create_query():
    response = client.post(
        "/api/v1/query",
        json={"question": "Quantos produtos tem no estoque?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert isinstance(data["answer"], str)
    assert isinstance(data["sources"], list)

def test_get_queries():
    response = client.get("/api/v1/queries")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_add_documents():
    response = client.post(
        "/api/v1/add-documents",
        json={
            "texts": ["Python é uma linguagem de programação", "FastAPI é um framework web"],
            "metadatas": [{"source": "test"}, {"source": "test"}]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "count" in data
    assert data["count"] == 2

def test_document_count():
    response = client.get("/api/v1/documents/count")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert isinstance(data["count"], int)
    assert data["count"] > 0