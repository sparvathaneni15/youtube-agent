from mcp.server import Server # type: ignore
from mcp import types # type: ignore
import json
from youtube_actions import scrape_youtube as _scrape_youtube

server = Server("youtube-agent")

@server.tool("scrape_youtube")
def scrape_youtube_tool():
    videos = _scrape_youtube()
    return types.TextContent(json.dumps(videos, indent=2))

if __name__ == "__main__":
    server.run()
