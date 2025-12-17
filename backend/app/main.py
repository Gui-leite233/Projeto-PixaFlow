from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import query_routes
from app.database import engine, Base

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RAG Query API",
    description="Sistema de consulta inteligente usando RAG com ChromaDB",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(query_routes.router, prefix="/api/v1", tags=["RAG Queries"])

@app.get("/")
async def root():
    return {
        "message": "Sistema RAG - Consulta Inteligente",
        "status": "ok",
        "endpoints": {
            "query": "/api/v1/query",
            "add_docs": "/api/v1/add-documents",
            "history": "/api/v1/queries",
            "sync": "/api/v1/sync-database",
            "count": "/api/v1/documents/count"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    try:
        from app.rag_service import rag_service
        print("✅ RAG Service inicializado!")
        print(f"📚 Documentos no sistema: {rag_service.collection.count()}")
    except Exception as e:
        print(f"⚠️ Aviso ao inicializar RAG: {e}")
    try:
        from app.init_db import init_database
        init_database()
        print("✅ Banco de dados inicializado!")
    except Exception as e:
        print(f"⚠️ Aviso ao inicializar DB: {e}")