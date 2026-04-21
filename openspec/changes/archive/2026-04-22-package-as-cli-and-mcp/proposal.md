## Why

ZLibrary2KindleSkill is currently usable only as an MCP server invoked by Claude Code. Users cannot run it directly from the terminal, and Claude Code cannot discover or load it as a skill without additional packaging. Packaging as both a standalone CLI and a local MCP makes it universally usable — with or without Claude Code — and enables skill-based loading.

## What Changes

- **New CLI entry point**: `zlibrary2kindle` command with subcommands for each tool (`login`, `search`, `download`, `send`)
- **MCP server packaging**: Register as a local MCP server via standard `mcp.json` manifest
- **Claude Code skill**: Skill definition so Claude Code can load and invoke tools natively
- **Single installation**: `pip install -e .` makes both CLI and MCP available
- **BREAKING**: Refactors `src/server.py` to support dual-mode: `python -m src.server` (MCP) and `zlibrary2kindle` (CLI)

## Capabilities

### New Capabilities

- `cli`: Command-line interface with subcommands mirroring MCP tools
- `mcp-packaging`: Local MCP server registration via `mcp.json` manifest
- `claude-skill`: Claude Code skill definition for skill-based tool invocation

### Modified Capabilities

- `server`: Refactor to support dual-mode (CLI + MCP) from a single entry point

## Impact

- New files: `src/cli.py`, `skill.md`, `mcp.json`
- Modified: `pyproject.toml` (console_scripts entry), `src/server.py` (dual-mode)
- New dependency: `click` or `typer` for CLI framework
- Existing deps: already has `mcp>=1.0.0`
