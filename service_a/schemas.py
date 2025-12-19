from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AIResultCreate(BaseModel):
    task_id: str
    image_url: str
    people_count: int
    confidence: float
    status: str = "completed"


class AIResultResponse(BaseModel):
    id: int
    task_id: str
    image_url: str
    people_count: int
    confidence: float
    processed_at: datetime
    status: str

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime

