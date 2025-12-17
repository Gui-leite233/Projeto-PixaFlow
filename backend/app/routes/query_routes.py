from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import Query
from app.sql_ai_service import sql_ai_service

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

@router.post("/query")
async def create_query(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        # Processa a pergunta com IA SQL
        result = sql_ai_service.process_query(request.question)
        
        # Salva no histórico
        query = Query(
            query_text=request.question,
            response=result["answer"]
        )
        db.add(query)
        db.commit()
        
        return {
            "answer": result["answer"],
            "sources": [result["sql"]] if result["sql"] else [],
            "data": result.get("data", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/queries")
async def get_queries(db: Session = Depends(get_db)):
    queries = db.query(Query).order_by(Query.created_at.desc()).limit(10).all()
    return queries
