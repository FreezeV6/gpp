"""
Testy E2E - komunikacja miedzy serwisami A i B.
Wymaga uruchomionych serwisow (docker compose up).
"""
import pytest
import httpx
import time
import os
SERVICE_A_URL = os.getenv("SERVICE_A_URL", "http://localhost:8001")
SERVICE_B_URL = os.getenv("SERVICE_B_URL", "http://localhost:8002")
# Timeout dla testow E2E
E2E_TIMEOUT = 60  # sekundy
@pytest.fixture(scope="module")
def http_client():
    with httpx.Client(timeout=30.0) as client:
        yield client
def wait_for_services(client: httpx.Client, max_wait: int = 30):
    """Czeka az serwisy beda gotowe"""
    start = time.time()
    while time.time() - start < max_wait:
        try:
            resp_a = client.get(f"{SERVICE_A_URL}/health")
            resp_b = client.get(f"{SERVICE_B_URL}/health")
            if resp_a.status_code == 200 and resp_b.status_code == 200:
                return True
        except httpx.HTTPError:
            pass
        time.sleep(1)
    return False
class TestE2EServicesHealth:
    """Testy sprawdzajace czy serwisy sa dostepne"""
    def test_service_a_health(self, http_client):
        response = http_client.get(f"{SERVICE_A_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "service-a"
    def test_service_b_health(self, http_client):
        response = http_client.get(f"{SERVICE_B_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "service-b"
    def test_service_b_rabbitmq_connection(self, http_client):
        response = http_client.get(f"{SERVICE_B_URL}/queue/status")
        assert response.status_code == 200
        data = response.json()
        assert data["rabbitmq_connected"] is True
class TestE2EImageAnalysisFlow:
    """Testy pelnego przeplywu analizy obrazu"""
    def test_full_analysis_flow(self, http_client):
        """
        Test pelnego przeplywu:
        1. Wyslanie zadania do Service B
        2. Zadanie trafia do RabbitMQ
        3. Consumer przetwarza zadanie
        4. Wynik zapisywany w Service A
        """
        task_id = f"e2e-test-{int(time.time())}"
        image_url = "https://example.com/e2e-test-image.jpg"
        # 1. Wyslij zadanie do Service B
        response = http_client.post(f"{SERVICE_B_URL}/analyze", json={
            "image_url": image_url,
            "task_id": task_id
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"
        assert data["task_id"] == task_id
        # 2. Poczekaj na przetworzenie przez consumera
        result = None
        start_time = time.time()
        while time.time() - start_time < E2E_TIMEOUT:
            try:
                response = http_client.get(f"{SERVICE_A_URL}/results/{task_id}")
                if response.status_code == 200:
                    result = response.json()
                    break
            except httpx.HTTPError:
                pass
            time.sleep(2)
        # 3. Sprawdz wynik w Service A
        assert result is not None, f"Nie znaleziono wyniku dla {task_id} w ciagu {E2E_TIMEOUT}s"
        assert result["task_id"] == task_id
        assert result["image_url"] == image_url
        assert "people_count" in result
        assert "confidence" in result
        assert result["status"] == "completed"
    def test_multiple_tasks_processing(self, http_client):
        """Test przetwarzania wielu zadan rownolegle"""
        base_task_id = f"e2e-multi-{int(time.time())}"
        num_tasks = 5
        tasks = []
        # Wyslij wiele zadan
        for i in range(num_tasks):
            task_id = f"{base_task_id}-{i}"
            response = http_client.post(f"{SERVICE_B_URL}/analyze", json={
                "image_url": f"https://example.com/multi-test-{i}.jpg",
                "task_id": task_id
            })
            assert response.status_code == 200
            tasks.append(task_id)
        # Poczekaj na wyniki
        results = []
        start_time = time.time()
        while len(results) < num_tasks and time.time() - start_time < E2E_TIMEOUT:
            for task_id in tasks:
                if task_id in [r["task_id"] for r in results]:
                    continue
                try:
                    response = http_client.get(f"{SERVICE_A_URL}/results/{task_id}")
                    if response.status_code == 200:
                        results.append(response.json())
                except httpx.HTTPError:
                    pass
            time.sleep(2)
        assert len(results) == num_tasks, f"Oczekiwano {num_tasks} wynikow, otrzymano {len(results)}"
class TestE2ESyncAnalysis:
    """Testy synchronicznej analizy (bez kolejkowania)"""
    def test_sync_analysis_and_manual_save(self, http_client):
        """Test synchronicznej analizy i recznego zapisu do Service A"""
        task_id = f"e2e-sync-{int(time.time())}"
        image_url = "https://example.com/sync-test.jpg"
        # 1. Synchroniczna analiza w Service B
        response = http_client.post(f"{SERVICE_B_URL}/analyze/sync", json={
            "image_url": image_url,
            "task_id": task_id
        })
        assert response.status_code == 200
        analysis_result = response.json()
        # 2. Reczny zapis do Service A
        response = http_client.post(f"{SERVICE_A_URL}/results", json={
            "task_id": task_id,
            "image_url": image_url,
            "people_count": analysis_result["people_count"],
            "confidence": analysis_result["confidence"],
            "status": "completed"
        })
        assert response.status_code == 201
        # 3. Pobierz z Service A
        response = http_client.get(f"{SERVICE_A_URL}/results/{task_id}")
        assert response.status_code == 200
        saved_result = response.json()
        assert saved_result["people_count"] == analysis_result["people_count"]
class TestE2EErrorHandling:
    """Testy obslugi bledow w komunikacji miedzy serwisami"""
    def test_invalid_url_rejected(self, http_client):
        """Test ze nieprawidlowy URL jest odrzucany"""
        response = http_client.post(f"{SERVICE_B_URL}/analyze", json={
            "image_url": "not-a-valid-url"
        })
        assert response.status_code == 400
    def test_duplicate_result_handling(self, http_client):
        """Test obslugi duplikatow w Service A"""
        task_id = f"e2e-dup-{int(time.time())}"
        result_data = {
            "task_id": task_id,
            "image_url": "https://example.com/dup-test.jpg",
            "people_count": 5,
            "confidence": 0.95,
            "status": "completed"
        }
        # Pierwszy zapis
        response = http_client.post(f"{SERVICE_A_URL}/results", json=result_data)
        assert response.status_code == 201
        # Duplikat
        response = http_client.post(f"{SERVICE_A_URL}/results", json=result_data)
        assert response.status_code == 409
    def test_nonexistent_result(self, http_client):
        """Test pobierania nieistniejacego wyniku"""
        response = http_client.get(f"{SERVICE_A_URL}/results/nonexistent-task-12345")
        assert response.status_code == 404
class TestE2EStats:
    """Testy statystyk"""
    def test_service_a_stats(self, http_client):
        """Test endpointu statystyk Service A"""
        response = http_client.get(f"{SERVICE_A_URL}/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_results" in data
        assert isinstance(data["total_results"], int)
