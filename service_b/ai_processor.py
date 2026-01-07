import hashlib
import os
from typing import Tuple

import cv2
import numpy as np
import imutils
import requests

USE_REAL_MODEL = os.getenv("USE_REAL_MODEL", "false").lower() == "true"


def process_img(image: cv2.typing.MatLike) -> int:
    """Count people in image using HOG detector."""
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())  # type: ignore
    MAX_WIDTH = 1500
    if image.shape[0] > MAX_WIDTH:
        ratio = image.shape[0] / MAX_WIDTH
        image = imutils.resize(image, width=MAX_WIDTH, height=int(image.shape[1] * ratio))
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    regions, weights = hog.detectMultiScale(
        gray, winStride=(2, 2), padding=(5, 5), scale=1.02
    )
    mean = np.mean(weights) if len(weights) > 0 else 0
    std = np.std(weights) if len(weights) > 0 else 0
    k = 0.86
    filtered_objects = []
    for index, weight in enumerate(weights):
        if weight >= (mean - k * std):
            filtered_objects.append(regions[index])
    return len(filtered_objects)


def _analyze_with_model(image_url: str) -> Tuple[int, float]:
    """Analyze image from URL and count people using HOG detector."""
    try:
        # Download image
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(image_url, timeout=15, headers=headers)
        resp.raise_for_status()

        # Decode
        image_array = np.asarray(bytearray(resp.content), dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Could not decode image")

        # Count people
        people_count = process_img(image)

        # Confidence based on detection
        confidence = 0.85 if people_count > 0 else 0.0

        return people_count, round(confidence, 2)

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[hog-detector] Error: {image_url}: {e}", flush=True)
        return 0, 0.0


def _analyze_simulated(image_url: str) -> Tuple[int, float]:
    """Simulated analysis for testing without real model."""
    url_hash = hashlib.md5(image_url.encode()).hexdigest()
    people_count = int(url_hash[:2], 16) % 21
    confidence_base = int(url_hash[2:4], 16) % 30
    confidence = 0.70 + (confidence_base / 100)
    return people_count, round(confidence, 2)


def analyze_image(image_url: str) -> Tuple[int, float]:
    """Main entry point for image analysis."""
    if USE_REAL_MODEL:
        return _analyze_with_model(image_url)
    else:
        return _analyze_simulated(image_url)


def validate_image_url(image_url: str) -> bool:
    """Validate that the URL is a valid image URL."""
    if not image_url:
        return False
    valid_prefixes = ['http://', 'https://']
    has_valid_prefix = any(image_url.lower().startswith(p) for p in valid_prefixes)
    return has_valid_prefix
