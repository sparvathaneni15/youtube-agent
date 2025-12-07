#!/usr/bin/env python3
import os, sys, json, time
import requests
from pathlib import Path

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
SYSTEM_PATH = Path(os.getenv("SYSTEM_PATH", "../system_instructions.md"))
INPUT_PATH = Path(os.getenv("INPUT_PATH", "../data/scraped.json"))
OUTPUT_PATH = Path(os.getenv("OUTPUT_PATH", "../data/selected.json"))
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"

SESSION = requests.Session()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"[orchestrator] Failed to read {path}: {e}", file=sys.stderr)
        sys.exit(1)


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[orchestrator] Failed to read JSON {path}: {e}", file=sys.stderr)
        sys.exit(1)


def chat_ollama(messages, model: str, format_schema=None):
    """
    Send a chat-style request to Ollama using /api/chat.
    No fallback logic. If /api/chat does not exist, raise an error.
    """
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
    }
    if format_schema is not None:
        payload["format"] = format_schema

    # Call /api/chat only
    r = SESSION.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json=payload,
        timeout=120
    )

    # If the endpoint doesn't exist → fail loudly
    if r.status_code == 404:
        raise RuntimeError(
            f"Ollama endpoint /api/chat not found at {OLLAMA_BASE_URL}. "
            f"Your Ollama version may be too old or misconfigured."
        )

    r.raise_for_status()
    data = r.json()

    # Common Ollama response format:
    # { "message": { "role": "...", "content": "..." } }
    if "message" in data and "content" in data["message"]:
        return data["message"]["content"]

    # Older / alternate format:
    # { "messages": [ { "content": "..." } ] }
    if "messages" in data and len(data["messages"]) > 0:
        return data["messages"][-1].get("content", "")

    # Unexpected response → return raw for debugging
    return str(data)




def main():
    system_text = read_text(SYSTEM_PATH)
    scraped = read_json(INPUT_PATH)

    # Expect a list of dicts with keys: title, url, thumbnail, channel
    videos = scraped if isinstance(scraped, list) else scraped.get("videos", [])

    # Ask the model to select 1-3 videos and return strict JSON.
    schema = {
        "type": "object",
        "properties": {
            "selections": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "reason": {"type": "string"}
                    },
                    "required": ["url", "reason"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["selections"],
        "additionalProperties": False
    }

    user_prompt = (
        "You are given a JSON array of YouTube homepage videos. "
        "Return a JSON object with a 'selections' array containing 1–3 chosen videos with a short reasoning. "
        "Only return valid JSON matching the provided schema."
    )

    messages = [
        {"role": "system", "content": system_text},
        {"role": "user", "content": user_prompt},
        {"role": "user", "content": json.dumps(videos)}
    ]

    try:
        content = chat_ollama(messages, MODEL, schema)
        result = json.loads(content)
    except Exception as e:
        print(f"[orchestrator] Model did not return valid JSON: {e}\nRaw: {content if 'content' in locals() else ''}", file=sys.stderr)
        sys.exit(2)

    # Persist selections
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))

    # Optionally call actions here (future: MCP tool add_to_watch_later)
    if DRY_RUN:
        print("[orchestrator] DRY_RUN=true, not invoking add_to_watch_later.")
    else:
        # Placeholder: implement MCP client call to add_to_watch_later(video_id)
        print("[orchestrator] Action execution not implemented yet.")


if __name__ == "__main__":
    main()
