from fastapi import FastAPI, HTTPException
from datetime import datetime
import uuid

from schemas import ImageAnalysisRequest, ImageAnalysisResponse, HealthResponse
from rabbitmq_client import publish_task, check_rabbitmq_connection
from ai_processor import validate_image_url

app = FastAPI(title="Service B - AI People Counting API")


@app.get("/health", response_model=HealthResponse)
def health_check():
    rabbitmq_ok = check_rabbitmq_connection()
    return HealthResponse(
        status="healthy" if rabbitmq_ok else "degraded",
        service="service-b",
        timestamp=datetime.utcnow(),
        rabbitmq_connected=rabbitmq_ok
    )


@app.post("/analyze", response_model=ImageAnalysisResponse)
def analyze_image(request: ImageAnalysisRequest):
    """
    Przyjmuje URL obrazu i kolejkuje go do analizy.
    Analiza odbywa się asynchronicznie przez consumera.
    """
    # Walidacja URL
    if not validate_image_url(request.image_url):
        raise HTTPException(status_code=400, detail="Invalid image URL")

    # Generuj task_id jeśli nie podano
    task_id = request.task_id or str(uuid.uuid4())

    # Przygotuj dane zadania
    task_data = {
        "task_id": task_id,
        "image_url": request.image_url,
        "created_at": datetime.utcnow().isoformat()
    }

    # Publikuj do kolejki
    if not publish_task(task_data):
        raise HTTPException(status_code=503, detail="Failed to queue task - RabbitMQ unavailable")

    return ImageAnalysisResponse(
        task_id=task_id,
        status="queued",
        message="Image analysis task has been queued for processing"
    )


@app.post("/analyze/sync", response_model=dict)
def analyze_image_sync(request: ImageAnalysisRequest):
    """
    Synchroniczna analiza obrazu (bez kolejkowania).
    Używane do testów i małych obciążeń.
    """
    from ai_processor import analyze_image as process_image

    if not validate_image_url(request.image_url):
        raise HTTPException(status_code=400, detail="Invalid image URL")

    task_id = request.task_id or str(uuid.uuid4())
    people_count, confidence = process_image(request.image_url)

    return {
        "task_id": task_id,
        "image_url": request.image_url,
        "people_count": people_count,
        "confidence": confidence,
        "status": "completed"
    }


@app.get("/queue/status")
def queue_status():
    """Sprawdza status kolejki"""
    rabbitmq_ok = check_rabbitmq_connection()
    return {
        "rabbitmq_connected": rabbitmq_ok,
        "service": "service-b"
    }

