import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from service_a.main import app
from service_a.database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "service-a"


class TestResultsEndpoint:
    def test_create_result(self, client):
        result_data = {
            "task_id": "test-task-001",
            "image_url": "https://example.com/image.jpg",
            "people_count": 5,
            "confidence": 0.95,
            "status": "completed"
        }
        response = client.post("/results", json=result_data)
        assert response.status_code == 201
        data = response.json()
        assert data["task_id"] == "test-task-001"
        assert data["people_count"] == 5
        assert data["confidence"] == 0.95

    def test_create_duplicate_result(self, client):
        result_data = {
            "task_id": "test-task-duplicate",
            "image_url": "https://example.com/image.jpg",
            "people_count": 3,
            "confidence": 0.90,
            "status": "completed"
        }
        response = client.post("/results", json=result_data)
        assert response.status_code == 201

        response = client.post("/results", json=result_data)
        assert response.status_code == 409

    def test_get_result(self, client):
        result_data = {
            "task_id": "test-task-get",
            "image_url": "https://example.com/image.jpg",
            "people_count": 10,
            "confidence": 0.88,
            "status": "completed"
        }
        client.post("/results", json=result_data)

        response = client.get("/results/test-task-get")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test-task-get"
        assert data["people_count"] == 10

    def test_get_nonexistent_result(self, client):
        response = client.get("/results/nonexistent-task")
        assert response.status_code == 404

    def test_get_all_results(self, client):
        for i in range(5):
            result_data = {
                "task_id": f"test-task-list-{i}",
                "image_url": f"https://example.com/image{i}.jpg",
                "people_count": i,
                "confidence": 0.80 + i * 0.02,
                "status": "completed"
            }
            client.post("/results", json=result_data)

        response = client.get("/results")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_delete_result(self, client):
        result_data = {
            "task_id": "test-task-delete",
            "image_url": "https://example.com/image.jpg",
            "people_count": 2,
            "confidence": 0.75,
            "status": "completed"
        }
        client.post("/results", json=result_data)

        response = client.delete("/results/test-task-delete")
        assert response.status_code == 204

        response = client.get("/results/test-task-delete")
        assert response.status_code == 404

    def test_delete_nonexistent_result(self, client):
        response = client.delete("/results/nonexistent")
        assert response.status_code == 404


class TestStatsEndpoint:
    def test_get_stats(self, client):
        for i in range(3):
            result_data = {
                "task_id": f"test-task-stats-{i}",
                "image_url": f"https://example.com/image{i}.jpg",
                "people_count": i,
                "confidence": 0.85,
                "status": "completed"
            }
            client.post("/results", json=result_data)

        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_results"] == 3
        assert data["service"] == "service-a"

