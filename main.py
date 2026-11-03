"""Personal AI Assistant - Root Entrypoint.

Delegates to:
- agent.runner: Command-line interface for running multi-agent queries.
- backend.run: Web API and frontend server on http://localhost:8000.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
AGENT_DIR = PROJECT_ROOT / "agent"
BACKEND_DIR = PROJECT_ROOT / "backend"

for p in (PROJECT_ROOT, AGENT_DIR, BACKEND_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def main():
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("server", "serve", "api"):
        from backend.run import main as run_server
        sys.argv.pop(1)
        run_server()
    else:
        from agent.runner import main as run_agent
        run_agent()


if __name__ == "__main__":
    main()
