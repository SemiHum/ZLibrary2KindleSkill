"""Pytest fixtures and shared test configuration."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def clean_env():
    """Ensure tests run without real credentials."""
    env = {
        "ZLIBRARY_EMAIL": "test@example.com",
        "ZLIBRARY_PASSWORD": "testpassword",
        "KINDLE_EMAIL": "kindle@test.com",
        "SENDER_EMAIL": "sender@test.com",
        "SENDER_PASSWORD": "testpassword",
        "SMTP_HOST": "smtp.test.com",
        "SMTP_PORT": "587",
        "ZLIBRARY_SESSION_PATH": str(Path("/tmp/test_session.json")),
        "DOWNLOAD_DIR": str(Path("/tmp/test_downloads")),
    }
    with patch.dict(os.environ, env, clear=False):
        yield
