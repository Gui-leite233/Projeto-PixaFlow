import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from app.config import settings

class RAGService:
    def __init__(self):
        try:
            print("🔄 Inicializando RAG Service...")
            
            # Embeddings locais (não precisa de API)
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
            
            # Adicionar dados de exemplo
            self._initialize_sample_data()
            
            print("✅ RAG Service inicializado com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar RAG: {e}")
            raise
    
    def _initialize_sample_data(self):
        """Adiciona dados de exemplo se o banco estiver vazio"""
        try:
            if self.collection.count() == 0:
                print("📝 Adicionando dados de exemplo...")
                sample_texts = [
                    "Python é uma linguagem de programação de alto nível, interpretada e de propósito geral. É conhecida por sua sintaxe clara e legível.",
                    "FastAPI é um framework web moderno e rápido para construir APIs com Python. Utiliza type hints e é baseado em padrões como OpenAPI.",
                    "React é uma biblioteca JavaScript para construir interfaces de usuário. Foi criada pelo Facebook e é mantida por uma comunidade ativa.",
                    "Docker é uma plataforma para desenvolver, enviar e executar aplicações em containers. Facilita a portabilidade de aplicações.",
                    "Machine Learning é um subcampo da inteligência artificial focado em criar sistemas que aprendem com dados e melhoram sua performance.",
                    "ChromaDB é um banco de dados vetorial open-source otimizado para armazenar e buscar embeddings.",
                    "RAG (Retrieval-Augmented Generation) é uma técnica que combina busca de informações com geração de texto por IA.",
                ]
                
                self.vectorstore.add_texts(texts=sample_texts)
                print(f"✅ {len(sample_texts)} documentos de exemplo adicionados!")
        except Exception as e:
            print(f"⚠️ Aviso ao inicializar dados: {e}")
    
    def add_documents(self, texts: list[str], metadatas: list[dict] = None):
        """Adiciona documentos ao banco vetorial"""
        try:
            self.vectorstore.add_texts(texts=texts, metadatas=metadatas)
            print(f"✅ {len(texts)} documento(s) adicionado(s)")
            return True
        except Exception as e:
            print(f"❌ Erro ao adicionar documentos: {e}")
            return False
    
    def query(self, question: str, k: int = 3):
        """Busca documentos relevantes e gera resposta"""
        try:
            print(f"🔍 Processando query: {question}")
            
            # Busca documentos similares
            docs = self.vectorstore.similarity_search(question, k=k)
            
            if not docs:
                return {
                    "answer": "Não encontrei informações relevantes para responder sua pergunta. Tente adicionar mais documentos ao sistema ou reformule sua pergunta.",
                    "sources": []
                }
            
            # Gera resposta baseada nos documentos encontrados
            answer = self._generate_answer(question, docs)
            sources = [doc.page_content for doc in docs]
            
            print(f"✅ Resposta gerada com {len(sources)} fontes")
            
            return {
                "answer": answer,
                "sources": sources
            }
            
        except Exception as e:
            print(f"❌ Erro na query: {e}")
            return {
                "answer": f"Desculpe, ocorreu um erro ao processar sua consulta: {str(e)}",
                "sources": []
            }
    
    def _generate_answer(self, question: str, docs: list):
        """Gera uma resposta baseada nos documentos encontrados"""
        
        # Monta a resposta com base nos documentos
        answer_parts = [f"Com base na sua pergunta '{question}', encontrei as seguintes informações:\n"]
        
        for i, doc in enumerate(docs, 1):
            answer_parts.append(f"\n{i}. {doc.page_content}")
        
        answer_parts.append("\n\n💡 Essas informações foram recuperadas do banco de conhecimento do sistema.")
        
        return "".join(answer_parts)

# Instância global do serviço
rag_service = RAGService()
