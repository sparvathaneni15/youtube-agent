from __future__ import annotations

from pathlib import Path

from agent.config import MODELS_DIR
from agent.model.classifiers.base import BaseClassifier


class ClickbaitClassifier(BaseClassifier):
    def __init__(self):
        super().__init__(
            model_path=Path(MODELS_DIR) / "clickbait_classifier.pkl",
            scaler_path=Path(MODELS_DIR) / "clickbait_scaler.pkl",
            fallback=0.4,
        )


def get_classifier() -> ClickbaitClassifier:
    return ClickbaitClassifier()
