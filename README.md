# AI Services - Microservices Architecture

## Opis projektu

Projekt składa się z dwóch mikroserwisów komunikujących się przez RabbitMQ:

- **Service A** - API do przechowywania wyników analizy AI
- **Service B** - API z algorytmem AI do liczenia osób na zdjęciach

## Architektura

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Klient     │────▶│  Service B   │────▶│  RabbitMQ   │
│             │     │  (Port 8002) │     │  (Queue)    │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                │
                                                ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Service A  │◀────│  Consumer    │◀────│  Consumer   │
│  (Port 8001)│     │  (replica 1) │     │  (replica N)│
└─────────────┘     └──────────────┘     └─────────────┘
```

## Wymagania

- Docker
- Docker Compose

## Uruchomienie

### 1. Uruchomienie wszystkich serwisów

```bash
docker compose up -d
```

### 2. Skalowanie consumerów

```bash
docker compose up -d --scale consumer=5
```

### 3. Sprawdzenie statusu

```bash
docker compose ps
```

## Endpointy

### Service A (Port 8001)

| Metoda | Endpoint | Opis |
|--------|----------|------|
| GET | `/health` | Health check |
| POST | `/results` | Zapisz wynik analizy |
| GET | `/results` | Pobierz wszystkie wyniki |
| GET | `/results/{task_id}` | Pobierz wynik po ID |
| DELETE | `/results/{task_id}` | Usuń wynik |
| GET | `/stats` | Statystyki |

### Service B (Port 8002)

| Metoda | Endpoint | Opis |
|--------|----------|------|
| GET | `/health` | Health check |
| POST | `/analyze` | Kolejkuj analizę obrazu |
| POST | `/analyze/sync` | Synchroniczna analiza |
| GET | `/queue/status` | Status kolejki RabbitMQ |

## Przykłady użycia

### Kolejkowanie analizy obrazu

```bash
curl -X POST http://localhost:8002/analyze \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/image.jpg"}'
```

### Synchroniczna analiza

```bash
curl -X POST http://localhost:8002/analyze/sync \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/image.jpg"}'
```

### Pobieranie wyników

```bash
curl http://localhost:8001/results
```

## Testy

### Testy jednostkowe i integracyjne

```bash
./run_unit_tests.sh
```

### Testy E2E (wymagają uruchomionych serwisów)

```bash
docker compose up -d
./run_e2e_tests.sh
```

## RabbitMQ Management

Panel zarządzania RabbitMQ dostępny pod adresem:
- URL: http://localhost:15672
- Login: guest
- Hasło: guest

## Retry Strategy

Consumer implementuje strategię retry dla wysyłania wyników do Service A:

1. **auto_ack=false** - wiadomość nie jest usuwana z kolejki dopóki nie zostanie pomyślnie przetworzona
2. **tenacity retry** - 5 prób z exponential backoff (2-30 sekund)
3. **NACK z requeue** - w przypadku niepowodzenia wiadomość wraca do kolejki

## Struktura projektu

```
├── docker-compose.yml
├── service_a/
│   ├── Dockerfile
│   ├── main.py
│   ├── database.py
│   ├── schemas.py
│   ├── requirements.txt
│   └── test_integration.py
├── service_b/
│   ├── Dockerfile
│   ├── Dockerfile.consumer
│   ├── main.py
│   ├── consumer.py
│   ├── ai_processor.py
│   ├── rabbitmq_client.py
│   ├── schemas.py
│   ├── requirements.txt
│   └── test_integration.py
└── tests/
    ├── test_e2e.py
    └── requirements.txt
```

