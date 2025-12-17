from app.database import engine, Base
from app.models import Document, Query
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime

# Modelo de Estoque
class Estoque(Base):
    __tablename__ = "estoque"
    
    id = Column(Integer, primary_key=True, index=True)
    produto = Column(String(100), nullable=False)
    quantidade = Column(Integer, nullable=False)
    unidade = Column(String(20), default="unidade")
    preco = Column(Float)
    categoria = Column(String(50))
    ultima_atualizacao = Column(DateTime, default=datetime.utcnow)

# Modelo de Vendas
class Vendas(Base):
    __tablename__ = "vendas"
    
    id = Column(Integer, primary_key=True, index=True)
    produto = Column(String(100), nullable=False)
    quantidade = Column(Integer, nullable=False)
    valor_total = Column(Float)
    data_venda = Column(DateTime, default=datetime.utcnow)
    cliente = Column(String(100))

def init_database():
    print("🔄 Criando tabelas...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas!")
    
    # Adicionar dados de exemplo
    from sqlalchemy.orm import Session
    db = Session(bind=engine)
    
    # Verifica se já tem dados
    estoque_count = db.query(Estoque).count()
    if estoque_count == 0:
        print("📝 Adicionando dados de exemplo...")
        
        produtos = [
            Estoque(produto="Alface", quantidade=50, unidade="unidade", preco=2.50, categoria="Verdura"),
            Estoque(produto="Tomate", quantidade=30, unidade="kg", preco=4.00, categoria="Legume"),
            Estoque(produto="Cenoura", quantidade=45, unidade="kg", preco=3.50, categoria="Legume"),
            Estoque(produto="Batata", quantidade=100, unidade="kg", preco=2.80, categoria="Tubérculo"),
            Estoque(produto="Cebola", quantidade=60, unidade="kg", preco=3.20, categoria="Legume"),
            Estoque(produto="Arroz", quantidade=200, unidade="kg", preco=5.50, categoria="Grão"),
            Estoque(produto="Feijão", quantidade=150, unidade="kg", preco=7.00, categoria="Grão"),
        ]
        
        vendas = [
            Vendas(produto="Alface", quantidade=5, valor_total=12.50, cliente="João Silva"),
            Vendas(produto="Tomate", quantidade=3, valor_total=12.00, cliente="Maria Santos"),
            Vendas(produto="Arroz", quantidade=10, valor_total=55.00, cliente="Pedro Costa"),
        ]
        
        db.add_all(produtos)
        db.add_all(vendas)
        db.commit()
        print("✅ Dados de exemplo adicionados!")
    
    db.close()

if __name__ == "__main__":
    init_database()