"""FastAPI Backend Application Package."""

import sys
from pathlib import Path

# Add project root and agent directory to sys.path
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
AGENT_DIR = PROJECT_ROOT / "agent"

for p in (PROJECT_ROOT, AGENT_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
