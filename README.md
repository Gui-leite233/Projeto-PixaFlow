# Projeto Pixaflow - Sistema RAG com IA

Sistema de consulta inteligente usando RAG (Retrieval-Augmented Generation) com ChromaDB.

## Stack Tecnológica

- **Frontend**: React
- **Backend**: FastAPI
- **Banco de Dados**: MySQL
- **Vector Store**: ChromaDB
- **LLM**: HuggingFace (Flan-T5)
- **Containerização**: Docker

## Como Executar

### 1. Iniciar os containers:
```bash
docker-compose up --build
```

### 2. Acessar a aplicação:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Documentação API: http://localhost:8000/docs

### 3. Executar testes:
```bash
docker-compose exec backend pytest
```

## Estrutura do Projeto
```
Projeto-pixaflow/
├── backend/           # API FastAPI
├── frontend/          # Interface React
└── docker-compose.yml # Orquestração dos containers
```

## Funcionalidades

- Consulta inteligente com IA
- Armazenamento de documentos
- Busca semântica com RAG
- Histórico de consultas
- Interface amigável

## Desenvolvido por: Guilherme
