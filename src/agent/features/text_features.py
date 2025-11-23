from __future__ import annotations

import logging
import re
from functools import lru_cache
from typing import Optional

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"


def clean_text(text: Optional[str]) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"\s+", " ", text)
    return cleaned.strip()


@lru_cache(maxsize=1)
def _load_model() -> SentenceTransformer:
    logger.info("Loading text encoder %s", MODEL_NAME)
    return SentenceTransformer(MODEL_NAME)


def extract_text_features(title: str, description: str = "") -> np.ndarray:
    text = clean_text(f"{title}\n{description}")
    if not text:
        return np.zeros(384, dtype=np.float32)
    try:
        model = _load_model()
        embedding = model.encode(text, normalize_embeddings=True)
        return np.asarray(embedding, dtype=np.float32)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Falling back to zeros for text features: %s", exc)
        return np.zeros(384, dtype=np.float32)
