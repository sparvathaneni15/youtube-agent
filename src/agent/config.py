import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = BASE_DIR / "config"
MODELS_DIR = BASE_DIR / "models"
DEFAULT_SCORE_THRESHOLD = float(os.getenv("VALUE_SCORE_THRESHOLD", "0.8"))
MAX_CANDIDATES = int(os.getenv("MAX_CANDIDATES", "25"))
OAUTH_CLIENT_FILE = CONFIG_DIR / "client_secret.json"
OAUTH_TOKEN_FILE = CONFIG_DIR / "oauth_token.json"

# YouTube scopes required for reading and writing playlists
YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube",
]
