#!/usr/bin/env python3
"""
Telegram Notification Module for YouTube Agent
Sends notifications to iOS devices via Telegram Bot API.
"""

import os
import requests
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_notification(
    videos_added: List[Dict[str, str]], 
    videos_failed: Optional[List[Dict[str, str]]] = None,
    run_time: Optional[str] = None
) -> bool:
    """
    Send notification to iOS device via Telegram Bot.
    
    Args:
        videos_added: List of dicts with 'title', 'url', 'channel', 'reason'
        videos_failed: Optional list of failed videos with same structure
        run_time: Optional time string for when the run completed
    
    Returns:
        bool: True if notification sent successfully, False otherwise
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[notifier] ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set in .env")
        return False
    
    # Build message
    message_parts = []
    
    # Header
    total_count = len(videos_added)
    if total_count > 0:
        message_parts.append(f"✅ *YouTube Agent: {total_count} Video{'s' if total_count != 1 else ''} Added*\n")
        message_parts.append("📺 *Videos added to Watch Later:*")
        
        # List videos
        for i, video in enumerate(videos_added, 1):
            title = video.get('title', 'Unknown Title')
            url = video.get('url', '')
            channel = video.get('channel', 'Unknown Channel')
            reason = video.get('reason', '')
            
            # Escape markdown special characters in title and channel
            title = escape_markdown(title)
            channel = escape_markdown(channel)
            
            video_line = f"{i}. [{title}]({url})"
            if channel:
                video_line += f" - _{channel}_"
            if reason:
                reason_escaped = escape_markdown(reason)
                video_line += f"\n   💡 _{reason_escaped}_"
            
            message_parts.append(video_line)
    else:
        message_parts.append("ℹ️ *YouTube Agent: No Videos Added*\n")
        message_parts.append("No videos matched your criteria this time.")
    
    # Failed videos section
    if videos_failed and len(videos_failed) > 0:
        message_parts.append(f"\n⚠️ *{len(videos_failed)} Video{'s' if len(videos_failed) != 1 else ''} Failed:*")
        for video in videos_failed:
            title = escape_markdown(video.get('title', 'Unknown'))
            error = escape_markdown(video.get('message', 'Unknown error'))
            message_parts.append(f"• {title}\n   ❌ {error}")
    
    # Timestamp
    if not run_time:
        run_time = datetime.now().strftime("%I:%M %p")
    message_parts.append(f"\n⏰ Run completed at {run_time}")
    
    message = "\n".join(message_parts)
    
    # Send via Telegram API
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False  # Show link previews for videos
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=10)
        response.raise_for_status()
        
        if response.json().get("ok"):
            print(f"[notifier] ✅ Telegram notification sent successfully")
            return True
        else:
            print(f"[notifier] ❌ Telegram API returned error: {response.json()}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"[notifier] ❌ Failed to send Telegram notification: {e}")
        return False


def escape_markdown(text: str) -> str:
    """
    Escape special characters for Telegram Markdown format.
    
    Characters that need escaping: _ * [ ] ( ) ~ ` > # + - = | { } . !
    """
    if not text:
        return ""
    
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    # Only escape characters that aren't part of our intended markdown
    # We'll keep some formatting intact by being selective
    for char in ['*', '_', '[', ']', '`']:
        # Don't escape these if we're using them for formatting
        continue
    
    # Escape problematic characters that often appear in titles
    for char in ['~', '>', '#', '+', '=', '|', '{', '}', '!']:
        text = text.replace(char, f'\\{char}')
    
    return text


def test_notification():
    """Test the notification system with sample data."""
    sample_videos = [
        {
            "title": "Building a YouTube Agent with Python",
            "url": "https://youtube.com/watch?v=test123",
            "channel": "Tech Channel",
            "reason": "Matches your interest in automation"
        },
        {
            "title": "Advanced Playwright Techniques",
            "url": "https://youtube.com/watch?v=test456",
            "channel": "Dev Academy",
            "reason": "Related to your recent projects"
        }
    ]
    
    sample_failed = [
        {
            "title": "Failed Video Example",
            "message": "Could not find Save button"
        }
    ]
    
    success = send_telegram_notification(sample_videos, sample_failed)
    print(f"\nTest notification {'succeeded' if success else 'failed'}")


if __name__ == "__main__":
    test_notification()
