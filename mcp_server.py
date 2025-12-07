from mcp.server import Server # type: ignore
from mcp import types # type: ignore
import json
from youtube_actions import scrape_youtube, save_video

server = Server("youtube-agent")

@server.tool("scrape_youtube")
def scrape_youtube():
    videos = scrape_youtube()
    return types.TextContent(json.dumps(videos, indent=2))

@server.tool("save_video")
def save_video(video_url: str):
    save_video(video_url)
    return types.TextContent(f"Added {video_url} to Watch Later")

if __name__ == "__main__":
    server.run()
