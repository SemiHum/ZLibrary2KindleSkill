---
name: zlib2k-cli
description: Search Z-Library for books, download them, and send to your Kindle.
allowed-tools: Bash(zlib2k-cli:*) Bash(python:*) Bash(pip:*)
---

# ZLibrary2Kindle

Search Z-Library for books, download (EPUB preferred), and send to your Kindle via email.

## Prerequisites

1. **ZLibrary account** — email and password
2. **Kindle email whitelisted** — Add sender in Amazon account settings
3. **Gmail App Password** — Required for Gmail SMTP with 2FA

### Setup

```bash
# Install
pip install -e .

# Set environment variables
export ZLIBRARY_EMAIL="your@email.com"
export ZLIBRARY_PASSWORD="your-password"
export KINDLE_EMAIL="your-name@kindle.com"
export SENDER_EMAIL="your@email.com"
export SENDER_PASSWORD="xxxx xxxx xxxx xxxx"  # Gmail App Password
```

## Tools

### zlibrary_login

Authenticate to ZLibrary. Session cookies are saved to `~/.cache/zlibrary2kindle/session.json` and reused automatically.

```bash
zlib2k-cli login
python -m src.cli login
```

### zlibrary_search

Search for books by title, author, ISBN, etc.

```bash
zlib2k-cli search "Python programming"
python -m src.cli search "随园食单" --limit 5
```

Returns: list of books with `book_id` for use in download.

### zlibrary_download

Download a book by its `book_id` (from search results).

```bash
zlib2k-cli download w8n2rz2N8Q
python -m src.cli download <book_id>
```

Files saved to `/tmp/zlibrary2kindle/downloads/`.

### kindle_send_email

Send a downloaded book to your Kindle.

```bash
zlib2k-cli send /path/to/book.epub "Book Title"
python -m src.cli send /path/to/book.epub "Book Title" --to your@kindle.com
```

File is deleted after sending.

## Quick workflow

```bash
# 1. Login (once)
zlib2k-cli login

# 2. Search
zlib2k-cli search "随园食单"
# → [z9lRkJxQ8y] 随园食单 | [清]袁枚

# 3. Download
zlib2k-cli download z9lRkJxQ8y

# 4. Send to Kindle
zlib2k-cli send /tmp/zlibrary2kindle/downloads/随园食单.epub "随园食单"
```

## MCP Mode

When Claude Code has this project's MCP server loaded, tools are available directly: `zlibrary_login`, `zlibrary_search`, `zlibrary_download`, `kindle_send_email`.

## Configuration

| Variable | Description |
|----------|-------------|
| `ZLIBRARY_EMAIL` | ZLibrary account email |
| `ZLIBRARY_PASSWORD` | ZLibrary account password |
| `KINDLE_EMAIL` | Target Kindle email address |
| `SENDER_EMAIL` | SMTP sender email |
| `SENDER_PASSWORD` | SMTP password or Gmail App Password |
| `SMTP_HOST` | SMTP server (default: smtp.gmail.com) |
| `SMTP_PORT` | SMTP port (default: 587) |
