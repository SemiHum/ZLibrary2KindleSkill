"""MCP tool: zlibrary_download — download a book from ZLibrary."""

from __future__ import annotations

import time
from pathlib import Path

from src.config import DOWNLOAD_DIR, ZLIBRARY_BASE_URL
from src.services.playwright_service import PlaywrightService
from src.services.zlibrary_service import ZLibraryService


def zlibrary_download(
    book_id: str | None = None, download_url: str | None = None
) -> dict:
    """
    Download a book from ZLibrary (preferring EPUB over PDF).

    Args:
        book_id: ZLibrary book ID (preferred — enables format preference).
        download_url: Direct download URL fallback.

    Returns:
        dict with status "success", file_path, and book metadata, or error details
    """
    try:
        pw = PlaywrightService()
        pw.launch()

        # Step 1: Get the download URL path using a session context
        ctx = pw.new_context()
        zlib = ZLibraryService(pw)

        if book_id:
            dl_path = zlib.get_download_url(book_id)  # returns /dl/xxx or full URL
        elif download_url:
            dl_path = download_url
        else:
            return {
                "status": "error",
                "message": "Either book_id or download_url is required",
            }
        ctx.close()

        # Step 2: Use a fresh context for the download to avoid Cloudflare
        # blocking internal navigations to /dl/ URLs
        dl_ctx = pw.new_context()
        dl_page = dl_ctx.new_page()

        # Ensure full URL
        if dl_path.startswith("http"):
            url = dl_path
        elif dl_path.startswith("/"):
            url = f"{ZLIBRARY_BASE_URL}{dl_path}"
        else:
            url = f"{ZLIBRARY_BASE_URL}/{dl_path}"

        with dl_page.expect_download(timeout=60_000) as download_info:
            dl_page.goto(url)

        download = download_info.value
        file_path = DOWNLOAD_DIR / download.suggested_filename
        download.save_as(str(file_path))
        dl_ctx.close()

        return {
            "status": "success",
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        pw.close()
