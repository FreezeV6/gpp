import random
import hashlib
import time
from typing import Tuple
def analyze_image(image_url: str) -> Tuple[int, float]:
    """
    Symuluje algorytm AI do liczenia osob na zdjeciu.
    W rzeczywistosci tutaj bylby model ML (np. YOLO, OpenCV DNN).
    Returns:
        Tuple[int, float]: (liczba_osob, confidence)
    """
    # Symulacja czasu przetwarzania (0.5-2 sekundy)
    processing_time = random.uniform(0.5, 2.0)
    time.sleep(processing_time)
    # Deterministyczny wynik bazowany na URL (dla powtarzalnosci testow)
    url_hash = hashlib.md5(image_url.encode()).hexdigest()
    # Liczba osob: 0-20 bazowane na hash
    people_count = int(url_hash[:2], 16) % 21
    # Confidence: 0.70 - 0.99
    confidence_base = int(url_hash[2:4], 16) % 30
    confidence = 0.70 + (confidence_base / 100)
    return people_count, round(confidence, 2)
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
