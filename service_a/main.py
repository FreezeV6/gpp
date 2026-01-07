from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from database import get_db, init_db, AIResult
from schemas import AIResultCreate, AIResultResponse, HealthResponse

app = FastAPI(title="Service A - AI Results Storage API")


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="healthy",
        service="service-a",
        timestamp=datetime.utcnow()
    )


@app.post("/results", response_model=AIResultResponse, status_code=201)
def create_result(result: AIResultCreate, db: Session = Depends(get_db)):
    existing = db.query(AIResult).filter(AIResult.task_id == result.task_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Result with this task_id already exists")

    db_result = AIResult(
        task_id=result.task_id,
        image_url=result.image_url,
        people_count=result.people_count,
        confidence=result.confidence,
        status=result.status
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result


@app.get("/results", response_model=List[AIResultResponse])
def get_all_results(skip: int = 0, limit: int = 100000, db: Session = Depends(get_db)):
    results = db.query(AIResult).offset(skip).limit(limit).all()
    return results


@app.get("/results/{task_id}", response_model=AIResultResponse)
def get_result(task_id: str, db: Session = Depends(get_db)):
    result = db.query(AIResult).filter(AIResult.task_id == task_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result


@app.delete("/results/{task_id}", status_code=204)
def delete_result(task_id: str, db: Session = Depends(get_db)):
    result = db.query(AIResult).filter(AIResult.task_id == task_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    db.delete(result)
    db.commit()
    return None


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(AIResult).count()
    return {
        "total_results": total,
        "service": "service-a"
    }

