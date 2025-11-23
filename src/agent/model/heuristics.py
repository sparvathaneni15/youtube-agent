"""Lightweight heuristic scores used when models are unavailable."""
from __future__ import annotations

import math
import re
from typing import Dict, Optional


def keyword_score(text: str, keywords: Optional[list[str]] = None) -> float:
    if not text:
        return 0.0
    keywords = keywords or []
    lowered = text.lower()
    hits = sum(1 for kw in keywords if kw in lowered)
    return min(1.0, hits / max(1, len(keywords)))


def clickbait_heuristic(title: str, description: str) -> float:
    patterns = [
        r"won't believe",
        r"shocking",
        r"secret",
        r"surprising",
        r"what happens next",
        r"top \d+",
        r"crazy",
    ]
    combined = f"{title} {description}".lower()
    score = sum(bool(re.search(p, combined)) for p in patterns) / len(patterns)
    return float(score)


def educational_heuristic(title: str, description: str) -> float:
    patterns = [
        "tutorial",
        "how to",
        "guide",
        "explained",
        "introduction",
        "lesson",
        "walkthrough",
    ]
    return keyword_score(f"{title} {description}", patterns)


def topic_match_heuristic(title: str, allowed_topics: Optional[list[str]] = None) -> float:
    allowed_topics = allowed_topics or ["machine learning", "math", "systems", "python"]
    return keyword_score(title, allowed_topics)


def thumbnail_quality_heuristic(thumbnail_signals: Dict[str, float]) -> float:
    faces = thumbnail_signals.get("face_count", 0.0)
    saturation = thumbnail_signals.get("saturation", 0.0)
    text_density = thumbnail_signals.get("text_density", 0.0)
    brightness = thumbnail_signals.get("brightness", 0.0)
    face_penalty = 0.0 if faces < 3 else 0.3
    base = 0.5 * (1 - face_penalty)
    bonus = 0.25 * saturation + 0.15 * (1 - text_density) + 0.1 * brightness
    return max(0.0, min(1.0, base + bonus))


def safe_sigmoid(x: float) -> float:
    if math.isinf(x):
        return 1.0 if x > 0 else 0.0
    return 1 / (1 + math.exp(-x))
