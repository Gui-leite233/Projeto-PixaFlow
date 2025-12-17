import pytest
from app.rag_service import RAGService

@pytest.fixture
def rag_service():
    service = RAGService()
    return service

def test_add_and_query_documents(rag_service):
    # Adiciona documentos de teste
    texts = [
        "Python é uma linguagem de programação de alto nível.",
        "FastAPI é um framework web moderno para Python."
    ]
    rag_service.add_documents(texts)
    
    # Testa query
    result = rag_service.query("O que é Python?")
    
    assert "answer" in result
    assert "sources" in result
    assert len(result["sources"]) > 0
