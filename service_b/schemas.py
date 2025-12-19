from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ImageAnalysisRequest(BaseModel):
    image_url: str
    task_id: Optional[str] = None


class ImageAnalysisResponse(BaseModel):
    task_id: str
    status: str
    message: str


class AnalysisResult(BaseModel):
    task_id: str
    image_url: str
    people_count: int
    confidence: float
    status: str = "completed"


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime
    rabbitmq_connected: bool
