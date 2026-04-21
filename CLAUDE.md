# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ZLibrary2KindleSkill is a Local MCP (Model Context Protocol) that searches Z-Library, downloads books (preferring EPUB, then PDF), and sends them to a Kindle email address for synchronization.

## Tech Stack

- **Language**: Python 3.11+
- **Browser Automation**: Playwright (for ZLibrary login, search, download)
- **MCP**: Local MCP server
- **Email**: SMTP (Kindle personal email sending)

## Architecture

```
src/
├── mcp_tools/          # MCP tool definitions (one file per tool)
│   ├── __init__.py
│   ├── zlibrary_login.py
│   ├── zlibrary_search.py
│   ├── zlibrary_download.py
│   └── kindle_send_email.py
├── services/           # Business logic layer
│   ├── __init__.py
│   ├── playwright_service.py    # Playwright browser management
│   ├── zlibrary_service.py      # ZLibrary interactions
│   └── email_service.py        # Kindle email sending
├── server.py           # MCP server entry point
└── config.py           # Configuration (env vars, credentials)
```

### MCP Tools (4 independent tools)

| Tool | Responsibility | Key Methods |
|------|---------------|-------------|
| `zlibrary_login` | Authenticate to ZLibrary | Browser setup, credentials, session persistence |
| `zlibrary_search` | Search books by query | Pagination, result parsing, metadata extraction |
| `zlibrary_download` | Download book files | Format preference (epub > pdf), file saving |
| `kindle_send_email` | Email book to Kindle | SMTP, attachment, recipient validation |

### Service Layer

- **playwright_service**: Manages browser lifecycle (launch, context, page, close). All ZLibrary operations use this.
- **zlibrary_service**: Wraps Playwright calls for ZLibrary-specific flows (login, search, download URLs).
- **email_service**: SMTP email composition and sending.

### Data Flow

```
zlibrary_login → zlibrary_search → zlibrary_download → kindle_send_email
```

Each tool is independently callable. Credentials and session state are managed via `config.py` (env vars).

## Configuration

All sensitive values via environment variables (see `.env.example`):

| Variable | Description |
|----------|-------------|
| `ZLIBRARY_EMAIL` | ZLibrary account email |
| `ZLIBRARY_PASSWORD` | ZLibrary account password |
| `KINDLE_EMAIL` | Target Kindle email address |
| `SENDER_EMAIL` | SMTP sender email |
| `SENDER_PASSWORD` | SMTP password or app password |
| `SMTP_HOST` | SMTP server host |
| `SMTP_PORT` | SMTP server port |

## Commands

```bash
# Install dependencies
pip install -e .

# Run MCP server (local)
python -m src.server

# Run tests
pytest tests/ -v

# Run a single test file
pytest tests/test_zlibrary_service.py -v

# Lint
ruff check src/

# Format
ruff format src/

# Type check
pyright src/
```

## ZLibrary Tool Behavior

### zlibrary_login
- Launches Playwright browser (headless by default)
- Navigates to ZLibrary login page, submits credentials
- Persists cookies/session to `~/.cache/zlibrary2kindle/session.json` (configurable via `ZLIBRARY_SESSION_PATH`)
- Returns: session status

### zlibrary_search
- Accepts: `query`, `limit` (default 10), `offset` (default 0)
- Returns: list of book metadata `{title, author, year, format, size, download_url}`
- Uses logged-in session from `zlibrary_login`

### zlibrary_download
- Accepts: `book_url` or `book_id`
- Downloads to temp directory, format preference: `epub > pdf`
- Returns: local file path

### kindle_send_email
- Accepts: `file_path`, `book_title`, `recipient_email` (optional, defaults to `KINDLE_EMAIL`)
- Sends book as attachment via SMTP, subject: `[Kindle] {book_title}`

## Notes

- Playwright session is persisted to disk (not in-memory) so tools can be independently invoked.
- ZLibrary may block automation — handle CAPTCHA or 2FA by having user do initial login manually and export session cookies.
- Downloaded files are temp files — clean up after emailing.
- Kindle email whitelisting must be configured in Amazon account settings.
