import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from app.config import settings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

class RAGService:
    def __init__(self):
        try:
            print("Inicializando RAG Service...")
            
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            
            self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
            
            try:
                self.collection = self.chroma_client.get_collection("documents")
            except:
                self.collection = self.chroma_client.create_collection("documents")
            
            self.vectorstore = Chroma(
                client=self.chroma_client,
                collection_name="documents",
                embedding_function=self.embeddings
            )
            
            DATABASE_URL = f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
            self.engine = create_engine(DATABASE_URL)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            self._sync_database_to_rag()
            
            print("✅ RAG Service inicializado com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar RAG: {e}")
            raise
    
    def _sync_database_to_rag(self):
        try:
            db = self.SessionLocal()
            
            try:
                all_items = self.collection.get()
                ids_to_delete = []
                
                for i, metadata in enumerate(all_items['metadatas']):
                    if metadata and metadata.get('source') in ['estoque', 'vendas']:
                        ids_to_delete.append(all_items['ids'][i])
                
                if ids_to_delete:
                    self.collection.delete(ids=ids_to_delete)
            except Exception as e:
                print(f"⚠️  Aviso ao limpar: {e}")
            
            estoque_query = text("SELECT * FROM estoque")
            estoque_result = db.execute(estoque_query)
            estoque_rows = estoque_result.fetchall()
            
            if not estoque_rows:
                print("⚠️  AVISO: Tabela estoque está VAZIA!")
            
            texts_to_add = []
            metadatas_to_add = []
            ids_to_add = []
            
            for row in estoque_rows:
                base_id = f"estoque_{row.id}"
                
                doc_text = (
                    f"Produto: {row.produto}. "
                    f"Temos {row.quantidade} {row.unidade} em estoque. "
                    f"Preço: R$ {row.preco:.2f} por {row.unidade}. "
                    f"Categoria: {row.categoria}."
                )
                texts_to_add.append(doc_text)
                metadatas_to_add.append({
                    "source": "estoque",
                    "produto": row.produto,
                    "quantidade": row.quantidade,
                    "preco": float(row.preco),
                    "categoria": row.categoria,
                    "id": row.id
                })
                ids_to_add.append(f"{base_id}_1")
                
                doc_text2 = f"Quantidade de {row.produto} disponível: {row.quantidade} {row.unidade}"
                texts_to_add.append(doc_text2)
                metadatas_to_add.append({
                    "source": "estoque",
                    "produto": row.produto,
                    "quantidade": row.quantidade,
                    "preco": float(row.preco),
                    "categoria": row.categoria,
                    "id": row.id
                })
                ids_to_add.append(f"{base_id}_2")
                
                doc_text3 = f"Preço do {row.produto}: R$ {row.preco:.2f}"
                texts_to_add.append(doc_text3)
                metadatas_to_add.append({
                    "source": "estoque",
                    "produto": row.produto,
                    "quantidade": row.quantidade,
                    "preco": float(row.preco),
                    "categoria": row.categoria,
                    "id": row.id
                })
                ids_to_add.append(f"{base_id}_3")
            
            vendas_query = text("SELECT * FROM vendas ORDER BY data_venda DESC LIMIT 20")
            vendas_result = db.execute(vendas_query)
            vendas_rows = vendas_result.fetchall()
            
            if not vendas_rows:
                print("⚠️  AVISO: Tabela vendas está VAZIA!")
            
            for row in vendas_rows:
                venda_text = (
                    f"Venda: {row.quantidade} unidades de {row.produto} "
                    f"para {row.cliente}. "
                    f"Valor: R$ {row.valor_total:.2f}. "
                    f"Data: {row.data_venda}."
                )
                texts_to_add.append(venda_text)
                metadatas_to_add.append({
                    "source": "vendas",
                    "produto": row.produto,
                    "cliente": row.cliente,
                    "valor": float(row.valor_total),
                    "quantidade": row.quantidade,
                    "id": row.id
                })
                ids_to_add.append(f"vendas_{row.id}")
            
            db.close()
            
            if texts_to_add:
                self.collection.add(
                    documents=texts_to_add,
                    metadatas=metadatas_to_add,
                    ids=ids_to_add
                )
                print(f"✅ {len(estoque_rows)} produtos (com {len([m for m in metadatas_to_add if m['source']=='estoque'])} variações)")
                print(f"✅ {len(vendas_rows)} vendas sincronizadas")
                print(f"📊 Total no ChromaDB: {self.collection.count()} documentos")
            else:
                print("❌ ERRO: Nenhum dado foi sincronizado!")
                
        except Exception as e:
            print(f"❌ ERRO ao sincronizar banco: {e}")
            import traceback
            traceback.print_exc()
    
    
    
    def sync_database(self):
        self._sync_database_to_rag()
        return {"message": "Banco de dados sincronizado com sucesso!"}
    
    def add_documents(self, texts: list[str], metadatas: list[dict] = None):
        try:
            self.vectorstore.add_texts(texts=texts, metadatas=metadatas)
            print(f"✅ {len(texts)} documento(s) adicionado(s)")
            return True
        except Exception as e:
            print(f"❌ Erro ao adicionar documentos: {e}")
            return False
    
    def query(self, question: str, k: int = 5):
        try:
            print(f"🔍 Processando query: {question}")
            
            docs = self.vectorstore.similarity_search(question, k=k)
            
            if not docs:
                return {
                    "answer": "Não encontrei informações relevantes para responder sua pergunta. Tente adicionar mais documentos ao sistema.",
                    "sources": []
                }
            
            answer = self._generate_answer(question, docs)
            sources = [doc.page_content for doc in docs]
            
            print(f"✅ Resposta gerada com {len(sources)} fontes")
            
            return {
                "answer": answer,
                "sources": sources,
                "metadata": [doc.metadata for doc in docs]
            }
            
        except Exception as e:
            print(f"❌ Erro na query: {e}")
            return {
                "answer": f"Desculpe, ocorreu um erro ao processar sua consulta: {str(e)}",
                "sources": []
            }
    
    def _generate_answer(self, question: str, docs: list):
        
        if not docs:
            return "Não encontrei informações relevantes."
        
        question_lower = question.lower()
        
        estoque_docs = [d for d in docs if d.metadata.get("source") == "estoque"]
        vendas_docs = [d for d in docs if d.metadata.get("source") == "vendas"]
        
        # Debug
        print(f"🔍 Análise:")
        print(f"   Estoque encontrado: {len(estoque_docs)}")
        print(f"   Vendas encontradas: {len(vendas_docs)}")
        
        if not estoque_docs and not vendas_docs:
            # Só usa conhecimento geral se NÃO houver nada do banco
            conhecimento_docs = [d for d in docs if d.metadata.get("source") not in ["estoque", "vendas"]]
            if conhecimento_docs:
                return (
                    f"{conhecimento_docs[0].page_content}\n\n"
                    f"💡 Informação da base de conhecimento geral."
                )
            return "Não encontrei informações específicas sobre sua pergunta."
        
        print("✅ Respondendo com dados REAIS do banco de dados MySQL")
        
        is_quantity = any(w in question_lower for w in ["quanto", "quantos", "quantidade"])
        is_price = any(w in question_lower for w in ["preço", "valor", "custa"])
        is_sales = any(w in question_lower for w in ["venda", "vendeu", "cliente"])
        is_list = any(w in question_lower for w in ["lista", "todos", "quais"])
        
        produtos_conhecidos = ["alface", "tomate", "cenoura", "batata", "cebola", "arroz", "feijão"]
        produto_mencionado = next((p for p in produtos_conhecidos if p in question_lower), None)
        
        if is_sales and vendas_docs:
            vendas_info = []
            total = 0
            
            for doc in vendas_docs[:5]:
                prod = doc.metadata.get("produto")
                cli = doc.metadata.get("cliente")
                val = doc.metadata.get("valor", 0)
                qtd = doc.metadata.get("quantidade", 0)
                total += float(val)
                vendas_info.append(f"• {qtd}x {prod} → {cli} (R$ {val:.2f})")
            
            return (
                f"📊 **Histórico de Vendas**\n\n" +
                "\n".join(vendas_info) +
                f"\n\n💵 Total: R$ {total:.2f}\n"
                f"✅ Dados reais do banco MySQL"
            )
        
        if estoque_docs:
            if produto_mencionado:
                for doc in estoque_docs:
                    if produto_mencionado in doc.metadata.get("produto", "").lower():
                        prod = doc.metadata.get("produto")
                        qtd = doc.metadata.get("quantidade")
                        preco = doc.metadata.get("preco")
                        cat = doc.metadata.get("categoria")
                        
                        if is_price:
                            return f"💰 **{prod}**: R$ {preco:.2f}/un\nEstoque: {qtd} unidades\n✅ Preço do banco de dados"
                        elif is_quantity:
                            return f"📦 **{prod}**: {qtd} unidades disponíveis\nPreço: R$ {preco:.2f}/un\n✅ Quantidade atualizada do MySQL"
                        else:
                            return f"📦 **{prod}** ({cat})\n• Quantidade: {qtd} un\n• Preço: R$ {preco:.2f}/un\n✅ Dados do estoque"
            
            if is_list or len(estoque_docs) > 1:
                produtos = []
                total_valor = 0
                
                for doc in estoque_docs[:7]:
                    prod = doc.metadata.get("produto")
                    qtd = doc.metadata.get("quantidade")
                    preco = doc.metadata.get("preco")
                    cat = doc.metadata.get("categoria", "")
                    total_valor += qtd * preco
                    produtos.append(f"• **{prod}** ({cat}): {qtd} un × R$ {preco:.2f} = R$ {qtd*preco:.2f}")
                
                return (
                    f"📋 **Estoque Completo**\n\n" +
                    "\n".join(produtos) +
                    f"\n\n💰 Valor total: R$ {total_valor:.2f}\n"
                    f"✅ Inventário MySQL em tempo real"
                )
            
            doc = estoque_docs[0]
            prod = doc.metadata.get("produto")
            qtd = doc.metadata.get("quantidade")
            preco = doc.metadata.get("preco")
            cat = doc.metadata.get("categoria", "")
            
            return (
                f"📦 **{prod}** ({cat})\n"
                f"• Quantidade: {qtd} unidades\n"
                f"• Preço: R$ {preco:.2f}/un\n"
                f"• Total: R$ {qtd * preco:.2f}\n\n"
                f"✅ Dados atualizados do MySQL"
            )
        
        return "Encontrei informações mas não consegui processá-las adequadamente."
rag_service = RAGService()