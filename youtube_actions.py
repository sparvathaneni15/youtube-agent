#!/usr/bin/env python3
from playwright.sync_api import sync_playwright # type: ignore
import asyncio
import re, json, time

STATE_FILE = "storage_state.json"


def add_to_watch_later(url):
    def find_button():

async def save_video(url : str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=STATE_FILE)
        page = context.new_page()

        page.goto(url)
        try:
            await page.getByRole("button", { "name": "More actions" }).click()

        except Exception as e:
            print(f"Error adding {url} to watch later playlist: {e}")