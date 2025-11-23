from __future__ import annotations

import logging
from pathlib import Path
from typing import Tuple

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report

logger = logging.getLogger(__name__)


def train_and_save(
    name: str,
    X: np.ndarray,
    y: np.ndarray,
    model_path: Path,
    scaler_path: Path,
    test_size: float = 0.2,
) -> Tuple[RandomForestClassifier, StandardScaler]:
    logger.info("Training %s classifier on %s samples", name, len(X))
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=test_size, random_state=42)
    model = RandomForestClassifier(n_estimators=80, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    logger.info("%s evaluation:\n%s", name, classification_report(y_test, preds, zero_division=0))

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    logger.info("Saved %s model to %s", name, model_path)
    return model, scaler
