"""ZLibrary-specific interactions — wraps PlaywrightService.

Based on real DOM exploration of https://zh.zlib.li/
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass

from src.config import ZLIBRARY_SESSION_PATH
from src.services.playwright_service import PlaywrightService


@dataclass
class BookMetadata:
    """Represents a book search result."""

    title: str
    author: str
    year: str
    language: str
    format: str
    size: str
    download_url: str
    book_id: str


class ZLibraryService:
    """ZLibrary operations: login, search, download.

    Verified against https://zh.zlib.li/
    """

    BASE_URL = "https://zh.zlib.li"
    LOGIN_URL = f"{BASE_URL}/login"
    SEARCH_URL = f"{BASE_URL}/"

    def __init__(self, playwright_service: PlaywrightService) -> None:
        self._pw = playwright_service
        self._page = None

    def login(self, email: str, password: str) -> dict:
        """Navigate to login page and authenticate.

        If session cookies already exist and are still valid, skip login
        and return immediately.
        """
        # Try using existing session first
        if ZLIBRARY_SESSION_PATH.exists():
            self._page = self._pw.new_page()
            self._page.goto(self.BASE_URL)
            try:
                self._page.wait_for_load_state("domcontentloaded", timeout=10_000)
                # Check for login-required elements to determine if session is valid
                self._page.wait_for_selector(
                    'a[href*="/profile"], a[href*="/logout"], a[href*="/book"]',
                    timeout=5_000
                )
                # If we can find book links or profile, session is valid
                self._pw.save_session()  # refresh to update expiry
                return {"status": "logged_in", "url": self._page.url, "source": "session"}
            except Exception:
                pass  # Session invalid or expired, proceed with login

        # No valid session — perform full login
        self._page = self._pw.new_page()
        self._page.goto(self.LOGIN_URL)
        self._page.wait_for_load_state("domcontentloaded", timeout=30_000)

        # Step 1: enter email and click continue
        self._page.fill('input[name="email"]', email)
        self._page.click('button:has-text("继续")')

        # Step 2: wait for password field, then enter password
        self._page.wait_for_selector('input[name="password"]', timeout=15_000)
        self._page.fill('input[name="password"]', password)
        self._page.click('button:has-text("登录")')

        # Wait for redirect away from /login (URL contains "login" before redirect)
        self._page.wait_for_url(lambda url: "login" not in url, timeout=30_000)

        self._pw.save_session()
        return {"status": "logged_in", "url": self._page.url, "source": "login"}

    def search(
        self, query: str, limit: int = 10, offset: int = 0
    ) -> list[BookMetadata]:
        """Search for books and return metadata list.

        Search URL pattern: https://zh.zlib.li/s/{query}
        Verified DOM:
        - Search box: textbox with placeholder "按书名、作者、ISBN、DOI、出版社、MD5等搜索…"
        - Search button: button "搜索"
        - Result book links: a[href*="/book/"] inside results area
        - Book ID extracted from URL like /book/{id}/{slug}.html
        - Author link: a[href*="/author/"]
        - Metadata lines: "年: {year}", "语言: {lang}", "文件: {format, size}"
        """
        if self._page is None:
            self._page = self._pw.new_page()

        # Navigate to search URL (URL-based, not API-based)
        self._page.goto(f"{self.BASE_URL}/s/{query}", timeout=30_000)
        self._page.wait_for_load_state("domcontentloaded", timeout=30_000)

        # Wait for dynamic content to render (z-cover elements appear after JS)
        try:
            self._page.wait_for_selector("z-cover", timeout=10_000)
        except Exception:
            pass  # Fallback: continue even if z-cover not found

        results: list[BookMetadata] = []
        seen_ids: set[str] = set()

        # Book links are <a> tags with href containing /book/
        book_links = self._page.query_selector_all("a[href*='/book/'][href*='.html']")

        for link in book_links:
            href = link.get_attribute("href") or ""
            if not href:
                continue

            # Extract book_id from URL like /book/LaOBY1o791/python-xxx.html
            parts = href.strip("/").split("/")
            book_id = parts[1] if len(parts) >= 2 else ""

            # Skip duplicates (same book_id from multiple links per card)
            if book_id in seen_ids:
                continue
            seen_ids.add(book_id)

            # Title from <z-cover> element's title attribute (inner_text is empty for shadow DOM)
            cover = link.query_selector("z-cover")
            title_text = cover.get_attribute("title") if cover else ""
            authors_attr = cover.get_attribute("authors") if cover else ""

            # Author: from z-cover authors attribute, or extract from nested text
            author_text = authors_attr.split(",")[0].strip() if authors_attr else ""
            if not author_text:
                # Extract author from nested text (appears before "已下载" marker)
                author_text = self._extract_author(link)

            if not author_text:
                author_text = "Unknown"

            results.append(
                BookMetadata(
                    title=title_text,
                    author=author_text,
                    year="",
                    language="",
                    format="",
                    size="",
                    download_url=href,
                    book_id=book_id,
                )
            )

        # Apply offset and limit after deduplication
        return results[offset : offset + limit]

    def get_download_url(self, book_id: str) -> str:
        """Get the direct download URL for a book.

        Verified on https://zh.zlib.li/book/{book_id}/{slug}.html:
        - Download link: a[href*="/dl/"] — no login required
        - Example: /dl/Anmb9Vn42W
        """
        if self._page is None:
            self._page = self._pw.new_page()

        self._page.goto(f"{self.BASE_URL}/book/{book_id}", timeout=30_000)
        self._page.wait_for_load_state("domcontentloaded", timeout=30_000)
        time.sleep(3)  # wait for dynamic content to render

        # Download link is directly on the page — no button click needed
        download_link = self._page.query_selector('a[href*="/dl/"]')
        if download_link:
            return download_link.get_attribute("href") or ""

        # Fallback: construct from known pattern
        return f"{self.BASE_URL}/dl/{book_id}"

    @staticmethod
    def _parse_label(text: str, prefix: str) -> str:
        """Extract a labelled field from card text like '年: 2016'."""
        for line in text.split("\n"):
            if prefix in line:
                return line.split(prefix)[-1].strip()
        return ""

    @staticmethod
    def _parse_file_info(text: str) -> tuple[str, str]:
        """Parse format and size from text like '文件: EPUB, 174 KB'."""
        match = re.search(r"(EPUB|PDF|MOBI|AZW3)\s*,\s*([\d.]+\s*\w+)", text, re.IGNORECASE)
        if match:
            return match.group(1).upper(), match.group(2)
        return "unknown", ""

    @staticmethod
    def _extract_author(link) -> str:
        """Extract author name from nested text in a book card link.

        The text containing '已下载' also contains the title; the author name
        is the last line before '已下载'.
        """
        try:
            for el in link.query_selector_all("*"):
                t = el.inner_text().strip()
                if not t or t.startswith(":host"):
                    continue
                if "已下载" in t:
                    # Split on "已下载" and take the part before, then get last line
                    before = t.split("已下载")[0].strip()
                    lines = [l.strip() for l in before.split("\n") if l.strip()]
                    if lines:
                        return lines[-1]
            return ""
        except Exception:
            return ""
