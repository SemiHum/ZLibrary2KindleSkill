"""Configuration loaded from environment variables."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ZLibrary
ZLIBRARY_EMAIL = os.environ.get("ZLIBRARY_EMAIL", "")
ZLIBRARY_PASSWORD = os.environ.get("ZLIBRARY_PASSWORD", "")

# Kindle
KINDLE_EMAIL = os.environ.get("KINDLE_EMAIL", "")

# SMTP
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "")
SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))


def _req(key: str, value: str) -> str:
    """Return value or raise if empty (for credentials that must be set)."""
    if not value:
        raise EnvironmentError(
            f"Required environment variable {key!r} is not set. "
            "Copy .env.example to .env and fill in your credentials."
        )
    return value


# Credentials that must be set
def get_zlibrary_email() -> str:
    return _req("ZLIBRARY_EMAIL", ZLIBRARY_EMAIL)


def get_zlibrary_password() -> str:
    return _req("ZLIBRARY_PASSWORD", ZLIBRARY_PASSWORD)


def get_kindle_email() -> str:
    return _req("KINDLE_EMAIL", KINDLE_EMAIL)


def get_sender_email() -> str:
    return _req("SENDER_EMAIL", SENDER_EMAIL)


def get_sender_password() -> str:
    return _req("SENDER_PASSWORD", SENDER_PASSWORD)


def get_smtp_host() -> str:
    return _req("SMTP_HOST", SMTP_HOST)


def get_smtp_port() -> int:
    port = os.environ.get("SMTP_PORT", "587")
    try:
        return int(port)
    except ValueError:
        raise EnvironmentError(f"SMTP_PORT must be an integer, got {port!r}")


# Session / paths
ZLIBRARY_BASE_URL = os.environ.get("ZLIBRARY_BASE_URL", "https://zh.zlib.li")
ZLIBRARY_SESSION_PATH = Path(
    os.environ.get("ZLIBRARY_SESSION_PATH", "~/.cache/zlibrary2kindle/session.json")
).expanduser()
ZLIBRARY_SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)

DOWNLOAD_DIR = Path(
    os.environ.get("DOWNLOAD_DIR", "/tmp/zlibrary2kindle/downloads")
)
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
