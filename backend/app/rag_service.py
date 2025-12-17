import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from app.config import settings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

class RAGService:
    def __init__(self):
        try:
            print("🔄 Inicializando RAG Service...")
            
            # Embeddings locais
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            
            # ChromaDB
            self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
            
            # Criar ou obter collection
            try:
                self.collection = self.chroma_client.get_collection("documents")
            except:
                self.collection = self.chroma_client.create_collection("documents")
            
            self.vectorstore = Chroma(
                client=self.chroma_client,
                collection_name="documents",
                embedding_function=self.embeddings
            )
            
            # Database connection para sincronização
            DATABASE_URL = f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
            self.engine = create_engine(DATABASE_URL)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Inicializar dados
            self._initialize_sample_data()
            self._sync_database_to_rag()
            
            print("✅ RAG Service inicializado com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar RAG: {e}")
            raise
    
    def _sync_database_to_rag(self):
        """Sincroniza dados do MySQL para o ChromaDB"""
        try:
            print("🔄 Sincronizando banco de dados para RAG...")
            db = self.SessionLocal()
            
            # Buscar dados de ESTOQUE
            estoque_query = text("SELECT * FROM estoque")
            estoque_result = db.execute(estoque_query)
            estoque_rows = estoque_result.fetchall()
            
            estoque_texts = []
            estoque_metadatas = []
            
            for row in estoque_rows:
                # Cria texto descritivo para cada produto
                text = (
                    f"No estoque temos {row.quantidade} {row.unidade} de {row.produto}. "
                    f"O preço unitário é R$ {row.preco:.2f}. "
                    f"Este produto pertence à categoria {row.categoria}. "
                    f"Última atualização: {row.ultima_atualizacao}."
                )
                estoque_texts.append(text)
                estoque_metadatas.append({
                    "source": "estoque",
                    "produto": row.produto,
                    "quantidade": row.quantidade,
                    "preco": row.preco,
                    "id": row.id
                })
            
            # Buscar dados de VENDAS
            vendas_query = text("SELECT * FROM vendas ORDER BY data_venda DESC LIMIT 20")
            vendas_result = db.execute(vendas_query)
            vendas_rows = vendas_result.fetchall()
            
            vendas_texts = []
            vendas_metadatas = []
            
            for row in vendas_rows:
                text = (
                    f"Foi realizada uma venda de {row.quantidade} unidades de {row.produto} "
                    f"para o cliente {row.cliente}. "
                    f"O valor total da venda foi R$ {row.valor_total:.2f}. "
                    f"Data da venda: {row.data_venda}."
                )
                vendas_texts.append(text)
                vendas_metadatas.append({
                    "source": "vendas",
                    "produto": row.produto,
                    "cliente": row.cliente,
                    "valor": row.valor_total,
                    "id": row.id
                })
            
            db.close()
            
            # Adiciona ao ChromaDB
            if estoque_texts:
                self.vectorstore.add_texts(
                    texts=estoque_texts,
                    metadatas=estoque_metadatas
                )
                print(f"✅ {len(estoque_texts)} produtos do estoque sincronizados!")
            
            if vendas_texts:
                self.vectorstore.add_texts(
                    texts=vendas_texts,
                    metadatas=vendas_metadatas
                )
                print(f"✅ {len(vendas_texts)} vendas sincronizadas!")
                
        except Exception as e:
            print(f"⚠️ Aviso ao sincronizar banco: {e}")
    
    def _initialize_sample_data(self):
        """Adiciona conhecimento geral ao sistema"""
        try:
            # Verifica se já tem muitos documentos (evita duplicação)
            if self.collection.count() > 50:
                print("📚 Base de conhecimento já populada.")
                return
                
            print("📝 Adicionando conhecimento geral...")
            sample_texts = [
                "Python é uma linguagem de programação de alto nível, interpretada e de propósito geral. É conhecida por sua sintaxe clara e legível.",
                
                "FastAPI é um framework web moderno para construir APIs com Python. Usa type hints e validação automática de dados.",
                
                "React é uma biblioteca JavaScript para interfaces de usuário. Permite criar componentes reutilizáveis e tem uma grande comunidade.",
                
                "Docker é uma plataforma para containers que facilita o deployment e a portabilidade de aplicações entre ambientes.",
                
                "Machine Learning é um campo da IA focado em sistemas que aprendem com dados e melhoram ao longo do tempo.",
                
                "ChromaDB é um banco vetorial open-source otimizado para embeddings e busca semântica.",
                
                "RAG (Retrieval-Augmented Generation) combina busca de informações com geração de texto por IA.",
                
                "SQL é a linguagem padrão para gerenciar bancos de dados relacionais, permitindo operações CRUD.",
                
                "Git é um sistema de controle de versão distribuído usado para rastrear mudanças em código.",
                
                "API REST usa métodos HTTP (GET, POST, PUT, DELETE) para operações em recursos web.",
            ]
            
            self.vectorstore.add_texts(texts=sample_texts)
            print(f"✅ {len(sample_texts)} documentos de conhecimento adicionados!")
            
        except Exception as e:
            print(f"⚠️ Aviso ao inicializar conhecimento: {e}")
    
    def sync_database(self):
        """Método público para re-sincronizar o banco"""
        self._sync_database_to_rag()
        return {"message": "Banco de dados sincronizado com sucesso!"}
    
    def add_documents(self, texts: list[str], metadatas: list[dict] = None):
        """Adiciona documentos customizados ao RAG"""
        try:
            self.vectorstore.add_texts(texts=texts, metadatas=metadatas)
            print(f"✅ {len(texts)} documento(s) adicionado(s)")
            return True
        except Exception as e:
            print(f"❌ Erro ao adicionar documentos: {e}")
            return False
    
    def query(self, question: str, k: int = 4):
        """Busca documentos relevantes e gera resposta"""
        try:
            print(f"🔍 Processando query: {question}")
            
            # Busca documentos similares
            docs = self.vectorstore.similarity_search(question, k=k)
            
            if not docs:
                return {
                    "answer": "Não encontrei informações relevantes para responder sua pergunta. Tente adicionar mais documentos ao sistema.",
                    "sources": []
                }
            
            # Gera resposta baseada nos documentos
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
        """Gera resposta natural baseada nos documentos encontrados"""
        
        if not docs:
            return "Não encontrei informações relevantes."
        
        question_lower = question.lower()
        
        # Identifica o tipo de pergunta
        is_quantity_question = any(word in question_lower for word in 
            ["quanto", "quantos", "quantidade", "tem"])
        
        is_price_question = any(word in question_lower for word in 
            ["preço", "valor", "custa", "custo"])
        
        is_sales_question = any(word in question_lower for word in 
            ["vendas", "vendeu", "cliente", "comprou"])
        
        # Resposta para perguntas de QUANTIDADE
        if is_quantity_question and docs[0].metadata.get("source") == "estoque":
            produto = docs[0].metadata.get("produto")
            quantidade = docs[0].metadata.get("quantidade")
            
            return (
                f"Atualmente temos **{quantidade} unidades** de {produto} no estoque.\n\n"
                f"📦 Informação recuperada do banco de dados em tempo real."
            )
        
        # Resposta para perguntas de PREÇO
        elif is_price_question and docs[0].metadata.get("source") == "estoque":
            produto = docs[0].metadata.get("produto")
            preco = docs[0].metadata.get("preco")
            
            return (
                f"O preço de {produto} é **R$ {preco:.2f}** por unidade.\n\n"
                f"💰 Informação recuperada do banco de dados."
            )
        
        # Resposta para perguntas de VENDAS
        elif is_sales_question and docs[0].metadata.get("source") == "vendas":
            vendas_info = []
            for doc in docs[:3]:
                if doc.metadata.get("source") == "vendas":
                    vendas_info.append(doc.page_content)
            
            return (
                f"Aqui estão as informações sobre vendas:\n\n" +
                "\n\n".join(f"• {info}" for info in vendas_info) +
                f"\n\n📊 Dados recuperados do histórico de vendas."
            )
        
        # Resposta GENÉRICA para múltiplas informações
        elif len(docs) > 1:
            answer_parts = [
                f"Com base na sua pergunta, encontrei as seguintes informações:\n"
            ]
            
            for i, doc in enumerate(docs[:3], 1):
                source_type = doc.metadata.get("source", "conhecimento")
                answer_parts.append(f"\n**{i}.** {doc.page_content}")
            
            answer_parts.append(
                f"\n\n💡 Informações recuperadas da base de conhecimento do sistema."
            )
            
            return "".join(answer_parts)
        
        # Resposta para DOCUMENTO ÚNICO
        else:
            return (
                f"{docs[0].page_content}\n\n"
                f"💡 Informação recuperada da base de conhecimento."
            )

# Instância global do serviço
rag_service = RAGService()