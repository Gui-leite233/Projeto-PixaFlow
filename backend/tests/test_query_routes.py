import pytest
import sys
import os
from fastapi.testclient import TestClient

# Adiciona o diretório raiz ao path
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
    """Testa criação de query"""
    response = client.post(
        "/api/v1/query",
        json={"question": "Quantos alfaces tem no estoque?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["answer"] is not None
