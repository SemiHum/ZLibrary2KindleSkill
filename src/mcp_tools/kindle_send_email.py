"""MCP tool: kindle_send_email — email a book to a Kindle address."""

from __future__ import annotations

from pathlib import Path

from src import config
from src.services.email_service import EmailService


def kindle_send_email(
    file_path: str,
    book_title: str,
    recipient_email: str | None = None,
) -> dict:
    """
    Send a book file as an email attachment to a Kindle device.

    Args:
        file_path: Local path to the book file (epub or pdf).
        book_title: Title of the book, used in email subject.
        recipient_email: Kindle email address. Defaults to KINDLE_EMAIL env var.

    Returns:
        dict with status "sent" or error details
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return {"status": "error", "message": f"File not found: {file_path}"}

        recipient = recipient_email or config.get_kindle_email()

        email_svc = EmailService()
        result = email_svc.send_book(path, book_title, recipient)

        # Clean up temp file after sending
        path.unlink(missing_ok=True)

        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}
