from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Dict, List

import isodate
import numpy as np

logger = logging.getLogger(__name__)


def _parse_int(value) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def _safe_ratio(num: float, denom: float) -> float:
    return float(num / denom) if denom else 0.0


def extract_metadata_features(snippet: Dict, statistics: Dict) -> List[float]:
    duration_iso = statistics.get("duration") or snippet.get("contentDetails", {}).get("duration")
    try:
        duration_seconds = isodate.parse_duration(duration_iso).total_seconds() if duration_iso else 0.0
    except Exception:
        duration_seconds = 0.0

    views = _parse_int(statistics.get("viewCount"))
    likes = _parse_int(statistics.get("likeCount"))
    comments = _parse_int(statistics.get("commentCount"))
    like_ratio = _safe_ratio(likes, views)

    published_at = snippet.get("publishedAt") or statistics.get("publishedAt")
    age_seconds = 0.0
    if published_at:
        try:
            published_dt = isodate.parse_datetime(published_at)
            age_seconds = (datetime.now(timezone.utc) - published_dt).total_seconds()
        except Exception:
            logger.debug("Failed to parse publishedAt: %s", published_at)

    # Simple normalization
    norm_views = np.log1p(views) / 20.0
    norm_likes = np.log1p(likes) / 20.0
    norm_comments = np.log1p(comments) / 15.0
    norm_duration = float(duration_seconds / 3600.0)  # hours
    norm_age = float(age_seconds / (3600 * 24 * 365))  # years

    return [
        float(norm_views),
        float(norm_likes),
        float(norm_comments),
        float(like_ratio),
        float(norm_duration),
        float(norm_age),
    ]
