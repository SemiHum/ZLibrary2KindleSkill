"""MCP tool: zlibrary_login — authenticate to ZLibrary."""

from __future__ import annotations

from src import config
from src.services.playwright_service import PlaywrightService
from src.services.zlibrary_service import ZLibraryService


def zlibrary_login(headless: bool = True) -> dict:
    """
    Authenticate to ZLibrary using Playwright.

    Args:
        headless: Run browser in headless mode. Set False for debugging.

    Returns:
        dict with status "logged_in" or error details
    """
    try:
        email = config.get_zlibrary_email()
        password = config.get_zlibrary_password()

        pw = PlaywrightService()
        pw.launch(headless=headless)
        pw.new_context()

        zlib = ZLibraryService(pw)
        result = zlib.login(email, password)

        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        pw.close()
