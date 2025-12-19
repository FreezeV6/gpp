import pika
import os
import json
import time
from typing import Optional

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
QUEUE_NAME = "image_analysis_queue"
RESULT_QUEUE_NAME = "result_queue"


def get_connection(max_retries: int = 5, retry_delay: float = 2.0) -> pika.BlockingConnection:
    """Tworzy połączenie z RabbitMQ z retry logic"""
    params = pika.URLParameters(RABBITMQ_URL)

    for attempt in range(max_retries):
        try:
            connection = pika.BlockingConnection(params)
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            if attempt < max_retries - 1:
                print(f"Nie można połączyć z RabbitMQ (próba {attempt + 1}/{max_retries}), ponawiam za {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                raise e
    raise Exception("Nie można połączyć z RabbitMQ po maksymalnej liczbie prób")


def get_channel() -> pika.adapters.blocking_connection.BlockingChannel:
    """Tworzy kanał i deklaruje kolejki"""
    connection = get_connection()
    channel = connection.channel()

    # Deklaracja głównej kolejki do analizy
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    # Deklaracja kolejki dla wyników (z retry)
    channel.queue_declare(queue=RESULT_QUEUE_NAME, durable=True)

    return channel


def publish_task(task_data: dict) -> bool:
    """Publikuje zadanie do kolejki"""
    try:
        connection = get_connection()
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=json.dumps(task_data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Persistent
                content_type='application/json'
            )
        )
        connection.close()
        return True
    except Exception as e:
        print(f"Błąd podczas publikowania zadania: {e}")
        return False


def publish_result(result_data: dict) -> bool:
    """Publikuje wynik do kolejki wyników (dla retry strategy)"""
    try:
        connection = get_connection()
        channel = connection.channel()
        channel.queue_declare(queue=RESULT_QUEUE_NAME, durable=True)

        channel.basic_publish(
            exchange='',
            routing_key=RESULT_QUEUE_NAME,
            body=json.dumps(result_data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Persistent
                content_type='application/json'
            )
        )
        connection.close()
        return True
    except Exception as e:
        print(f"Błąd podczas publikowania wyniku: {e}")
        return False


def check_rabbitmq_connection() -> bool:
    """Sprawdza czy RabbitMQ jest dostępny"""
    try:
        connection = get_connection(max_retries=1, retry_delay=0.5)
        connection.close()
        return True
    except:
        return False

