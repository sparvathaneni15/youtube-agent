from __future__ import annotations

import logging

import numpy as np

from agent.config import MODELS_DIR
from agent.model.train.utils import train_and_save

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FEATURE_DIM = 390


def build_synthetic_dataset(samples: int = 400):
    rng = np.random.default_rng(1)
    # Educational videos are smoother/steadier feature space
    pos = rng.normal(loc=0.4, scale=0.05, size=(samples // 2, FEATURE_DIM))
    neg = rng.normal(loc=0.1, scale=0.05, size=(samples // 2, FEATURE_DIM))
    X = np.vstack([pos, neg])
    y = np.array([1] * (samples // 2) + [0] * (samples // 2))
    return X, y


def main():
    X, y = build_synthetic_dataset()
    train_and_save(
        name="educational",
        X=X,
        y=y,
        model_path=MODELS_DIR / "educational_classifier.pkl",
        scaler_path=MODELS_DIR / "educational_scaler.pkl",
    )


if __name__ == "__main__":
    main()
