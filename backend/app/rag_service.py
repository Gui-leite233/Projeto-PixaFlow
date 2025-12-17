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
                    "categoria": row.categoria,
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
                    "quantidade": row.quantidade,
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
    
    def query(self, question: str, k: int = 5):
        """Busca documentos relevantes e gera resposta"""
        try:
            print(f"🔍 Processando query: {question}")
            
            # Busca documentos similares (aumentei para k=5 para ter mais contexto)
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
        
        # Separa documentos por tipo
        estoque_docs = [d for d in docs if d.metadata.get("source") == "estoque"]
        vendas_docs = [d for d in docs if d.metadata.get("source") == "vendas"]
        conhecimento_docs = [d for d in docs if d.metadata.get("source") not in ["estoque", "vendas"]]
        
        # Identifica o tipo de pergunta com mais palavras-chave
        is_quantity_question = any(word in question_lower for word in 
            ["quanto", "quantos", "quantidade", "tem", "há", "existe", "tenho", "temos"])
        
        is_price_question = any(word in question_lower for word in 
            ["preço", "valor", "custa", "custo", "quanto custa", "vale"])
        
        is_sales_question = any(word in question_lower for word in 
            ["vendas", "vendeu", "cliente", "comprou", "comprador", "compra", "vendido"])
        
        is_list_question = any(word in question_lower for word in 
            ["lista", "listar", "todos", "todas", "quais", "mostre", "exiba"])
        
        is_stock_question = any(word in question_lower for word in 
            ["estoque", "produto", "produtos", "disponível", "disponibilidade"])
        
        # Busca nome de produto específico na pergunta
        produtos_conhecidos = ["alface", "tomate", "cenoura", "batata", "cebola", "arroz", "feijão"]
        produto_mencionado = None
        for produto in produtos_conhecidos:
            if produto in question_lower:
                produto_mencionado = produto
                break
        
        # === PERGUNTAS SOBRE QUANTIDADE DE PRODUTOS ESPECÍFICOS ===
        if is_quantity_question and estoque_docs:
            # Se mencionou um produto específico, prioriza ele
            if produto_mencionado:
                for doc in estoque_docs:
                    if doc.metadata.get("produto", "").lower() == produto_mencionado:
                        produto = doc.metadata.get("produto")
                        quantidade = doc.metadata.get("quantidade")
                        preco = doc.metadata.get("preco")
                        return (
                            f"📦 **Estoque de {produto}**\n\n"
                            f"Quantidade disponível: **{quantidade} unidades**\n"
                            f"Preço unitário: **R$ {preco:.2f}**\n\n"
                            f"✅ Informação em tempo real do banco de dados."
                        )
            
            # Se não mencionou produto ou não encontrou, lista os encontrados
            if len(estoque_docs) == 1:
                produto = estoque_docs[0].metadata.get("produto")
                quantidade = estoque_docs[0].metadata.get("quantidade")
                preco = estoque_docs[0].metadata.get("preco")
                return (
                    f"📦 **Estoque de {produto}**\n\n"
                    f"Quantidade disponível: **{quantidade} unidades**\n"
                    f"Preço unitário: **R$ {preco:.2f}**\n\n"
                    f"✅ Informação em tempo real do banco de dados."
                )
            else:
                # Múltiplos produtos
                produtos_info = []
                for doc in estoque_docs[:5]:
                    produto = doc.metadata.get("produto")
                    quantidade = doc.metadata.get("quantidade")
                    preco = doc.metadata.get("preco")
                    produtos_info.append(
                        f"• **{produto}**: {quantidade} unidades (R$ {preco:.2f}/un)"
                    )
                
                return (
                    f"📦 **Quantidades em estoque:**\n\n" +
                    "\n".join(produtos_info) +
                    f"\n\n✅ Dados atualizados do sistema."
                )
        
        # === PERGUNTAS SOBRE PREÇO ===
        elif is_price_question and estoque_docs:
            # Se mencionou um produto específico, prioriza ele
            if produto_mencionado:
                for doc in estoque_docs:
                    if doc.metadata.get("produto", "").lower() == produto_mencionado:
                        produto = doc.metadata.get("produto")
                        preco = doc.metadata.get("preco")
                        quantidade = doc.metadata.get("quantidade")
                        return (
                            f"💰 **Preço de {produto}**\n\n"
                            f"Valor: **R$ {preco:.2f}** por unidade\n"
                            f"Estoque disponível: {quantidade} unidades\n\n"
                            f"✅ Informação do banco de dados."
                        )
            
            if len(estoque_docs) == 1:
                produto = estoque_docs[0].metadata.get("produto")
                preco = estoque_docs[0].metadata.get("preco")
                quantidade = estoque_docs[0].metadata.get("quantidade")
                
                return (
                    f"💰 **Preço de {produto}**\n\n"
                    f"Valor: **R$ {preco:.2f}** por unidade\n"
                    f"Estoque disponível: {quantidade} unidades\n\n"
                    f"✅ Informação do banco de dados."
                )
            else:
                # Múltiplos produtos
                produtos_info = []
                for doc in estoque_docs[:5]:
                    produto = doc.metadata.get("produto")
                    preco = doc.metadata.get("preco")
                    produtos_info.append(f"• **{produto}**: R$ {preco:.2f}")
                
                return (
                    f"💰 **Tabela de preços:**\n\n" +
                    "\n".join(produtos_info) +
                    f"\n\n✅ Informação atualizada."
                )
        
        # === PERGUNTAS SOBRE VENDAS ===
        elif is_sales_question and vendas_docs:
            vendas_info = []
            total_vendas = 0
            produtos_vendidos = {}
            
            for doc in vendas_docs[:5]:
                produto = doc.metadata.get("produto")
                cliente = doc.metadata.get("cliente")
                valor = doc.metadata.get("valor", 0)
                quantidade = doc.metadata.get("quantidade", 0)
                
                total_vendas += float(valor) if valor else 0
                
                if produto in produtos_vendidos:
                    produtos_vendidos[produto] += quantidade
                else:
                    produtos_vendidos[produto] = quantidade
                
                vendas_info.append(
                    f"• {quantidade}x **{produto}** → Cliente: {cliente} (R$ {valor:.2f})"
                )
            
            resumo = "\n".join(f"• **{prod}**: {qtd} unidades vendidas" 
                              for prod, qtd in produtos_vendidos.items())
            
            return (
                f"📊 **Histórico de Vendas**\n\n"
                f"**Vendas recentes:**\n" +
                "\n".join(vendas_info) +
                f"\n\n**Resumo por produto:**\n{resumo}\n\n"
                f"💵 **Total em vendas:** R$ {total_vendas:.2f}\n"
                f"✅ Dados do histórico de vendas."
            )
        
        # === LISTAR TODOS OS PRODUTOS ===
        elif (is_list_question or is_stock_question) and estoque_docs:
            produtos_completos = []
            valor_total_estoque = 0
            
            for doc in estoque_docs:
                produto = doc.metadata.get("produto")
                quantidade = doc.metadata.get("quantidade")
                preco = doc.metadata.get("preco")
                categoria = doc.metadata.get("categoria", "Geral")
                
                valor_total_estoque += quantidade * preco
                
                produtos_completos.append(
                    f"• **{produto}** ({categoria})\n"
                    f"  Qtd: {quantidade} un | Preço: R$ {preco:.2f}/un | Total: R$ {quantidade * preco:.2f}"
                )
            
            return (
                f"📋 **Produtos em Estoque**\n\n" +
                "\n\n".join(produtos_completos) +
                f"\n\n📊 **Resumo:**\n"
                f"• Total de produtos: {len(produtos_completos)}\n"
                f"• Valor total do estoque: R$ {valor_total_estoque:.2f}\n\n"
                f"✅ Inventário completo do sistema."
            )
        
        # === RESPOSTA BASEADA EM CONHECIMENTO GERAL ===
        elif conhecimento_docs:
            if len(conhecimento_docs) == 1:
                return (
                    f"{conhecimento_docs[0].page_content}\n\n"
                    f"💡 Informação da base de conhecimento."
                )
            else:
                answer_parts = ["📚 **Informações encontradas:**\n"]
                
                for i, doc in enumerate(conhecimento_docs[:3], 1):
                    answer_parts.append(f"\n**{i}.** {doc.page_content}")
                
                answer_parts.append("\n\n💡 Base de conhecimento do sistema.")
                return "".join(answer_parts)
        
        # === RESPOSTA GENÉRICA COM TODOS OS DADOS ===
        else:
            response_parts = []
            
            if estoque_docs:
                response_parts.append("📦 **Informações de Estoque:**")
                for doc in estoque_docs[:3]:
                    produto = doc.metadata.get("produto")
                    quantidade = doc.metadata.get("quantidade")
                    preco = doc.metadata.get("preco")
                    response_parts.append(
                        f"\n• **{produto}**: {quantidade} un | R$ {preco:.2f}/un"
                    )
            
            if vendas_docs:
                response_parts.append("\n\n📊 **Informações de Vendas:**")
                for doc in vendas_docs[:3]:
                    produto = doc.metadata.get("produto")
                    cliente = doc.metadata.get("cliente")
                    valor = doc.metadata.get("valor")
                    response_parts.append(
                        f"\n• **{produto}** vendido para {cliente} (R$ {valor:.2f})"
                    )
            
            if conhecimento_docs:
                response_parts.append("\n\n💡 **Base de Conhecimento:**")
                for doc in conhecimento_docs[:2]:
                    response_parts.append(f"\n• {doc.page_content}")
            
            return "".join(response_parts) + "\n\n✅ Dados recuperados do sistema."

# Instância global do serviço
rag_service = RAGService()