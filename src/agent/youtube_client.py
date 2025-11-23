from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from agent.config import OAUTH_CLIENT_FILE, OAUTH_TOKEN_FILE, YOUTUBE_SCOPES

logger = logging.getLogger(__name__)


def get_credentials(token_file: Path = OAUTH_TOKEN_FILE, client_file: Path = OAUTH_CLIENT_FILE) -> Credentials:
    creds: Optional[Credentials] = None
    if token_file.exists() and token_file.stat().st_size > 0:
        creds = Credentials.from_authorized_user_file(str(token_file), YOUTUBE_SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(client_file), YOUTUBE_SCOPES)
        creds = flow.run_local_server(port=8080, prompt="consent")
        token_file.parent.mkdir(parents=True, exist_ok=True)
        token_file.write_text(creds.to_json())
        logger.info("Stored new OAuth token at %s", token_file)
    return creds


def get_youtube_client():
    creds = get_credentials()
    return build("youtube", "v3", credentials=creds)
