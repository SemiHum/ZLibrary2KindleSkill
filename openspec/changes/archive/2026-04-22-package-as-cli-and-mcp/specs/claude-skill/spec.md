## ADDED Requirements

### Requirement: Claude Code skill manifest
The system SHALL provide a skill definition at `~/.claude/skills/zlibrary2kindle/skill.md` that Claude Code can discover and load.

#### Scenario: Skill loaded by Claude Code
- **WHEN** Claude Code is configured to load skills from `~/.claude/skills/`
- **THEN** the skill at `~/.claude/skills/zlibrary2kindle/skill.md` is available for invocation

### Requirement: Skill provides tool descriptions
The skill manifest SHALL describe the available tools (login, search, download, send) so Claude Code knows how to invoke them.

#### Scenario: Tool descriptions available
- **WHEN** Claude Code reads the skill definition
- **THEN** it can see descriptions of all 4 tools: login, search, download, send

### Requirement: Skill does not duplicate code
The skill definition SHALL reference the existing tools without duplicating implementation.

#### Scenario: Code in this repo
- **WHEN** Claude Code invokes a skill tool
- **THEN** execution happens via the installed MCP server or CLI, not within the skill
