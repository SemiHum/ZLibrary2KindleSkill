# ZLibrary2KindleSkill

Search Z-Library books and send them to your Kindle via email. Supports both CLI and Claude Code MCP mode.

**Features:**
- Search Z-Library by title, author, ISBN
- Download books (EPUB preferred, PDF fallback)
- Send directly to Kindle email
- Session cookies persisted — login once, reuse automatically
- Two-factor auth supported via app password

> **Language**: English | [中文](./README_CN.md)

## Prerequisites

- **ZLibrary account** — email and password
- **Kindle email whitelisted** — Add sender in Amazon account settings
- **Gmail App Password** — Required for Gmail SMTP with 2FA

## Setup

### 1. Install

```bash
pip install -e .
```

### 2. Configure credentials

**Method A — `~/.zshrc` (recommended)**

Add to `~/.zshrc`:

```bash
export ZLIBRARY_EMAIL="your@email.com"
export ZLIBRARY_PASSWORD="your-password"
export KINDLE_EMAIL="your-name@kindle.com"
export SENDER_EMAIL="your@email.com"
export SENDER_PASSWORD="xxxx xxxx xxxx xxxx"  # Gmail App Password
```

Then `source ~/.zshrc`.

**Method B — `mcp.json` env**

Edit `mcp.json` and fill in the `env` block.

> **Security**: Method A keeps credentials out of your project directory. Method B stores them in plaintext.

## Step-by-Step Guide

- [Beginner Guide (English)](./SOP.md)
- [傻瓜指南（中文）](./SOP_CN.md)

## Quick Start

```bash
# 1. Login (once)
python -m src.cli login

# 2. Search
python -m src.cli search "Mo Yan"

# 3. Download (copy book_id from search results)
python -m src.cli download <book_id>

# 4. Send to Kindle
python -m src.cli send /tmp/zlibrary2kindle/downloads/book.epub "Book Title"
```

## CLI Reference

| Command | Description |
|---------|-------------|
| `python -m src.cli login` | Authenticate to ZLibrary. Session is saved automatically. |
| `python -m src.cli search "query" --limit 10` | Search books. Returns `[book_id] title \| author`. |
| `python -m src.cli download <book_id>` | Download book to `/tmp/zlibrary2kindle/downloads/`. |
| `python -m src.cli send <file> "Title"` | Email file to Kindle. |

> **Note**: If `zlib2k-cli` command is not found after install, use `python -m src.cli` instead.

## Claude Code Skill

Load as a Claude Code local MCP server for AI-assisted book search and sending:

```json
// mcp.json
{
  "mcpServers": {
    "zlibrary2kindle": {
      "command": "python",
      "args": ["-m", "src.server"]
    }
  }
}
```

Then you can ask Claude in natural language:

```
帮我下载莫言的书发送到Kindle
Search for books by Yu Hua and send them to my Kindle
```

Claude Code will automatically use the `zlibrary_login`, `zlibrary_search`, `zlibrary_download`, and `kindle_send_email` tools to complete the task.

## Architecture

```
src/
├── mcp_tools/          # MCP tool definitions
│   ├── zlibrary_login.py
│   ├── zlibrary_search.py
│   ├── zlibrary_download.py
│   └── kindle_send_email.py
├── services/           # Business logic
│   ├── playwright_service.py    # Browser lifecycle
│   ├── zlibrary_service.py      # ZLibrary flows
│   └── email_service.py        # SMTP sending
├── server.py           # MCP server entry
└── cli.py             # CLI entry point
```

## Troubleshooting

**"Session expired" or download fails**
: Run `python -m src.cli login` again to refresh session cookies.

**Login page changed / Cloudflare challenge**
: Try `python -m src.cli login --no-headless` to see the browser and solve CAPTCHA manually.

**Email too large for Kindle**
: Google/Gmail limits attachments to ~25MB. PDFs often exceed this. Try searching for EPUB format instead.

**PDF Chinese fonts missing on Kindle**
: EPUB format renders Chinese better on Kindle. Download EPUB when available.
