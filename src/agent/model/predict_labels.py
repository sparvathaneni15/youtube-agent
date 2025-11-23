from __future__ import annotations

from typing import Dict, Iterable

import numpy as np


def predict_labels(perception_vectors: Dict[str, Iterable[float]], classifiers: Dict[str, object]) -> Dict[str, float]:
    text_vec = np.asarray(perception_vectors.get("text"), dtype=float)
    thumb_vec = np.asarray(perception_vectors.get("thumbnail"), dtype=float)
    meta_vec = np.asarray(perception_vectors.get("metadata"), dtype=float)
    thumb_signals_vec = np.asarray(perception_vectors.get("thumbnail_signals"), dtype=float)

    clickbait_features = np.concatenate([text_vec, meta_vec]) if text_vec.size and meta_vec.size else text_vec
    educational_features = np.concatenate([text_vec, meta_vec]) if text_vec.size and meta_vec.size else text_vec
    topic_features = text_vec
    thumbnail_features = np.concatenate([thumb_vec, thumb_signals_vec, meta_vec]) if thumb_vec.size else thumb_signals_vec

    return {
        "clickbait_prob": classifiers["clickbait"].predict_proba(clickbait_features),
        "educational_prob": classifiers["educational"].predict_proba(educational_features),
        "topic_relevance": classifiers["topic"].predict_proba(topic_features),
        "thumbnail_clickbait_prob": classifiers["thumbnail"].predict_proba(thumbnail_features),
    }
