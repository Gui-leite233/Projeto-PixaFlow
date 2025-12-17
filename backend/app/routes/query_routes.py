from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db
from app.models import Query
from app.rag_service import rag_service

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

class DocumentRequest(BaseModel):
    texts: List[str]
    metadatas: Optional[List[dict]] = None

@router.post("/query")
async def create_query(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        result = rag_service.query(request.question)
        
        query = Query(
            query_text=request.question,
            response=result["answer"]
        )
        db.add(query)
        db.commit()
        
        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "metadata": result.get("metadata", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/queries")
async def get_queries(db: Session = Depends(get_db)):
    queries = db.query(Query).order_by(Query.created_at.desc()).limit(10).all()
    return queries

@router.post("/add-documents")
async def add_documents(request: DocumentRequest):
    try:
        if request.metadatas is None:
            request.metadatas = [{"source": "custom"} for _ in request.texts]
        
        if len(request.metadatas) != len(request.texts):
            raise HTTPException(
                status_code=400, 
                detail="metadatas deve ter o mesmo tamanho que texts"
            )
        
        success = rag_service.add_documents(
            texts=request.texts,
            metadatas=request.metadatas
        )
        
        if success:
            return {
                "message": f"{len(request.texts)} documento(s) adicionado(s) com sucesso!",
                "count": len(request.texts)
            }
        else:
            raise HTTPException(status_code=500, detail="Erro ao adicionar documentos")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync-database")
async def sync_database():
    try:
        result = rag_service.sync_database()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/count")
async def get_document_count():
    try:
        count = rag_service.collection.count()
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))