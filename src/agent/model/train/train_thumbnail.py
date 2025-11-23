from __future__ import annotations

import logging

import numpy as np

from agent.config import MODELS_DIR
from agent.model.train.utils import train_and_save

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FEATURE_DIM = 522  # 512 clip + 4 signals + 6 metadata


def build_synthetic_dataset(samples: int = 400):
    rng = np.random.default_rng(3)
    pos = rng.normal(loc=0.3, scale=0.05, size=(samples // 2, FEATURE_DIM))
    neg = rng.normal(loc=0.7, scale=0.05, size=(samples // 2, FEATURE_DIM))
    # For thumbnail clickbait, lower is better; invert labels
    X = np.vstack([pos, neg])
    y = np.array([0] * (samples // 2) + [1] * (samples // 2))
    return X, y


def main():
    X, y = build_synthetic_dataset()
    train_and_save(
        name="thumbnail",
        X=X,
        y=y,
        model_path=MODELS_DIR / "thumbnail_classifier.pkl",
        scaler_path=MODELS_DIR / "thumbnail_scaler.pkl",
    )


if __name__ == "__main__":
    main()
