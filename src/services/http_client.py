"""Pure-HTTP client for ZLibrary using saved session cookies.

Playwright is only used to establish and persist the session (login).
All other operations (search, detail pages, download) use httpx with the saved cookies.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import ssl
import httpx

from src.config import ZLIBRARY_BASE_URL, ZLIBRARY_SESSION_PATH

# Bypass SSL verification when a proxy/MITM intercepts HTTPS
# Z-Library content is benign book download data
_SSL_CONTEXT = ssl.create_default_context()
_SSL_CONTEXT.check_hostname = False
_SSL_CONTEXT.verify_mode = ssl.CERT_NONE


@dataclass(frozen=True)
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


class ZLibraryHttpClient:
    """HTTP-based ZLibrary client using saved session cookies.

    Requires a valid session cookie file (from prior Playwright login).
    Playwright is only used for the initial login; all other operations
    use httpx with the saved cookies.
    """

    BASE_URL = ZLIBRARY_BASE_URL
    USER_AGENT = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    )

    def __init__(self) -> None:
        self._client: httpx.Client | None = None
        self._raw_cookies: list[dict[str, Any]] = []
        self._load_cookies()

    # -------------------------------------------------------------------------
    # Cookie / session management
    # -------------------------------------------------------------------------

    def _load_cookies(self) -> None:
        """Load cookies from the saved session file (Playwright format)."""
        if not ZLIBRARY_SESSION_PATH.exists():
            return
        try:
            self._raw_cookies = json.loads(ZLIBRARY_SESSION_PATH.read_text())
        except Exception:
            pass

    def _build_client(self) -> httpx.Client:
        """Build an httpx client with the current cookies.

        Converts Playwright-format cookies (list of dicts with name/value/domain/path)
        into httpx-compatible dict format.
        """
        cookie_dict = {c["name"]: c["value"] for c in self._raw_cookies if "name" in c}
        return httpx.Client(
            base_url=self.BASE_URL,
            cookies=cookie_dict,
            timeout=30.0,
            follow_redirects=True,
            headers={"User-Agent": self.USER_AGENT},
            trust_env=False,
            verify=_SSL_CONTEXT,
        )

    def _ensure_client(self) -> httpx.Client:
        if self._client is None:
            self._client = self._build_client()
        return self._client

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def is_logged_in(self) -> bool:
        """Check if current cookies represent a logged-in session."""
        client = self._ensure_client()
        resp = client.get("/")
        return "login" not in resp.url.path

    def search(self, query: str, limit: int = 10, offset: int = 0) -> list[BookMetadata]:
        """Search books via HTTP and parse the HTML response.

        Search URL: https://zh.zlib.li/s/{query}
        The page returns server-side rendered HTML when logged in.
        """
        client = self._ensure_client()
        resp = client.get(f"/s/{query}")
        resp.raise_for_status()
        return self._parse_search_html(resp.text, limit, offset)

    def get_download_url(self, book_id: str) -> str:
        """Fetch a book detail page and extract the /dl/ link.

        Detail URL: https://zh.zlib.li/book/{book_id}/{slug}.html
        """
        client = self._ensure_client()
        resp = client.get(f"/book/{book_id}")
        resp.raise_for_status()
        return self._parse_download_link(resp.text)

    def download_file(self, url: str, dest_path: Path) -> Path:
        """Download a file from a direct URL (or /dl/ path) to dest_path.

        If url is a relative path (e.g. /dl/xxx), it is joined with BASE_URL.
        The CDN redirect is followed automatically via follow_redirects=True.
        """
        client = self._ensure_client()

        if url.startswith("http"):
            full_url = url
        elif url.startswith("/"):
            full_url = f"{self.BASE_URL}{url}"
        else:
            full_url = f"{self.BASE_URL}/{url}"

        with client.stream("GET", full_url) as resp:
            resp.raise_for_status()
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with dest_path.open("wb") as f:
                for chunk in resp.iter_bytes(chunk_size=65536):
                    f.write(chunk)

        return dest_path

    # -------------------------------------------------------------------------
    # HTML parsing helpers
    # -------------------------------------------------------------------------

    def _parse_search_html(self, html: str, limit: int, offset: int) -> list[BookMetadata]:
        """Parse book cards from search page HTML.

        Book links are: <a href="/book/{book_id}/{slug}.html" ...>
        """
        results: list[BookMetadata] = []
        seen_ids: set[str] = set()

        # Find all book detail URLs
        # Pattern: /book/{book_id}/{slug}.html
        book_pattern = re.compile(r'/book/([a-zA-Z0-9]+)/[^/]+\.html')
        for match in book_pattern.finditer(html):
            book_id = match.group(1)
            if book_id in seen_ids:
                continue
            seen_ids.add(book_id)
            href = match.group(0)

            # Extract title and author from nearby HTML context
            title, author = self._extract_card_meta(html, match.start())

            results.append(
                BookMetadata(
                    title=title or "Unknown",
                    author=author or "Unknown",
                    year="",
                    language="",
                    format="",
                    size="",
                    download_url=href,
                    book_id=book_id,
                )
            )

            if len(results) >= limit + offset:
                break

        return results[offset : offset + limit]

    def _extract_card_meta(self, html: str, book_link_pos: int) -> tuple[str, str]:
        """Extract title and author from HTML context around a book link position."""
        window_start = max(0, book_link_pos - 3000)
        window = html[window_start:book_link_pos + 200]

        title = ""
        author = ""

        # Title: look for data-title attribute near the link
        title_match = re.search(r'data-title="([^"]+)"', window)
        if title_match:
            title = self._unescape_html(title_match.group(1))

        # Author: look for author patterns near the link
        author_match = re.search(r'data-authors="([^"]+)"', window)
        if author_match:
            author = author_match.group(1).split(",")[0].strip()

        if not author:
            author_match = re.search(r'/author/[^"]+">([^<]+)<', window)
            if author_match:
                author = author_match.group(1).strip()

        return title, author

    def _parse_download_link(self, html: str) -> str:
        """Extract the /dl/ link from a book detail page HTML."""
        match = re.search(r'href="(/dl/[^"]+)"', html)
        if match:
            return match.group(1)
        return ""

    @staticmethod
    def _unescape_html(text: str) -> str:
        """Unescape basic HTML entities."""
        return (
            text.replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&quot;", '"')
            .replace("&#39;", "'")
            .replace("&nbsp;", " ")
        )

    def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self) -> "ZLibraryHttpClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
