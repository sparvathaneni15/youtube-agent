from __future__ import annotations

import logging
from functools import lru_cache
from io import BytesIO
from typing import Dict, Tuple

import cv2
import numpy as np
import requests
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

logger = logging.getLogger(__name__)

CLIP_MODEL_NAME = "openai/clip-vit-base-patch32"


@lru_cache(maxsize=1)
def _load_clip() -> Tuple[CLIPModel, CLIPProcessor]:
    logger.info("Loading CLIP model %s", CLIP_MODEL_NAME)
    model = CLIPModel.from_pretrained(CLIP_MODEL_NAME)
    processor = CLIPProcessor.from_pretrained(CLIP_MODEL_NAME)
    return model, processor


def _download_image(url: str) -> Image.Image:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return Image.open(BytesIO(response.content)).convert("RGB")


def _face_count(np_image: np.ndarray) -> int:
    gray = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)
    classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = classifier.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    return int(len(faces))


def _saturation(np_image: np.ndarray) -> float:
    hsv = cv2.cvtColor(np_image, cv2.COLOR_RGB2HSV)
    return float(np.mean(hsv[:, :, 1]) / 255.0)


def _text_density(np_image: np.ndarray) -> float:
    gray = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    return float(np.mean(edges) / 255.0)


def _brightness(np_image: np.ndarray) -> float:
    hsv = cv2.cvtColor(np_image, cv2.COLOR_RGB2HSV)
    return float(np.mean(hsv[:, :, 2]) / 255.0)


def extract_thumbnail_features(url: str) -> Tuple[np.ndarray, Dict[str, float]]:
    try:
        image = _download_image(url)
        np_image = np.array(image)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to download thumbnail; returning zeros: %s", exc)
        return np.zeros(512, dtype=np.float32), {
            "face_count": 0.0,
            "saturation": 0.0,
            "text_density": 0.0,
            "brightness": 0.0,
        }

    try:
        model, processor = _load_clip()
        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            embeddings = model.get_image_features(**inputs)
        clip_emb = embeddings[0].detach().cpu().numpy().astype(np.float32)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("CLIP embedding failed; returning zeros: %s", exc)
        clip_emb = np.zeros(512, dtype=np.float32)

    signals = {
        "face_count": float(_face_count(np_image)),
        "saturation": _saturation(np_image),
        "text_density": _text_density(np_image),
        "brightness": _brightness(np_image),
    }
    return clip_emb, signals
