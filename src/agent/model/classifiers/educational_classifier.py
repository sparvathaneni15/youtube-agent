from __future__ import annotations

from pathlib import Path

from agent.config import MODELS_DIR
from agent.model.classifiers.base import BaseClassifier


class EducationalClassifier(BaseClassifier):
    def __init__(self):
        super().__init__(
            model_path=Path(MODELS_DIR) / "educational_classifier.pkl",
            scaler_path=Path(MODELS_DIR) / "educational_scaler.pkl",
            fallback=0.6,
        )


def get_classifier() -> EducationalClassifier:
    return EducationalClassifier()
