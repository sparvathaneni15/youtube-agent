from __future__ import annotations

import json
import logging
import os
from typing import Dict, Tuple

import requests

from agent.model import heuristics

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a selective YouTube assistant. Score each video for learning value on [0,1]. "
    "Prefer technical depth, clarity, credible sources, and practical insight. Penalize clickbait, gossip, or fluff."
)


def _heuristic_score(ctx: Dict) -> Tuple[float, str]:
    text = f"{ctx.get('title', '')} {ctx.get('description_summary', '')}"
    thumb_score = heuristics.thumbnail_quality_heuristic(ctx.get("thumbnail_signals", {}))
    educational_hint = ctx.get("text_signals", {}).get("educational_hint", 0.0)
    topic_hint = ctx.get("text_signals", {}).get("topic_hint", 0.0)
    clickbait_prob = ctx.get("perceived_scores", {}).get("clickbait_prob", 0.5)
    base = 0.2 + 0.4 * educational_hint + 0.2 * topic_hint + 0.2 * thumb_score
    penalty = 0.3 * clickbait_prob
    score = max(0.0, min(1.0, base - penalty))
    return score, "Heuristic fallback score with clickbait penalty"


def score_with_llm(video_context: Dict) -> Tuple[float, str]:
    endpoint = os.getenv("LLM_ENDPOINT")
    if not endpoint:
        return _heuristic_score(video_context)

    payload = {
        "model": "local-llm",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": "Given this video metadata, return JSON with 'value_score' (0-1) and 'reason'.\n"
                + json.dumps(video_context, ensure_ascii=False),
            },
        ],
    }
    try:
        resp = requests.post(endpoint, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict) and "choices" in data:
            # OpenAI chat format
            message = data["choices"][0]["message"]["content"]
            try:
                parsed = json.loads(message)
            except Exception:
                parsed = data
        else:
            parsed = data
        score = float(parsed.get("value_score"))
        reason = str(parsed.get("reason", ""))
        return score, reason
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("LLM scoring failed; using heuristic: %s", exc)
        return _heuristic_score(video_context)
