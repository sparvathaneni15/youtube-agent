from __future__ import annotations

from pathlib import Path

from agent.config import MODELS_DIR
from agent.model.classifiers.base import BaseClassifier


class ThumbnailClassifier(BaseClassifier):
    def __init__(self):
        super().__init__(
            model_path=Path(MODELS_DIR) / "thumbnail_classifier.pkl",
            scaler_path=Path(MODELS_DIR) / "thumbnail_scaler.pkl",
            fallback=0.5,
        )


def get_classifier() -> ThumbnailClassifier:
    return ThumbnailClassifier()
