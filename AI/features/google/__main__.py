"""CLI launcher for mcp_google package.

Usage:
  python3 -m mcp_google               # Runs the MCP server (stdio transport)
  python3 -m mcp_google setup         # Runs OAuth setup authorization flow
  python3 -m mcp_google check         # Checks current authorization status
  python3 -m mcp_google instructions  # Prints step-by-step Google Cloud project setup
"""

import sys

if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] in ("setup", "auth", "setup_auth", "setup-auth", "login"):
        from .setup_auth import main as setup_main
        sys.argv.pop(1)
        setup_main()
    elif args and args[0] in ("check", "status"):
        from .setup_auth import main as setup_main
        sys.argv = [sys.argv[0], "--check"]
        setup_main()
    elif args and args[0] in ("instructions", "help-setup"):
        from .setup_auth import main as setup_main
        sys.argv = [sys.argv[0], "--instructions"]
        setup_main()
    else:
        from .server import main
        main()
