"""Playwright browser lifecycle management — shared across all ZLibrary tools."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from playwright.sync_api import Browser, BrowserContext, sync_playwright

from src.config import ZLIBRARY_SESSION_PATH


class PlaywrightService:
    """Manages Playwright browser, context, and page lifecycle."""

    def __init__(self) -> None:
        self._playwright = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None

    def launch(self, headless: bool = True) -> Browser:
        """Launch a new browser instance."""
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=headless)
        return self._browser

    def new_context(self, persist_session: bool = True) -> BrowserContext:
        """Create a new browser context, optionally loading a saved session."""
        if self._browser is None:
            self.launch()

        # Set realistic browser headers to avoid Z-Library blocking
        self._context = self._browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            ),
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,"
                    "image/avif,image/webp,image/apng,*/*;q=0.8"
                ),
            },
        )

        if persist_session and ZLIBRARY_SESSION_PATH.exists():
            self._context.add_cookies(self._load_session())

        return self._context

    def new_page(self):
        """Create a new page in the current context."""
        if self._context is None:
            self.new_context()
        return self._context.new_page()

    def save_session(self) -> None:
        """Persist current browser context cookies to disk."""
        if self._context is None:
            return
        cookies = self._context.cookies()
        ZLIBRARY_SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
        ZLIBRARY_SESSION_PATH.write_text(json.dumps(cookies))

    def close(self) -> None:
        """Close browser and stop Playwright."""
        if self._context:
            self._context.close()
            self._context = None
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None

    @staticmethod
    def _load_session() -> list[dict[str, Any]]:
        """Load cookies from session file."""
        return json.loads(ZLIBRARY_SESSION_PATH.read_text())

    def __enter__(self):
        self.launch()
        return self

    def __exit__(self, *args):
        self.close()
