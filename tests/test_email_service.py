"""Tests for email_service.py."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.services.email_service import EmailService


@pytest.fixture
def email_service():
    """EmailService with mocked config getters."""
    with patch("src.config.get_smtp_host", return_value="smtp.test.com"):
        with patch("src.config.get_smtp_port", return_value=587):
            with patch("src.config.get_sender_email", return_value="test@test.com"):
                with patch("src.config.get_sender_password", return_value="password"):
                    yield EmailService()


def test_send_book_success(email_service, tmp_path):
    """Send book email with valid file and recipient."""
    book_file = tmp_path / "test.epub"
    book_file.write_bytes(b"fake epub content")

    with patch.object(email_service, "_sender", "test@test.com"):
        with patch("smtplib.SMTP") as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            result = email_service.send_book(book_file, "Test Book", "kindle@kindle.com")

    assert result["status"] == "sent"
    assert result["recipient"] == "kindle@kindle.com"
    assert result["file"] == "test.epub"
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("test@test.com", "password")
    mock_server.sendmail.assert_called_once()


def test_send_book_file_not_found():
    """Error returned when file does not exist."""
    with patch("src.config.get_smtp_host", return_value="smtp.test.com"):
        with patch("src.config.get_smtp_port", return_value=587):
            with patch("src.config.get_sender_email", return_value="test@test.com"):
                with patch("src.config.get_sender_password", return_value="password"):
                    svc = EmailService()
                    result = svc.send_book(
                        Path("/nonexistent/book.epub"), "Test", "kindle@kindle.com"
                    )
    assert result["status"] == "error"
    assert "not found" in result["message"]
