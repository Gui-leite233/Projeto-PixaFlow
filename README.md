# 🤖 Pixaflow - Sistema RAG com IA

Sistema inteligente de consulta usando **RAG (Retrieval-Augmented Generation)** para responder perguntas sobre estoque e vendas.

## 🛠️ Stack Tecnológica

- **Frontend**: React 18 (interface moderna de chatbot)
- **Backend**: FastAPI (API REST)
- **Banco de Dados**: MySQL 8.0 (estoque + vendas + histórico)
- **Vector Store**: ChromaDB (busca semântica)
- **LLM**: HuggingFace Sentence Transformers (embeddings)
- **Containerização**: Docker Compose

## 🚀 Como Executar

### 1️⃣ Clone o repositório
```bash
git clone https://github.com/Gui-leite233/Projeto-PixaFlow.git
cd Projeto-pixaflow
```

### 2️⃣ Inicie os containers
```bash
docker-compose up --build
```
⏳ Aguarde ~2 minutos para inicialização completa.

### 3️⃣ Acesse a aplicação
- **Interface do Chat**: http://localhost:3000
- **API Backend**: http://localhost:8000
- **Documentação Interativa**: http://localhost:8000/docs

### 4️⃣ Execute os testes
```bash
docker-compose exec backend pytest
```

## 📁 Estrutura do Projeto

```
Projeto-pixaflow/
├── backend/
│   ├── app/
│   │   ├── models.py          # Modelos de BD (Estoque, Vendas, Query)
│   │   ├── rag_service.py     # Sistema RAG + ChromaDB
│   │   ├── routes/            # Endpoints da API
│   │   └── database.py        # Conexão MySQL
│   ├── tests/
│   │   └── test_query_routes.py  # Testes pytest
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Interface do chatbot
│   │   ├── services/api.js    # Cliente API
│   │   └── App.css            # Estilos modernos
│   └── package.json
│
└── docker-compose.yml         # Orquestração completa
```

## ✨ Funcionalidades

✅ **Chatbot Inteligente** - Interface conversacional moderna  
✅ **RAG (Retrieval-Augmented Generation)** - Busca semântica em documentos  
✅ **Consultas em Tempo Real** - Dados sincronizados com MySQL  
✅ **Histórico de Conversas** - Armazena perguntas e respostas  
✅ **Dados de Exemplo** - Estoque e vendas pré-carregados  
✅ **Testes Automatizados** - 6 testes com pytest  

## 🎯 Exemplos de Uso

Pergunte ao sistema:

- *"Quanto custa o tomate?"*
- *"Quantos produtos tem no estoque?"*
- *"Mostre as vendas recentes"*
- *"Qual o preço da alface?"*

## 🔧 Tecnologias de IA

- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`
- **Vector Database**: ChromaDB (persistente)
- **Framework**: LangChain Community

## 📊 Dados de Exemplo

O sistema vem com dados pré-carregados:
- 7 produtos em estoque (Alface, Tomate, Cenoura, etc.)
- 3 vendas registradas
- Categorias e preços definidos

## 🔍 Endpoints da API

- `POST /api/v1/query` - Fazer pergunta ao sistema
- `GET /api/v1/queries` - Histórico de consultas
- `POST /api/v1/add-documents` - Adicionar documentos
- `POST /api/v1/sync-database` - Sincronizar BD com ChromaDB
- `GET /api/v1/documents/count` - Contar documentos
- `GET /health` - Status da aplicação

## 👨‍💻 Desenvolvido por: Guilherme