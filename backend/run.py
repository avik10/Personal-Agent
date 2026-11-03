"""Runner script for the FastAPI backend server."""

import sys
from pathlib import Path
import uvicorn

# Setup paths
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
AGENT_DIR = PROJECT_ROOT / "agent"

for p in (PROJECT_ROOT, AGENT_DIR, BACKEND_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def main():
    print("Starting Personal AI Agent Backend server on http://localhost:8000...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False, app_dir=str(BACKEND_DIR))


if __name__ == "__main__":
    main()
