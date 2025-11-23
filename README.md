# youtube-agent

youtube-agent filters YouTube recommendation candidates by combining perception (DL feature extraction), classical classifiers, and an LLM judge to decide which videos deserve your Watch Later list.

## Architecture
- **Perception layer**: MiniLM embeddings for text (`all-MiniLM-L6-v2`), CLIP image embeddings for thumbnails (`openai/clip-vit-base-patch32`), OpenCV signals (faces, saturation, edges, brightness), and normalized metadata (duration, engagement, age).
- **Classifier layer**: RandomForest + StandardScaler models for clickbait, educational value, topic relevance, and thumbnail clickbait. Models load from `models/*.pkl` and fall back to heuristic probabilities if artifacts are missing.
- **LLM reasoning**: Sends the semantic context to an OpenAI-compatible endpoint (`LLM_ENDPOINT`) and expects `{ "value_score": float, "reason": str }`. A heuristic scorer is used if no endpoint is configured.
- **Pipeline**: Fetches candidates (subscriptions, trending, related to liked), builds semantic attributes, scores with the LLM, logs outcomes, and adds accepted videos to Watch Later.
- **Scheduler**: APScheduler runs the pipeline every 6 hours.

## Setup
1. Ensure Python 3.10+ and `pip` are available. Optionally export `PYTHONPATH=src`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Populate OAuth client secrets at `config/client_secret.json` (Google console) and keep `config/oauth_token.json` writeable.

## OAuth Instructions
- The first run opens a browser for Google consent on port 8080 using `InstalledAppFlow`.
- After approval, tokens are stored in `config/oauth_token.json` and refreshed automatically.

## Training Classifiers
- Synthetic training scripts are provided to bootstrap usable models.
- Run individually: `python src/agent/model/train/train_clickbait.py` (similar for educational/topic/thumbnail).
- Or train all: `python src/agent/model/train/train_all.py`.
- Artifacts save into `models/` and will be picked up automatically.

## LLM Configuration
- Set `LLM_ENDPOINT` to an OpenAI-compatible chat completion URL (e.g., `http://localhost:8000/v1/chat/completions`).
- Without the variable, the system falls back to heuristic scoring.

## Running Once
```
python src/run_once.py
```
Logs each candidate and accepted video. Threshold defaults to `VALUE_SCORE_THRESHOLD` env var (default 0.8).

## Scheduling
```
python src/run_scheduler.py
```
Starts APScheduler to run every 6 hours and keep the process alive.

## Docker Usage
Build and run with docker-compose:
```
docker-compose up --build
```
- `llm` service exposes an OpenAI-compatible endpoint on port 8000.
- `youtube_agent` mounts `config/` and `models/`, sets `LLM_ENDPOINT`, and runs the scheduler.
- To run once inside the container: `docker-compose run youtube_agent run`.

## Developer Notes
- Perception modules are resilient and fall back to zero vectors on failures.
- Classifiers return fallback probabilities if artifacts are missing; train artifacts to improve quality.
- Update `config/allow_block_lists.py` to whitelist or block channels/keywords.
- Logging is configured in entrypoints; adjust verbosity as needed.
