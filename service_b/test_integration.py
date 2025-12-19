import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class TestHealthEndpoint:
    def test_health_check_rabbitmq_connected(self, client):
        with patch('main.check_rabbitmq_connection', return_value=True):
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "service-b"
            assert data["rabbitmq_connected"] is True

    def test_health_check_rabbitmq_disconnected(self, client):
        with patch('main.check_rabbitmq_connection', return_value=False):
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert data["rabbitmq_connected"] is False


class TestAnalyzeEndpoint:
    def test_analyze_valid_url(self, client):
        with patch('main.publish_task', return_value=True):
            response = client.post("/analyze", json={
                "image_url": "https://example.com/image.jpg"
            })
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "queued"
            assert "task_id" in data

    def test_analyze_with_custom_task_id(self, client):
        with patch('main.publish_task', return_value=True):
            response = client.post("/analyze", json={
                "image_url": "https://example.com/image.jpg",
                "task_id": "custom-task-123"
            })
            assert response.status_code == 200
            data = response.json()
            assert data["task_id"] == "custom-task-123"

    def test_analyze_invalid_url(self, client):
        response = client.post("/analyze", json={
            "image_url": "not-a-valid-url"
        })
        assert response.status_code == 400

    def test_analyze_empty_url(self, client):
        response = client.post("/analyze", json={
            "image_url": ""
        })
        assert response.status_code == 400

    def test_analyze_rabbitmq_unavailable(self, client):
        with patch('main.publish_task', return_value=False):
            response = client.post("/analyze", json={
                "image_url": "https://example.com/image.jpg"
            })
            assert response.status_code == 503


class TestAnalyzeSyncEndpoint:
    def test_analyze_sync_valid_url(self, client):
        response = client.post("/analyze/sync", json={
            "image_url": "https://example.com/image.jpg"
        })
        assert response.status_code == 200
        data = response.json()
        assert "people_count" in data
        assert "confidence" in data
        assert data["status"] == "completed"
        assert isinstance(data["people_count"], int)
        assert 0 <= data["confidence"] <= 1

    def test_analyze_sync_invalid_url(self, client):
        response = client.post("/analyze/sync", json={
            "image_url": "invalid-url"
        })
        assert response.status_code == 400

    def test_analyze_sync_deterministic_result(self, client):
        """Test że ten sam URL daje ten sam wynik (deterministyczny)"""
        url = "https://example.com/test-image.jpg"

        response1 = client.post("/analyze/sync", json={"image_url": url})
        response2 = client.post("/analyze/sync", json={"image_url": url})

        data1 = response1.json()
        data2 = response2.json()

        assert data1["people_count"] == data2["people_count"]
        assert data1["confidence"] == data2["confidence"]


class TestQueueStatusEndpoint:
    def test_queue_status_connected(self, client):
        with patch('main.check_rabbitmq_connection', return_value=True):
            response = client.get("/queue/status")
            assert response.status_code == 200
            data = response.json()
            assert data["rabbitmq_connected"] is True

    def test_queue_status_disconnected(self, client):
        with patch('main.check_rabbitmq_connection', return_value=False):
            response = client.get("/queue/status")
            assert response.status_code == 200
            data = response.json()
            assert data["rabbitmq_connected"] is False


class TestAIProcessor:
    def test_validate_image_url_valid_http(self):
        from ai_processor import validate_image_url
        assert validate_image_url("http://example.com/image.jpg") is True

    def test_validate_image_url_valid_https(self):
        from ai_processor import validate_image_url
        assert validate_image_url("https://example.com/image.png") is True

    def test_validate_image_url_invalid(self):
        from ai_processor import validate_image_url
        assert validate_image_url("ftp://example.com/image.jpg") is False
        assert validate_image_url("not-a-url") is False
        assert validate_image_url("") is False

    def test_analyze_image_returns_valid_data(self):
        from ai_processor import analyze_image
        people_count, confidence = analyze_image("https://example.com/test.jpg")

        assert isinstance(people_count, int)
        assert 0 <= people_count <= 20
        assert isinstance(confidence, float)
        assert 0.70 <= confidence <= 0.99

