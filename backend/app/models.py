from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from datetime import datetime
from app.database import Base

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Query(Base):
    __tablename__ = "queries"
    
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Estoque(Base):
    __tablename__ = "estoque"
    
    id = Column(Integer, primary_key=True, index=True)
    produto = Column(String(100), nullable=False)
    quantidade = Column(Integer, nullable=False)
    unidade = Column(String(20), default="unidade")
    preco = Column(Float)
    categoria = Column(String(50))
    ultima_atualizacao = Column(DateTime, default=datetime.utcnow)

class Vendas(Base):
    __tablename__ = "vendas"
    
    id = Column(Integer, primary_key=True, index=True)
    produto = Column(String(100), nullable=False)
    quantidade = Column(Integer, nullable=False)
    valor_total = Column(Float)
    data_venda = Column(DateTime, default=datetime.utcnow)
    cliente = Column(String(100))