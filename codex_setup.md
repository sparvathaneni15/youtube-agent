You are an AI software engineer. Generate a complete Python project in this workspace following the architecture described below. Create the entire directory structure, ALL FILES, and ALL CODE — fully implemented, runnable, no placeholders, no omissions. Use correct imports, error handling, docstrings, class structures, environment variables, and Docker best practices.

===============================
PROJECT: youtube-value-agent
===============================

This system filters YouTube recommendation candidates by combining:
1. A **perception layer** (DL models: MiniLM, CLIP, OpenCV, features)
2. A **classifier layer** (RandomForest + StandardScaler) to create **semantic labels**
3. An **LLM reasoning layer** (local LLM HTTP endpoint) to judge actual value
4. A pipeline to fetch videos → analyze → label → reason → Watch Later.

Generate all code to implement this pipeline.

------------------------------------
1. Full Directory Structure (Create)
------------------------------------

youtube-value-agent/
├── src/
│   ├── agent/
│   │   ├── youtube_client.py
│   │   ├── fetch_candidates.py
│   │   ├── attributes.py
│   │   ├── llm_scorer.py
│   │   ├── playlist_writer.py
│   │   ├── pipeline.py
│   │   ├── scheduler.py
│   │   ├── config.py
│   │   ├── features/
│   │   │   ├── text_features.py
│   │   │   ├── thumbnail_features.py
│   │   │   ├── metadata_features.py
│   │   └── model/
│   │       ├── heuristics.py
│   │       ├── classifiers/
│   │       │   ├── clickbait_classifier.py
│   │       │   ├── educational_classifier.py
│   │       │   ├── topic_classifier.py
│   │       │   ├── thumbnail_classifier.py
│   │       │   ├── load_classifiers.py
│   │       ├── train/
│   │       │   ├── train_clickbait.py
│   │       │   ├── train_educational.py
│   │       │   ├── train_topic.py
│   │       │   ├── train_thumbnail.py
│   │       │   ├── train_all.py
│   │       └── predict_labels.py
│   ├── run_once.py
│   └── run_scheduler.py
├── config/
│   ├── client_secret.json              # empty placeholder
│   ├── oauth_token.json                # empty placeholder
│   └── allow_block_lists.py
├── models/
│   ├── clickbait_classifier.pkl        # empty placeholders
│   ├── clickbait_scaler.pkl
│   ├── educational_classifier.pkl
│   ├── educational_scaler.pkl
│   ├── topic_classifier.pkl
│   ├── topic_scaler.pkl
│   ├── thumbnail_classifier.pkl
│   ├── thumbnail_scaler.pkl
├── docker/
│   ├── Dockerfile
│   └── entrypoint.sh
├── docker-compose.yml
├── requirements.txt
└── README.md

----------------------------------------
2. Functional Requirements (Implement)
----------------------------------------

──────────────────────────────────────────
A. Perception Layer  (features/)
──────────────────────────────────────────

### text_features.py
- Use sentence-transformers `all-MiniLM-L6-v2`
- Implement:
  - clean_text()
  - extract_text_features() returning a 384-dim embedding

### thumbnail_features.py
- Use CLIP: openai/clip-vit-base-patch32
- Use OpenCV for:
  - face detection
  - saturation computation
  - text density (Canny edge)
- extract_thumbnail_features() returns:
  - 512-dim CLIP embedding
  - 4 thumbnail scalar features

### metadata_features.py
- Parse:
  - duration (ISO8601) via isodate
  - views, likes, comments, like ratio
  - age (seconds since published)
- Return a normalized numeric vector

──────────────────────────────────────────
B. Classifier Layer (model/classifiers)
──────────────────────────────────────────

Implement **four classifiers**:
1. clickbait_classifier.py
2. educational_classifier.py
3. topic_classifier.py
4. thumbnail_classifier.py

Each file must:
- Load `classifier.pkl` and `scaler.pkl`
- Provide `predict_proba(feature_vector)` returning float
- Provide `is_trained()` boolean

Implement central loader:  
### load_classifiers.py
- load all classifiers
- expose a single object:
  {
    "clickbait": classifier_instance,
    "educational": classifier_instance,
    "topic": classifier_instance,
    "thumbnail": classifier_instance
  }

Implement training scripts:
- train_clickbait.py
- train_educational.py
- train_topic.py
- train_thumbnail.py
- train_all.py → runs all above

Each:
- Fetch labeled samples (liked videos = positive; trending = negative)
- Extract features
- Fit StandardScaler + RandomForestClassifier
- Save to appropriate `models/*.pkl`

