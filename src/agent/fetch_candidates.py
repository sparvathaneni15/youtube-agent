from __future__ import annotations

import logging
from typing import Dict, List, Set

from googleapiclient.errors import HttpError

from agent.config import MAX_CANDIDATES
from agent.youtube_client import get_youtube_client

logger = logging.getLogger(__name__)


def _fetch_video_details(youtube, video_ids: List[str]) -> List[Dict]:
    if not video_ids:
        return []
    resp = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=",".join(video_ids),
        maxResults=len(video_ids),
    ).execute()
    return resp.get("items", [])


def fetch_subscription_videos(limit: int = 10) -> List[Dict]:
    try:
        youtube = get_youtube_client()
        subs_resp = youtube.subscriptions().list(part="snippet", mine=True, maxResults=limit).execute()
        channel_ids = [item["snippet"]["resourceId"]["channelId"] for item in subs_resp.get("items", []) if item.get("snippet", {}).get("resourceId")]
        video_ids: List[str] = []
        for channel_id in channel_ids:
            search = youtube.search().list(channelId=channel_id, part="id", order="date", maxResults=1, type="video").execute()
            video_ids.extend([item["id"]["videoId"] for item in search.get("items", []) if "videoId" in item.get("id", {})])
        return _fetch_video_details(youtube, video_ids)
    except (HttpError, Exception) as exc:  # pragma: no cover - defensive
        logger.warning("Failed to fetch subscription videos: %s", exc)
    return []


def fetch_trending(limit: int = 10) -> List[Dict]:
    try:
        youtube = get_youtube_client()
        resp = youtube.videos().list(part="snippet,statistics,contentDetails", chart="mostPopular", maxResults=limit, regionCode="US").execute()
        return resp.get("items", [])
    except (HttpError, Exception) as exc:  # pragma: no cover - defensive
        logger.warning("Failed to fetch trending videos: %s", exc)
        return []


def fetch_related_to_liked(limit_per_video: int = 2, limit: int | None = None) -> List[Dict]:
    related: List[Dict] = []
    try:
        youtube = get_youtube_client()
        liked_resp = youtube.videos().list(part="snippet", myRating="like", maxResults=5).execute()
        liked_ids = [item.get("id") for item in liked_resp.get("items", []) if item.get("id")]
        for vid in liked_ids:
            search = youtube.search().list(part="id", type="video", relatedToVideoId=vid, maxResults=limit_per_video).execute()
            related_ids = [item["id"].get("videoId") for item in search.get("items", []) if item.get("id", {}).get("videoId")]
            related.extend(_fetch_video_details(youtube, related_ids))
    except (HttpError, Exception) as exc:  # pragma: no cover - defensive
        logger.warning("Failed to fetch related videos: %s", exc)
    return related


def _fallback_samples() -> List[Dict]:
    return [
        {
            "id": "sample1",
            "snippet": {
                "title": "Building a REST API with FastAPI",
                "description": "Walkthrough creating a production-ready REST API using FastAPI and Pydantic.",
                "channelTitle": "DevStack",
                "channelId": "devstack",
                "publishedAt": "2024-01-01T00:00:00Z",
                "thumbnails": {"high": {"url": "https://picsum.photos/seed/api/480/360"}},
                "contentDetails": {"duration": "PT12M30S"},
            },
            "statistics": {"viewCount": "12000", "likeCount": "1500", "commentCount": "120"},
        },
        {
            "id": "sample2",
            "snippet": {
                "title": "Top 10 unbelievable facts",
                "description": "You won't believe number 7!",
                "channelTitle": "ViralHub",
                "channelId": "viralhub",
                "publishedAt": "2024-01-03T00:00:00Z",
                "thumbnails": {"high": {"url": "https://picsum.photos/seed/top10/480/360"}},
                "contentDetails": {"duration": "PT8M"},
            },
            "statistics": {"viewCount": "980000", "likeCount": "22000", "commentCount": "3500"},
        },
    ]


def get_candidate_videos(limit: int = MAX_CANDIDATES) -> List[Dict]:
    seen: Set[str] = set()
    videos: List[Dict] = []
    for fetcher in (fetch_subscription_videos, fetch_trending):
        for video in fetcher(limit=limit // 3 or 1):
            vid = video.get("id") or video.get("videoId")
            if vid and vid not in seen:
                seen.add(vid)
                videos.append(video)
            if len(videos) >= limit:
                return videos
    related_limit = max(1, limit // 5)
    for video in fetch_related_to_liked(limit_per_video=related_limit):
        vid = video.get("id") or video.get("videoId")
        if vid and vid not in seen:
            seen.add(vid)
            videos.append(video)
        if len(videos) >= limit:
            return videos
    if not videos:
        logger.info("Using fallback sample videos")
        videos = _fallback_samples()
    return videos[:limit]
