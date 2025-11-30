from agent.fetch_candidates import get_candidate_videos
from agent.youtube_client import get_youtube_client

def main():
    print("🔑 Testing OAuth + YouTube API client...")
    youtube = get_youtube_client()
    print("✔ YouTube client authenticated successfully.\n")

    print("🎥 Fetching candidate videos...")
    videos = get_candidate_videos()

    print(f"📦 Total videos returned: {len(videos)}")

    # Print info for the first 5 videos
    for item in videos[:5]:
        snippet = item.get("snippet", {})
        title = snippet.get("title", "NO TITLE")
        channel = snippet.get("channelTitle", "NO CHANNEL")
        print(f"- {title}  |  Channel: {channel}")

    print("\n✅ Test completed successfully.")

if __name__ == "__main__":
    main()
