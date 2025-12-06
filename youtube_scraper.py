#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import re, json, time

STATE_FILE = "storage_state.json"
YOUTUBE_URL = "https://www.youtube.com/"

def parse_video_id(url):
    match = re.search(r"v=([A-Za-z0-9_\-]+)", url)
    return match.group(1) if match else None


def find_video_cards(page):
    """
    YouTube uses multiple DOM layouts.
    We merge all possible video containers into one locator.
    """
    selectors = [
        "ytd-rich-item-renderer",
        "ytd-rich-grid-media",
        "ytd-grid-video-renderer",
        "ytd-video-renderer"
    ]

    combined = ",".join(selectors)
    return page.locator(combined)



def scrape_video(item):
    def safe_text(locator, nth=None):
        try:
            target = item.locator(locator)
            if nth is not None:
                target = target.nth(nth)
            return target.inner_text(timeout=500).strip()
        except:
            return None

    def safe_attr(locator, attr):
        try:
            return item.locator(locator).get_attribute(attr, timeout=500)
        except:
            return None

    # ---------- TITLE ----------
    title = (
        safe_text("h3 a") or
        safe_text("a#video-title") or
        safe_text("a[title]")
    )

    # ---------- URL ----------
    url = safe_attr("h3 a", "href")
    if url and url.startswith("/"):
        url = "https://www.youtube.com" + url

    # ---------- THUMBNAIL ----------
    thumbnail = (
        safe_attr("img.ytCoreImageHost cover video-thumbnail-img ytCoreImageFillParentHeight ytCoreImageFillParentWidth", "src")
        or safe_attr("img", "src")
    )

    # ---------- CHANNEL, VIEWS, TIME AGO ----------
    channel = safe_text("ytm-badge-and-byline-renderer", "span")

    return {
        "title": title,
        "url": url,
        "video_id": parse_video_id(url) if url else None,
        "thumbnail": thumbnail,
        "channel": channel
    }



def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=STATE_FILE)
        page = context.new_page()

        print("Loading YouTube…")
        page.goto(YOUTUBE_URL, wait_until="networkidle")

        # YouTube lazy loads; scroll to load more


        cards = find_video_cards(page)
        count = cards.count()
        print(f"Found {count} video cards")

        results = []
        for i in range(count):
            card = scrape_video(cards.nth(i))
            print(f"finised checking {i}th video")
            if card:
                results.append(card)



        print(json.dumps(results, indent=2))

        browser.close()


if __name__ == "__main__":
    main()
