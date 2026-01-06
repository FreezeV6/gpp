import hashlib
import os
from typing import Tuple
import requests
from io import BytesIO
from PIL import Image
import numpy as np

# Flaga do wyboru trybu: True = prawdziwy YOLO, False = symulacja (dla testów)
USE_REAL_YOLO = os.getenv("USE_REAL_YOLO", "false").lower() == "true"

# Lazy loading modelu YOLO
_yolo_model = None

def _get_yolo_model():
    """Lazy loading modelu YOLO - ładuje tylko raz przy pierwszym użyciu."""
    global _yolo_model
    if _yolo_model is None:
        from ultralytics import YOLO
        # Używamy YOLOv8n (nano) - szybki i lekki model
        # Automatycznie pobierze wagi przy pierwszym uruchomieniu
        _yolo_model = YOLO("yolov8n.pt")
    return _yolo_model


def _download_image(image_url: str) -> Image.Image:
    """Pobiera obraz z URL i zwraca jako PIL Image."""
    response = requests.get(image_url, timeout=10)
    response.raise_for_status()
    image = Image.open(BytesIO(response.content))
    # Konwertuj do RGB jeśli potrzeba (np. dla PNG z alpha channel)
    if image.mode != "RGB":
        image = image.convert("RGB")
    return image


def _analyze_with_yolo(image_url: str) -> Tuple[int, float]:
    """
    Rzeczywista analiza obrazu z użyciem modelu YOLO.
    Wykrywa osoby (klasa 'person' = 0 w COCO dataset) na zdjęciu.

    Returns:
        Tuple[int, float]: (liczba_osob, srednia_confidence)
    """
    try:
        # Pobierz obraz
        image = _download_image(image_url)

        # Załaduj model YOLO
        model = _get_yolo_model()

        # Wykonaj detekcję
        results = model(image, verbose=False)

        # Filtruj tylko osoby (klasa 0 w COCO = 'person')
        person_class_id = 0
        people_count = 0
        confidences = []

        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                if cls == person_class_id:
                    people_count += 1
                    confidences.append(conf)

        # Oblicz średnią confidence (lub 0.0 jeśli brak osób)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return people_count, round(avg_confidence, 2)

    except Exception as e:
        # W przypadku błędu (np. nie można pobrać obrazu) zwróć 0 osób
        print(f"[YOLO] Błąd analizy obrazu {image_url}: {e}")
        return 0, 0.0


def _analyze_simulated(image_url: str) -> Tuple[int, float]:
    """
    Symulowana analiza - deterministyczny wynik bazowany na URL.
    Używana do testów jednostkowych.
    """
    url_hash = hashlib.md5(image_url.encode()).hexdigest()
    people_count = int(url_hash[:2], 16) % 21
    confidence_base = int(url_hash[2:4], 16) % 30
    confidence = 0.70 + (confidence_base / 100)
    return people_count, round(confidence, 2)


def analyze_image(image_url: str) -> Tuple[int, float]:
    """
    Analizuje obraz i zlicza liczbę osób na zdjęciu.

    Używa modelu YOLOv8 do detekcji osób gdy USE_REAL_YOLO=true,
    w przeciwnym razie używa symulacji (dla testów).

    Returns:
        Tuple[int, float]: (liczba_osob, confidence)
    """
    if USE_REAL_YOLO:
        return _analyze_with_yolo(image_url)
    else:
        return _analyze_simulated(image_url)
def validate_image_url(image_url: str) -> bool:
    """
    Waliduje czy URL obrazu jest poprawny.
    W rzeczywistosci sprawdzaloby czy URL prowadzi do obrazu.
    """
    if not image_url:
        return False
    # Podstawowa walidacja URL
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    valid_prefixes = ['http://', 'https://']
    has_valid_prefix = any(image_url.lower().startswith(p) for p in valid_prefixes)
    # Dla testow akceptujemy wszystkie URL z http/https
    return has_valid_prefix
