import os

# -----------------------------------
# Base Path Setup
# -----------------------------------

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# -----------------------------------
# OAuth / YouTube Client Credentials
# -----------------------------------

CLIENT_SECRET_FILE = os.path.join(CONFIG_DIR, "client_secret.json")
OAUTH_TOKEN_FILE   = os.path.join(CONFIG_DIR, "oauth_token.json")

# -----------------------------------
# Classifier Model Paths
# -----------------------------------

CLICKBAIT_CLASSIFIER_PATH = os.path.join(MODELS_DIR, "clickbait_classifier.pkl")
CLICKBAIT_SCALER_PATH     = os.path.join(MODELS_DIR, "clickbait_scaler.pkl")

EDUCATIONAL_CLASSIFIER_PATH = os.path.join(MODELS_DIR, "educational_classifier.pkl")
EDUCATIONAL_SCALER_PATH     = os.path.join(MODELS_DIR, "educational_scaler.pkl")

TOPIC_CLASSIFIER_PATH = os.path.join(MODELS_DIR, "topic_classifier.pkl")
TOPIC_SCALER_PATH     = os.path.join(MODELS_DIR, "topic_scaler.pkl")

THUMBNAIL_CLASSIFIER_PATH = os.path.join(MODELS_DIR, "thumbnail_classifier.pkl")
THUMBNAIL_SCALER_PATH     = os.path.join(MODELS_DIR, "thumbnail_scaler.pkl")

# -----------------------------------
# Watch Later Playlist ID
# -----------------------------------

WATCH_LATER_PLAYLIST_ID = "WL"   # YouTube global watch later playlist ID

# -----------------------------------
# LLM Endpoint
# -----------------------------------

LLM_ENDPOINT = os.getenv(
    "LLM_ENDPOINT", 
    "http://localhost:11434/api/chat"
)

# -----------------------------------
# User Preferences
# -----------------------------------

USER_INTERESTS = [
    "artificial intelligence",
    "machine learning",
    "software engineering",
    "basketball analytics",
    "music production",
    "interior design",
    "fashion",
    "philosophy",
    "psychology"
]

# -----------------------------------
# Threshold Settings
# -----------------------------------

DEFAULT_VALUE_THRESHOLD = 0.80