──────────────────────────────────────────
C. Semantic Label Builder (attributes.py)
──────────────────────────────────────────

attributes.py must:
- Import perception modules
- Import classifiers via load_classifiers.py
- Import heuristics
- Build a dictionary:

{
  "video_id": str,
  "title": str,
  "description_summary": str,
  "channel": {...},
  "stats": {...},
  "thumbnail_signals": {...},
  "text_signals": {...},
  "perceived_scores": {
      "clickbait_prob": float,
      "educational_prob": float,
      "topic_relevance": float,
      "thumbnail_clickbait_prob": float
  }
}

This is the object passed to the LLM.

──────────────────────────────────────────
D. LLM Reasoner (llm_scorer.py)
──────────────────────────────────────────

- Provide score_with_llm(video_context: dict) → (score: float, reason: str)
- Use environment variable: LLM_ENDPOINT
- Build system prompt describing the decision criteria
- User prompt contains JSON of the video_context
- Call the LLM endpoint via HTTP POST (OpenAI-compatible schema)
- Expect JSON: { "value_score": float, "reason": str }
- Return parsed values

──────────────────────────────────────────
E. Fetch Candidates (fetch_candidates.py)
──────────────────────────────────────────

Implement:
- fetch_subscription_videos()
- fetch_trending()
- fetch_related_to_liked()
- get_candidate_videos()

Use browser OAuth via youtube_client.

──────────────────────────────────────────
F. OAuth (youtube_client.py)
──────────────────────────────────────────

- Implement browser-based OAuth with InstalledAppFlow
- Port 8080 local redirect
- Save/refresh credentials
- Return authenticated YouTube API client

──────────────────────────────────────────
G. Pipeline (pipeline.py)
──────────────────────────────────────────

1. Fetch candidates
2. Build video_context (attributes.py)
3. Get LLM score
4. Log:
   "[title] → LLM score 0.912 | reason: ..."
5. Accept if score ≥ 0.8 (configurable)
6. Append to accepted list
7. Optionally send to Watch Later

──────────────────────────────────────────
H. Playlist Writer (playlist_writer.py)
──────────────────────────────────────────

- add_to_watch_later(video_id: str)
- Use playlistId "WL"

──────────────────────────────────────────
I. Scheduler (scheduler.py)
──────────────────────────────────────────

- APScheduler every 6 hours
- Pipeline run + playlist_writer

──────────────────────────────────────────
J. Entry Points
──────────────────────────────────────────

### run_once.py
- Runs pipeline once, adds accepted videos to Watch Later

### run_scheduler.py
- Starts APScheduler loop

──────────────────────────────────────────
K. Docker (docker/)
──────────────────────────────────────────

### Dockerfile
- python:3.10-slim
- Install apt deps (OpenCV, ffmpeg)
- pip install -r requirements.txt
- Copy src/, config/, models/
- Set PYTHONPATH=/app/src
- ENTRYPOINT → entrypoint.sh

### entrypoint.sh
if arg == 'run': run run_once.py
if arg == 'schedule': run run_scheduler.py
else: print usage


──────────────────────────────────────────
L. docker-compose.yml
──────────────────────────────────────────

- service llm:
    - OpenAI-compatible endpoint at port 8000
- service youtube_agent:
    - build Dockerfile
    - depends_on llm
    - environment: LLM_ENDPOINT=http://llm:8000/v1/chat/completions
    - volumes: config/, models/
    - command: ["schedule"]
    - restart: unless-stopped

──────────────────────────────────────────
M. requirements.txt
──────────────────────────────────────────
Include:
google-auth  
google-auth-oauthlib  
google-api-python-client  
sentence-transformers  
torch  
transformers  
scikit-learn  
numpy  
pandas  
opencv-python  
Pillow  
isodate  
apscheduler  
requests  
tqdm  
ffmpeg-python (optional)

──────────────────────────────────────────
N. README.md
──────────────────────────────────────────
Must include:
- Full project overview
- Explanation of perception → classifier → LLM architecture
- Setup steps
- OAuth instructions
- Training instructions
- LLM configuration
- Running once
- Scheduling
- Docker usage
- Developer notes

===============================
IMPORTANT:
===============================
Generate EVERY file with **complete code**.  
NO placeholders.  
NO “TODO”.  
NO omissions.  
All modules must import each other correctly.  
Every classifier must load and predict properly.  
The attributes builder must integrate all layers.  
The LLM scorer must be fully implemented.  
This MUST be a fully runnable project.

