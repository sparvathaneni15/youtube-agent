from __future__ import annotations

import logging
from typing import Dict, Optional

import numpy as np

from agent.features.metadata_features import extract_metadata_features
from agent.features.text_features import extract_text_features
from agent.features.thumbnail_features import extract_thumbnail_features
from agent.model import heuristics
from agent.model.classifiers.load_classifiers import load_classifiers
from agent.model.predict_labels import predict_labels

logger = logging.getLogger(__name__)


def _description_summary(text: str, limit: int = 240) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def build_attributes(video: Dict, classifiers: Optional[Dict[str, object]] = None) -> Dict:
    snippet = video.get("snippet", {})
    statistics = video.get("statistics", {})
    title = snippet.get("title", "")
    description = snippet.get("description", "")
    channel_title = snippet.get("channelTitle", "")

    text_vec = extract_text_features(title, description)
    thumb_url = (
        snippet.get("thumbnails", {}).get("high", {}).get("url")
        or snippet.get("thumbnails", {}).get("default", {}).get("url")
    )
    if thumb_url:
        thumb_vec, thumb_signals = extract_thumbnail_features(thumb_url)
    else:
        thumb_vec = np.zeros(512, dtype=np.float32)
        thumb_signals = {"face_count": 0.0, "saturation": 0.0, "text_density": 0.0, "brightness": 0.0}

    meta_vec = np.asarray(extract_metadata_features(snippet, statistics), dtype=np.float32)
    thumbnail_signal_vec = np.asarray(list(thumb_signals.values()), dtype=np.float32)

    clf = classifiers or load_classifiers()
    perceived_scores = predict_labels(
        {
            "text": text_vec,
            "thumbnail": thumb_vec,
            "metadata": meta_vec,
            "thumbnail_signals": thumbnail_signal_vec,
        },
        clf,
    )

    video_context = {
        "video_id": video.get("id") or video.get("videoId"),
        "title": title,
        "description_summary": _description_summary(description),
        "channel": {
            "title": channel_title,
            "id": snippet.get("channelId"),
        },
        "stats": {
            "view_count": statistics.get("viewCount"),
            "like_count": statistics.get("likeCount"),
            "comment_count": statistics.get("commentCount"),
            "duration": statistics.get("duration") or snippet.get("contentDetails", {}).get("duration"),
            "published_at": snippet.get("publishedAt"),
        },
        "thumbnail_signals": thumb_signals,
        "text_signals": {
            "clickbait_hint": heuristics.clickbait_heuristic(title, description),
            "educational_hint": heuristics.educational_heuristic(title, description),
            "topic_hint": heuristics.topic_match_heuristic(title),
        },
        "perceived_scores": perceived_scores,
    }
    return video_context
