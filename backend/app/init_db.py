from app.database import engine, Base
from app.models import Document, Query, Estoque, Vendas
from sqlalchemy.orm import Session

def init_database():
    print("🔄 Criando tabelas...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas!")
    
    db = Session(bind=engine)
    
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