import pytest
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.sql_ai_service import SQLAIService

def test_sql_ai_initialization():
    """Testa inicialização do serviço"""
    service = SQLAIService()
    assert service is not None

def test_query_estoque():
    """Testa consulta de estoque"""
    service = SQLAIService()
    result = service.process_query("Quantos alfaces tem no estoque?")
    
    assert "answer" in result
    assert result["answer"] is not None
    assert "sql" in result

def test_question_to_sql():
    """Testa conversão de pergunta para SQL"""
    service = SQLAIService()
    
    # Teste pergunta sobre quantidade
    sql = service._question_to_sql("Quantos alfaces tem no estoque?")
    assert sql is not None
    assert "SELECT" in sql.upper()
    assert "estoque" in sql.lower()
    
    # Teste pergunta sobre vendas
    sql = service._question_to_sql("Qual o total de vendas?")
    assert sql is not None
    assert "vendas" in sql.lower()
