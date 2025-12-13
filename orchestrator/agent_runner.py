#!/usr/bin/env python3
import os, sys, json, time
import requests # type: ignore
from pathlib import Path
from mcp.server import Server # type: ignore

from dotenv import load_dotenv # type: ignore

load_dotenv()

# Ensure repo root is on sys.path so we can import mcp_server when running locally
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
SYSTEM_PATH = Path(os.getenv("SYSTEM_PATH", "../system_instructions.md"))
INPUT_PATH = Path(os.getenv("INPUT_PATH", "../data/scraped.json"))
OUTPUT_PATH = Path(os.getenv("OUTPUT_PATH", "../data/selected.json"))
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
USE_MCP_MODULE = os.getenv("USE_MCP_MODULE", "false").lower() == "true"

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


def scrape_via_mcp_module():
    """
    Calls the tool wrapper defined in mcp_server.py directly as a function.
    This does NOT speak the MCP protocol; it imports and invokes the wrapper.
    Returns the parsed Python list of video dicts.
    """
    try:
        from orchestrator.mcp_server import scrape_youtube_tool  # type: ignore
    except Exception as e:
        print(f"[orchestrator] Could not import mcp_server.scrape_youtube_tool: {e}", file=sys.stderr)
        sys.exit(1)

    content = scrape_youtube_tool()

    # mcp.types.TextContent likely exposes the JSON via a 'text' attribute
    text = None
    if hasattr(content, "title"):
        title = getattr(content, "title")
    elif hasattr(content, "url"):
        url = getattr(content, "url")
    elif isinstance(content, str):
        text = content
    else:
        # Last resort: try to stringify
        text = str(content)

    try:
        data = json.loads(text)
    except Exception as e:
        print(f"[orchestrator] Failed to parse JSON from mcp_server tool output: {e}\nRaw: {text}", file=sys.stderr)
        sys.exit(2)

    return data


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
    from datetime import datetime
    
    # Import YouTube actions and notifier from parent directory
    try:
        from youtube_actions import add_to_watch_later
        from notifier import send_telegram_notification
    except ImportError as e:
        print(f"[orchestrator] ERROR: Could not import modules: {e}", file=sys.stderr)
        print(f"[orchestrator] Make sure youtube_actions.py and notifier.py are in parent directory", file=sys.stderr)
        sys.exit(1)
    
    system_text = read_text(SYSTEM_PATH)
    print(f"[orchestrator] USE_MCP_MODULE={USE_MCP_MODULE}, DRY_RUN={DRY_RUN}")
    
    if USE_MCP_MODULE:
        scraped = scrape_via_mcp_module()
        print(f"[orchestrator] Scraped {len(scraped)} videos via MCP module.")
    else:
        scraped = read_json(INPUT_PATH)
        print(f"[orchestrator] Loaded {len(scraped) if isinstance(scraped, list) else 'unknown'} videos from file")

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

    # Execute Watch Later actions
    selections = result.get("selections", [])
    
    if DRY_RUN:
        print(f"[orchestrator] DRY_RUN=true, would add {len(selections)} videos to Watch Later")
        for sel in selections:
            print(f"  - {sel.get('url')}")
        return
    
    # Execute actions for real
    print(f"[orchestrator] Adding {len(selections)} videos to Watch Later...")
    
    videos_added = []
    videos_failed = []
    
    for selection in selections:
        url = selection.get("url")
        reason = selection.get("reason")
        
        # Find the original video metadata
        video_meta = None
        for v in videos:
            if v.get("url") == url:
                video_meta = v
                break
        
        if not video_meta:
            print(f"[orchestrator] WARNING: Could not find metadata for {url}")
            video_meta = {"title": "Unknown", "channel": "Unknown", "url": url}
        
        # Add to Watch Later
        action_result = add_to_watch_later(url)
        
        if action_result.get("success"):
            videos_added.append({
                "title": video_meta.get("title"),
                "url": url,
                "channel": video_meta.get("channel"),
                "reason": reason
            })
        else:
            videos_failed.append({
                "title": video_meta.get("title"),
                "url": url,
                "message": action_result.get("message")
            })
    
    # Send notification
    run_time = datetime.now().strftime("%I:%M %p")
    print(f"[orchestrator] Sending Telegram notification...")
    
    notification_sent = send_telegram_notification(
        videos_added=videos_added,
        videos_failed=videos_failed if videos_failed else None,
        run_time=run_time
    )
    
    if notification_sent:
        print(f"[orchestrator] ✅ Workflow complete: {len(videos_added)} added, {len(videos_failed)} failed")
    else:
        print(f"[orchestrator] ⚠️ Workflow complete but notification failed")
    
    # Exit with appropriate code
    sys.exit(0 if len(videos_failed) == 0 else 1)


if __name__ == "__main__":
    main()
