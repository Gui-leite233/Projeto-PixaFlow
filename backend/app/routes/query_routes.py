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







