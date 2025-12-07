#!/usr/bin/env python3
from playwright.sync_api import sync_playwright # type: ignore
import asyncio
import re, json, time, os

from dotenv import load_dotenv # type: ignore

load_dotenv()

STATE_FILE = os.path.abspath(os.getenv('STATE_FILE'))
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
            return value
        except:
            return None

    # ---------- TITLE ----------
    title = safe_text("h3 a")    

    # ---------- URL ----------
    url = safe_attr("h3 a", "href")

    # Normalize
    if url and url.startswith("/"):
        url = "https://www.youtube.com" + url

    # --- Skip YouTube Shorts ---
    if url and "/shorts/" in url:
        return None    # skip this card entirely


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



def scrape_youtube():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=STATE_FILE)
        page = context.new_page()

        print("Loading YouTube…")
        print(STATE_FILE)
        page.goto(YOUTUBE_URL)


        cards = find_video_cards(page)
        count = cards.count()
        print(f"Found {count} video cards")

        results = []
        for i in range(count):
            try:
                item = cards.nth(i)

                # --- Ensure the card is actually visible (lazy-load trigger) ---
                try:
                    item.scroll_into_view_if_needed(timeout=2000)
                except:
                    pass

                # --- Allow YouTube Mobile's JS to hydrate thumbnail src values ---
                page.wait_for_timeout(200)  # small wait after scroll

                # --- Additional lazy load trigger (mouse wheel) ---
                page.mouse.wheel(0, 200)
                page.wait_for_timeout(120)

                # --- Scrape the card after guaranteed loading ---
                card = scrape_video(item)

                print(f"finished checking {i}th video")

                if card:
                    results.append(card)

            except Exception as e:
                print(f"[WARN] error scraping card {i}: {e}")

        print(json.dumps(results, indent=2))

        browser.close()