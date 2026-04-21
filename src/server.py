"""MCP server entry point for ZLibrary2KindleSkill."""

from __future__ import annotations

from mcp.server import Server
from mcp.types import Tool, TextContent

from src.mcp_tools import (
    zlibrary_login,
    zlibrary_search,
    zlibrary_download,
    kindle_send_email,
)

server = Server("zlibrary2kindle")


@server.list_tools()
def list_tools() -> list[Tool]:
    """Return all available MCP tools."""
    return [
        Tool(
            name="zlibrary_login",
            description="Authenticate to ZLibrary using Playwright browser automation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "headless": {
                        "type": "boolean",
                        "default": True,
                        "description": "Run browser in headless mode. Set False for debugging.",
                    },
                },
            },
        ),
        Tool(
            name="zlibrary_search",
            description="Search for books on ZLibrary.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query string."},
                    "limit": {
                        "type": "integer",
                        "default": 10,
                        "description": "Maximum number of results.",
                    },
                    "offset": {
                        "type": "integer",
                        "default": 0,
                        "description": "Number of results to skip for pagination.",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="zlibrary_download",
            description="Download a book from ZLibrary (preferring EPUB over PDF).",
            inputSchema={
                "type": "object",
                "properties": {
                    "book_id": {
                        "type": "string",
                        "description": "ZLibrary book ID (preferred).",
                    },
                    "download_url": {
                        "type": "string",
                        "description": "Direct download URL fallback.",
                    },
                },
            },
        ),
        Tool(
            name="kindle_send_email",
            description="Send a book file as an email attachment to a Kindle device.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Local path to the book file."},
                    "book_title": {"type": "string", "description": "Title of the book."},
                    "recipient_email": {
                        "type": "string",
                        "description": "Kindle email address. Defaults to KINDLE_EMAIL env var.",
                    },
                },
                "required": ["file_path", "book_title"],
            },
        ),
    ]


@server.call_tool()
def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Route tool calls to the appropriate handler."""
    if name == "zlibrary_login":
        result = zlibrary_login.zlibrary_login(**arguments)
    elif name == "zlibrary_search":
        result = zlibrary_search.zlibrary_search(**arguments)
    elif name == "zlibrary_download":
        result = zlibrary_download.zlibrary_download(**arguments)
    elif name == "kindle_send_email":
        result = kindle_send_email.kindle_send_email(**arguments)
    else:
        result = {"status": "error", "message": f"Unknown tool: {name}"}

    return [TextContent(type="text", text=str(result))]


if __name__ == "__main__":
    import mcp.server.stdio

    async def main():
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )

    import asyncio
    asyncio.run(main())
