"""Standalone CLI entrypoint for Google Keep MCP Server."""

import sys
from .server import server

if __name__ == "__main__":
    print("Starting Google Keep MCP Server (stdio)...", file=sys.stderr)
    server.run(transport="stdio")
