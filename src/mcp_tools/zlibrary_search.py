"""MCP tool: zlibrary_search — search for books on ZLibrary."""

from __future__ import annotations

from src.services.playwright_service import PlaywrightService
from src.services.zlibrary_service import ZLibraryService


def zlibrary_search(query: str, limit: int = 10, offset: int = 0) -> dict:
    """
    Search for books on ZLibrary.

    Args:
        query: Search query string (title, author, ISBN, etc.)
        limit: Maximum number of results to return (default 10)
        offset: Number of results to skip for pagination (default 0)

    Returns:
        dict with status "success" and list of books, or error details
    """
    try:
        pw = PlaywrightService()
        pw.launch()
        pw.new_context()

        zlib = ZLibraryService(pw)
        books = zlib.search(query, limit=limit, offset=offset)

        return {
            "status": "success",
            "query": query,
            "count": len(books),
            "books": [
                {
                    "title": b.title,
                    "author": b.author,
                    "year": b.year,
                    "format": b.format,
                    "size": b.size,
                    "download_url": b.download_url,
                    "book_id": b.book_id,
                }
                for b in books
            ],
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        pw.close()
