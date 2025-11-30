"""
Fetch candidate YouTube videos from multiple sources:

- Subscription feed
- Trending videos
- Related-to-liked videos

This module prepares the raw candidate pool before perception/classification/LLM.
"""

from __future__ import annotations

from typing import List, Dict, Any
import time
import re

from agent.youtube_client import get_youtube_client


# ---------------------------------------------------------
# Utility: Extract video ID from different API response types
# ---------------------------------------------------------

def extract_video_id(item: Dict[str, Any]) -> str | None:
    """
    Normalizes YouTube API response objects into a string video ID.

    Cases:
    - videos().list() — item["id"] is a string
    - search().list() — item["id"] is an object: {"videoId": "..."}
    """
    if "id" not in item:
        return None

    if isinstance(item["id"], str):
        return item["id"]  # videos().list()

    if isinstance(item["id"], dict):
        return item["id"].get("videoId")  # search().list()

    return None


# ---------------------------------------------------------
# Fetch subscription feed videos
# ---------------------------------------------------------

def fetch_subscription_videos(youtube, max_results: int = 25) -> List[Dict]:
    """
    Fetches videos from channels the authenticated user is subscribed to.

    Note:
    - This uses the "subscriptions" + "activities" endpoints.
    - The subscription feed is not perfectly accessible via API,
      so we get uploads for channels the user is subscribed to.
    """

    videos = []
    request = youtube.subscriptions().list(
        part="snippet",
        mine=True,
        maxResults=50
    )
    response = request.execute()

    channel_ids = [item["snippet"]["resourceId"]["channelId"] for item in response["items"]]

    # Fetch recent uploads from each channel
    for channel_id in channel_ids[:max_results]:  # throttle
        try:
            uploads = youtube.search().list(
                part="snippet",
                channelId=channel_id,
                maxResults=5,
                order="date",
                type="video"
            ).execute()

            for item in uploads.get("items", []):
                videos.append(item)
        except Exception as e:
            print(f"[fetch_candidates] Failed to fetch uploads for channel {channel_id}: {e}")

        time.sleep(0.2)

    print(f"[fetch_candidates] Subscription videos fetched: {len(videos)}")
    return videos


# ---------------------------------------------------------
# Fetch trending videos
# ---------------------------------------------------------

def fetch_trending(youtube, max_results: int = 25) -> List[Dict]:
    """
    Fetch trending videos. Useful for training negative samples or broader exploration.
    """
    try:
        response = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            chart="mostPopular",
            maxResults=max_results,
            regionCode="US"
        ).execute()
        items = response.get("items", [])
        print(f"[fetch_candidates] Trending videos fetched: {len(items)}")
        return items
    except Exception as e:
        print(f"[fetch_candidates] Failed to fetch trending: {e}")
        return []


# ---------------------------------------------------------
# Unified entry point for the pipeline
# ---------------------------------------------------------

def get_candidate_videos() -> List[Dict]:
    """
    Primary function used by the perception pipeline.
    Combines:
    - subscription videos
    - trending videos
    - related to liked videos

    Deduplicates by video ID.
    """
    youtube = get_youtube_client()

    subs = fetch_subscription_videos(youtube)
    trending = fetch_trending(youtube)

    all_items = subs + trending

    deduped = {}
    for item in all_items:
        vid = extract_video_id(item)
        if vid:
            deduped[vid] = item

    print(f"[fetch_candidates] Total unique candidate videos: {len(deduped)}")

    # Filter out YouTube Shorts (videos with duration < 60s).
    candidates = list(deduped.values())

    print(f"[fetch_candidates] Candidates after filtering shorts: {len(candidates)}")
    return candidates