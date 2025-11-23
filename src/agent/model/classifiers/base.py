from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, Optional

import joblib
import numpy as np

logger = logging.getLogger(__name__)


class BaseClassifier:
    """Wrapper that loads a scaler + classifier and predicts probabilities."""

    def __init__(self, model_path: Path, scaler_path: Path, fallback: float = 0.5):
        self.model_path = Path(model_path)
        self.scaler_path = Path(scaler_path)
        self.fallback = float(fallback)
        self.model = None
        self.scaler = None
        self._load()

    def _load(self) -> None:
        try:
            if self.model_path.exists() and self.model_path.stat().st_size > 0:
                self.model = joblib.load(self.model_path)
            if self.scaler_path.exists() and self.scaler_path.stat().st_size > 0:
                self.scaler = joblib.load(self.scaler_path)
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Failed to load classifier artifacts: %s", exc)
            self.model = None
            self.scaler = None

    def is_trained(self) -> bool:
        return self.model is not None and self.scaler is not None

    def predict_proba(self, features: Iterable[float]) -> float:
        array = np.asarray(list(features), dtype=np.float32).reshape(1, -1)
        if not self.is_trained():
            return self.fallback
        try:
            scaled = self.scaler.transform(array)
            proba = self.model.predict_proba(scaled)[0, 1]
            return float(proba)
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Prediction failed; using fallback: %s", exc)
            return self.fallback
