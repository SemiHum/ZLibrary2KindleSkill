## Context

ZLibrary2KindleSkill currently runs only as an MCP server (`python -m src.server`). The user wants CLI access and Claude Code skill discovery.

**Current state:**
- `src/server.py` — MCP server entry point (uses `mcp.server`)
- `src/mcp_tools/` — 4 independent tools (login, search, download, send_email)
- `src/services/` — Business logic (playwright_service, zlibrary_service, email_service)
- No CLI, no skill definition

## Goals / Non-Goals

**Goals:**
- `zlibrary2kindle` CLI with `login`, `search`, `download`, `send` subcommands
- Local MCP manifest via `mcp.json`
- Claude Code skill definition in `~/.claude/skills/`
- Single `pip install -e .` makes everything available

**Non-Goals:**
- Cloud-hosted MCP or remote service
- Web UI
- User management beyond ZLibrary session

## Decisions

### 1. CLI Framework: `click`

Use `click` for CLI. Battle-tested, clean subcommand support, simpler than `typer` for this use case.

### 2. Separate entry points

Keep `src/server.py` for MCP. Create `src/cli.py` for CLI. Use `console_scripts` to route `zlibrary2kindle` command to `src.cli:main`. Separate files avoid complex if/else dispatch.

### 3. MCP manifest: `mcp.json` at project root

```json
{
  "mcpServers": {
    "zlibrary2kindle": {
      "command": "python",
      "args": ["-m", "src.server"]
    }
  }
}
```

Claude Code scans project roots for `mcp.json`.

### 4. Claude Code Skill: `~/.claude/skills/zlibrary2kindle/skill.md`

Skill manifest in user-level skills directory. Code stays in this repo; skill provides tool definitions and usage instructions for Claude Code.

### 5. MCP tools unchanged

Service layer (`zlibrary_service`, `email_service`) is already tool-agnostic. CLI wraps the same services.

## Architecture

```
pip install -e .
     │
     ├── zlibrary2kindle CLI  ──→  src/cli.py
     │
     ├── mcp.json manifest   ──→  Claude Code MCP discovery
     │
     └── python -m src.server ──→  MCP server mode

~/.claude/skills/zlibrary2kindle/skill.md  ──→  Claude Code skill discovery
```

## CLI Interface

```
zlibrary2kindle login                    # authenticate to ZLibrary
zlibrary2kindle search <query>           # search books
zlibrary2kindle download <book-id>       # download by book ID
zlibrary2kindle send <file> <title>      # email file to Kindle
zlibrary2kindle --help                  # show all commands
```

## Risks / Trade-offs

- [Risk] Playwright browser state conflict if CLI and MCP used simultaneously → **Mitigation:** Single browser instance is normal; warn users not to run both at once.
- [Risk] Skill installation requires manual step to `~/.claude/skills/` → **Mitigation:** Document in skill README.

## Open Questions

1. Should CLI support `--output-dir` or always use `DOWNLOAD_DIR`?
2. Should skill auto-invoke `login` if session expired?
3. Should `search "query" --send` do search + download + send in one command?
