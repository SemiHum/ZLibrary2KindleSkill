## 1. Setup

- [x] 1.1 Add `click` to `pyproject.toml` dependencies
- [x] 1.2 Add `console_scripts` entry point to `pyproject.toml` pointing to `src.cli:main`

## 2. CLI Implementation

- [x] 2.1 Create `src/cli.py` with `click` group and `login` subcommand
- [x] 2.2 Add `search` subcommand to CLI
- [x] 2.3 Add `download` subcommand to CLI
- [x] 2.4 Add `send` subcommand to CLI
- [x] 2.5 Verify `zlibrary2kindle --help` works after `pip install -e .`

## 3. MCP Packaging

- [x] 3.1 Create `mcp.json` at project root with local server manifest
- [x] 3.2 Verify `python -m src.server` starts MCP server correctly

## 4. Claude Code Skill

- [x] 4.1 Create skill directory at `~/.claude/skills/zlibrary2kindle/`
- [x] 4.2 Write `skill.md` with tool descriptions for all 4 tools
- [x] 4.3 Document installation steps in skill README

## 5. Verification

- [x] 5.1 Run `pytest tests/ -v` — all tests still pass
- [x] 5.2 End-to-end test: CLI search + download + send to Kindle
