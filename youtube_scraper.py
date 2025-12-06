#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import re, json, time

STATE_FILE = "storage_state.json"
YOUTUBE_URL = "https://www.youtube.com/"


def find_video_cards(page):
    """
    YouTube uses multiple DOM layouts.
    We merge all possible video containers into one locator.
    """
    selector = "ytd-rich-item-renderer"

    return page.locator(selector)



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
            target = item.locator(locator)
            value = target.get_attribute(attr, timeout=500)
            print(value)
            return value
        except:
            return None

    # ---------- TITLE ----------
    title = safe_text("h3 a")    

    # ---------- URL ----------
    url = safe_attr("h3 a", "href")
    if url and url.startswith("/"):
        url = "https://www.youtube.com" + url

    # ---------- THUMBNAIL ----------
    thumbnail = safe_attr("yt-thumbnail-view-model img", "src")

    # ---------- CHANNEL, VIEWS, TIME AGO ----------
    channel = safe_text("yt-content-metadata-view-model a")

    return {
        "title": title,
        "url": url,
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


        cards = find_video_cards(page)
        count = cards.count()
        print(f"Found {count} video cards")

        results = []
        for i in range(1):
            card = scrape_video(cards.nth(i))
            print(f"finised checking {i}th video")
            if card:
                results.append(card)



        print(json.dumps(results, indent=2))

        browser.close()


if __name__ == "__main__":
    main()
