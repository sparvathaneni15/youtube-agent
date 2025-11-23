from __future__ import annotations

import logging

import numpy as np

from agent.config import MODELS_DIR
from agent.model.train.utils import train_and_save

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FEATURE_DIM = 390  # 384 text + 6 metadata


def build_synthetic_dataset(samples: int = 400):
    rng = np.random.default_rng(0)
    # Positive: higher variance and higher values on early dimensions to mimic provocative wording
    pos = rng.normal(loc=0.6, scale=0.1, size=(samples // 2, FEATURE_DIM))
    neg = rng.normal(loc=0.2, scale=0.05, size=(samples // 2, FEATURE_DIM))
    X = np.vstack([pos, neg])
    y = np.array([1] * (samples // 2) + [0] * (samples // 2))
    return X, y


def main():
    X, y = build_synthetic_dataset()
    train_and_save(
        name="clickbait",
        X=X,
        y=y,
        model_path=MODELS_DIR / "clickbait_classifier.pkl",
        scaler_path=MODELS_DIR / "clickbait_scaler.pkl",
    )


if __name__ == "__main__":
    main()
