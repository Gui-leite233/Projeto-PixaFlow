from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import query_routes
from app.database import engine, Base

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SQL AI Query API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query_routes.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "SQL AI rodando!", "status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Inicializar dados ao startar
@app.on_event("startup")
async def startup_event():
    from app.init_db import init_database
    try:
        init_database()
    except Exception as e:
        print(f"⚠️ Aviso ao inicializar dados: {e}")
