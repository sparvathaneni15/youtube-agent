"""
YouTube OAuth client manager.

This module handles:
- Browser-based OAuth login using Google's InstalledAppFlow
- Automatic token refresh
- Persisting credentials to config/oauth_token.json
- Returning an authenticated YouTube Data API client
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from agent.config import (
    CLIENT_SECRET_FILE,
    OAUTH_TOKEN_FILE,
)

# YouTube Data API requires this scope for read/write playlist access.
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]


def load_credentials() -> Credentials | None:
    """
    Load stored OAuth credentials from disk if they exist.
    Returns:
        - Credentials object if valid
        - None if file missing or invalid
    """
    if not os.path.exists(OAUTH_TOKEN_FILE):
        return None

    try:
        creds = Credentials.from_authorized_user_file(OAUTH_TOKEN_FILE, SCOPES)
        return creds
    except Exception as e:
        print(f"[youtube_client] Failed to load OAuth token: {e}")
        return None


def save_credentials(creds: Credentials) -> None:
    """
    Persist credentials back to oauth_token.json.
    """
    with open(OAUTH_TOKEN_FILE, "w") as f:
        f.write(creds.to_json())


def perform_oauth_flow() -> Credentials:
    """
    Launch browser OAuth (InstalledAppFlow), run a local server on port 8080,
    and return the authenticated credentials.
    """
    print("[youtube_client] No valid token found — starting OAuth flow...")

    if not os.path.exists(CLIENT_SECRET_FILE):
        raise RuntimeError(
            f"Missing {CLIENT_SECRET_FILE}. "
            "Download OAuth client credentials from Google Cloud and place them there."
        )

    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        SCOPES
    )

    # Browser launches → Google Auth → local server receives token
    creds = flow.run_local_server(port=8080, prompt="consent")

    save_credentials(creds)
    print("[youtube_client] OAuth authentication successful and token saved.")

    return creds


def refresh_credentials(creds: Credentials) -> Credentials:
    """
    Refresh the access token if expired.
    """
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            save_credentials(creds)
            print("[youtube_client] Token refreshed.")
        except Exception as e:
            print(f"[youtube_client] Failed to refresh token: {e}")
            print("[youtube_client] Running full OAuth flow...")
            return perform_oauth_flow()

    return creds


def get_youtube_client():
    """
    Main function to call from other modules.
    Returns a fully authenticated YouTube API client.
    """

    # 1. Try loading token from disk
    creds = load_credentials()

    # 2. If missing or invalid → run full OAuth
    if not creds:
        creds = perform_oauth_flow()

    # 3. If expired → refresh
    creds = refresh_credentials(creds)

    # 4. Build authenticated YouTube client
    try:
        youtube = build(
            serviceName="youtube",
            version="v3",
            credentials=creds,
            cache_discovery=False
        )
        return youtube
    except Exception as e:
        print(f"[youtube_client] Failed to create YouTube API client: {e}")
        raise
