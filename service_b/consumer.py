import pika
import json
import os
import time
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ai_processor import analyze_image
from rabbitmq_client import get_connection, QUEUE_NAME, RESULT_QUEUE_NAME

SERVICE_A_URL = os.getenv("SERVICE_A_URL", "http://localhost:8001")
CONSUMER_ID = os.getenv("HOSTNAME", f"consumer-{os.getpid()}")


class ServiceAClient:
    """Klient do komunikacji z Serwisem A z retry strategy"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.timeout = 30.0

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException))
    )
    def send_result(self, result_data: dict) -> bool:
        """
        Wysyła wynik do Serwisu A z retry strategy.
        Obsługuje chwilowe przestoje i błędy Cloudflare.
        """
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}/results",
                json=result_data
            )

            # Cloudflare errors (520-530) lub 5xx - retry
            if response.status_code >= 500:
                raise httpx.HTTPError(f"Server error: {response.status_code}")

            # 409 Conflict - już istnieje, traktuj jako sukces
            if response.status_code == 409:
                print(f"[{CONSUMER_ID}] Wynik dla {result_data['task_id']} już istnieje w Serwisie A")
                return True

            response.raise_for_status()
            return True


def process_message(ch, method, properties, body):
    """Przetwarza wiadomość z kolejki"""
    try:
        task_data = json.loads(body)
        task_id = task_data.get("task_id")
        image_url = task_data.get("image_url")

        print(f"[{CONSUMER_ID}] Przetwarzam zadanie: {task_id}")
        print(f"[{CONSUMER_ID}] URL obrazu: {image_url}")

        # Analizuj obraz (symulacja AI)
        people_count, confidence = analyze_image(image_url)

        print(f"[{CONSUMER_ID}] Wynik: {people_count} osób, confidence: {confidence}")

        # Przygotuj wynik
        result_data = {
            "task_id": task_id,
            "image_url": image_url,
            "people_count": people_count,
            "confidence": confidence,
            "status": "completed"
        }

        # Wyślij wynik do Serwisu A z retry
        service_a_client = ServiceAClient(SERVICE_A_URL)
        try:
            service_a_client.send_result(result_data)
            print(f"[{CONSUMER_ID}] ✓ Wynik wysłany do Serwisu A: {task_id}")
            # ACK tylko po pomyślnym wysłaniu
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"[{CONSUMER_ID}] ✗ Nie udało się wysłać wyniku po wszystkich próbach: {e}")
            # NACK - wiadomość wróci do kolejki
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    except json.JSONDecodeError as e:
        print(f"[{CONSUMER_ID}] ✗ Błąd parsowania JSON: {e}")
        # Uszkodzona wiadomość - odrzuć bez requeue
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        print(f"[{CONSUMER_ID}] ✗ Błąd przetwarzania: {e}")
        # Requeue dla innych błędów
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def main():
    print(f"[{CONSUMER_ID}] Uruchamiam konsumenta...")

    while True:
        try:
            connection = get_connection(max_retries=10, retry_delay=3.0)
            channel = connection.channel()

            # Deklaruj kolejkę
            channel.queue_declare(queue=QUEUE_NAME, durable=True)

            # Pobieraj max 1 wiadomość na raz (fair dispatch)
            channel.basic_qos(prefetch_count=1)

            # Auto-ack = False dla retry strategy
            channel.basic_consume(
                queue=QUEUE_NAME,
                on_message_callback=process_message,
                auto_ack=False
            )

            print(f"[{CONSUMER_ID}] ✓ Połączono z RabbitMQ. Oczekuję na zadania...")
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            print(f"[{CONSUMER_ID}] Utracono połączenie z RabbitMQ: {e}")
            print(f"[{CONSUMER_ID}] Ponawiam połączenie za 5 sekund...")
            time.sleep(5)
        except KeyboardInterrupt:
            print(f"[{CONSUMER_ID}] Zatrzymuję konsumenta...")
            break
        except Exception as e:
            print(f"[{CONSUMER_ID}] Nieoczekiwany błąd: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()

