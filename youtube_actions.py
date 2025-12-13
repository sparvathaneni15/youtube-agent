#!/usr/bin/env python3
from playwright.sync_api import sync_playwright # type: ignore
import asyncio
import re, json, time, os

from dotenv import load_dotenv # type: ignore

load_dotenv()

STATE_FILE = os.path.abspath(os.getenv('STATE_FILE'))
YOUTUBE_URL = "https://www.youtube.com/"

def scrape_youtube(output_path: str | None = "data/scraped.json"):
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
    

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=STATE_FILE)
        page = context.new_page()

        page.goto(YOUTUBE_URL)


        cards = find_video_cards(page)
        count = cards.count()

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

                if card:
                    results.append(card)

            except Exception as e:
                print(f"[WARN] error scraping card {i}: {e}")

        # Write results to file if requested
        if output_path:
            out_abs = os.path.abspath(output_path)
            os.makedirs(os.path.dirname(out_abs), exist_ok=True)
            with open(out_abs, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
            print(f"[scrape_youtube] Wrote {len(results)} items to {out_abs}")

        # Also print JSON to stdout for convenience
        print(json.dumps(results, indent=2))

        browser.close()

    return results

def add_to_watch_later(video_url: str, timeout: int = 10000) -> dict:
    """
    Add a YouTube video to the Watch Later playlist.
    
    Args:
        video_url: Full YouTube video URL (e.g., https://youtube.com/watch?v=...)
        timeout: Maximum time to wait for elements (milliseconds)
    
    Returns:
        dict with keys:
            - success: bool
            - url: str (original URL)
            - message: str (error message if failed)
    """
    result = {
        "success": False,
        "url": video_url,
        "message": ""
    }
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state=STATE_FILE)
            page = context.new_page()
            
            print(f"[add_to_watch_later] Navigating to {video_url}")
            page.goto(video_url, wait_until="domcontentloaded", timeout=timeout)
            
            # Wait for page to be ready
            page.wait_for_load_state("networkidle", timeout=timeout)
            
            # YouTube has multiple possible button selectors, try them in order
            save_button_selectors = [
                "button[aria-label*='Save']",
                "button[aria-label*='save']",
                "ytd-button-renderer:has-text('Save')",
                "#button-shape-like + button",  # Often next to like button
            ]
            
            save_button = None
            for selector in save_button_selectors:
                try:
                    save_button = page.locator(selector).first
                    if save_button.is_visible(timeout=2000):
                        print(f"[add_to_watch_later] Found Save button with selector: {selector}")
                        break
                except:
                    continue
            
            if not save_button:
                result["message"] = "Could not find Save button"
                print(f"[add_to_watch_later] ERROR: {result['message']}")
                browser.close()
                return result
            
            # Click the Save button
            save_button.click(timeout=timeout)
            page.wait_for_timeout(1000)  # Wait for menu to appear
            
            # Find and click "Watch later" option in the menu
            watch_later_selectors = [
                "text='Watch later'",
                "text='Watch Later'",
                "ytd-playlist-add-to-option-renderer:has-text('Watch later')",
                "[aria-label*='Watch later']",
            ]
            
            watch_later_option = None
            for selector in watch_later_selectors:
                try:
                    watch_later_option = page.locator(selector).first
                    if watch_later_option.is_visible(timeout=2000):
                        print(f"[add_to_watch_later] Found Watch Later option with selector: {selector}")
                        break
                except:
                    continue
            
            if not watch_later_option:
                result["message"] = "Could not find Watch Later option in menu"
                print(f"[add_to_watch_later] ERROR: {result['message']}")
                browser.close()
                return result
            
            # Click Watch Later
            watch_later_option.click(timeout=timeout)
            page.wait_for_timeout(1000)  # Wait for action to complete
            
            # Success!
            result["success"] = True
            result["message"] = "Successfully added to Watch Later"
            print(f"[add_to_watch_later] ✅ {result['message']}")
            
            browser.close()
            
    except Exception as e:
        result["message"] = f"Error: {str(e)}"
        print(f"[add_to_watch_later] ERROR: {result['message']}")
    
    return result

if __name__ == "__main__":
    scrape_youtube()