from __future__ import annotations

import logging

from googleapiclient.errors import HttpError

from agent.youtube_client import get_youtube_client

logger = logging.getLogger(__name__)

WATCH_LATER_ID = "WL"


def add_to_watch_later(video_id: str) -> bool:
    youtube = get_youtube_client()
    body = {
        "snippet": {
            "playlistId": WATCH_LATER_ID,
            "resourceId": {"kind": "youtube#video", "videoId": video_id},
        }
    }
    try:
        youtube.playlistItems().insert(part="snippet", body=body).execute()
        logger.info("Added %s to Watch Later", video_id)
        return True
    except HttpError as exc:  # pragma: no cover - external
        logger.warning("Failed to add %s to Watch Later: %s", video_id, exc)
        return False
