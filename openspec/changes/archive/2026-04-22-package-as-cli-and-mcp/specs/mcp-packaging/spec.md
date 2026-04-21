## ADDED Requirements

### Requirement: mcp.json manifest
The system SHALL provide an `mcp.json` file at the project root that describes the local MCP server.

#### Scenario: Manifest content
- **WHEN** Claude Code or another MCP client reads `mcp.json` from the project root
- **THEN** the file contains a valid MCP server manifest with `command: python` and `args: ["-m", "src.server"]`

### Requirement: MCP server mode
The system SHALL run as an MCP server when invoked via `python -m src.server`.

#### Scenario: Server starts
- **WHEN** user runs `python -m src.server`
- **THEN** the MCP server starts and listens for MCP requests on the default transport

### Requirement: Dual-mode compatibility
The MCP server mode and CLI mode SHALL coexist in the same installation without conflict.

#### Scenario: Both modes available
- **WHEN** user runs `pip install -e .`
- **THEN** both `zlibrary2kindle` CLI and `python -m src.server` MCP server are available
