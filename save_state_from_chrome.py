#!/usr/bin/env python3
"""
save_state_from_chrome.py
------------------------------------------
Loads your real Chrome profile, launches YouTube logged in,
and saves Playwright storage state to storage_state.json.
"""

from pathlib import Path
from playwright.sync_api import sync_playwright # type: ignore
import re, json, time, os
from dotenv import load_dotenv # type: ignore

load_dotenv()


# Path to your *actual* Chrome profile
CHROME_PROFILE = os.path.abspath(os.getenv('PROFILE'))

# Output where Playwright will save cookies + localStorage/sessionStorage
STATE_FILE = Path("storage_state.json")

def main():
    print("🚀 Launching Chrome with your real profile...")

    with sync_playwright() as p:
        # Launch persistent context using your Chrome profile
        context = p.chromium.launch_persistent_context(
            CHROME_PROFILE,
            headless=False,
            args=[
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                "--allow-insecure-localhost",
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
            ],
        )

        page = context.new_page()

        print("🌐 Navigating to YouTube...")
        page.goto("https://www.youtube.com", wait_until="domcontentloaded")

        print("🤝 Waiting for YouTube homepage to fully load...")
        page.wait_for_load_state("networkidle")

        print("💾 Saving cookies + local/session storage...")
        context.storage_state(path=str(STATE_FILE))

        print(f"✅ Saved Playwright state to: {STATE_FILE.resolve()}")

        # Keep browser open (optional)
        input("Press ENTER to close browser...")

        context.close()


if __name__ == "__main__":
    main()
