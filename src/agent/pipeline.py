from __future__ import annotations

import logging
from typing import Dict, List

from agent.attributes import build_attributes
from agent.config import DEFAULT_SCORE_THRESHOLD
from config.allow_block_lists import ALLOW_CHANNELS, BLOCK_CHANNELS, BLOCK_KEYWORDS
from agent.fetch_candidates import get_candidate_videos
from agent.llm_scorer import score_with_llm
from agent.model.classifiers.load_classifiers import load_classifiers
from agent.playlist_writer import add_to_watch_later

logger = logging.getLogger(__name__)


def run_pipeline(score_threshold: float = DEFAULT_SCORE_THRESHOLD, auto_watch_later: bool = True) -> List[Dict]:
    candidates = get_candidate_videos()
    classifiers = load_classifiers()
    accepted: List[Dict] = []
    blocked_channels = {c.lower() for c in BLOCK_CHANNELS}
    allow_channels = {c.lower() for c in ALLOW_CHANNELS}
    for video in candidates:
        ctx = build_attributes(video, classifiers)
        channel_title = (ctx.get("channel") or {}).get("title", "").lower()
        title = (ctx.get("title") or "").lower()
        if channel_title in blocked_channels:
            logger.info("Skipping blocked channel: %s", channel_title)
            continue
        if BLOCK_KEYWORDS and any(kw.lower() in title for kw in BLOCK_KEYWORDS):
            logger.info("Skipping due to blocked keyword for: %s", title)
            continue
        if channel_title in allow_channels:
            ctx.setdefault("text_signals", {})["educational_hint"] = min(
                1.0, ctx.get("text_signals", {}).get("educational_hint", 0.0) + 0.2
            )
        score, reason = score_with_llm(ctx)
        logger.info("[%s] \u2192 LLM score %.3f | reason: %s", ctx.get("title"), score, reason)
        if score >= score_threshold:
            ctx["value_score"] = score
            ctx["llm_reason"] = reason
            accepted.append(ctx)
            if auto_watch_later and ctx.get("video_id"):
                add_to_watch_later(ctx["video_id"])
    return accepted
