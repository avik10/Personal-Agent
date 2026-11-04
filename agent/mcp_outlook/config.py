"""Configuration for Microsoft Outlook & Graph API MCP Server."""

import os
from pathlib import Path
from dotenv import load_dotenv

AGENT_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = AGENT_DIR.parent

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(AGENT_DIR / ".env")

# Microsoft Storage Directory
DEFAULT_STORAGE_DIR = AGENT_DIR / "storage" / "microsoft_credentials"
DEFAULT_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Token file path
TOKEN_PATH = Path(
    os.getenv("MICROSOFT_TOKEN_FILE", str(DEFAULT_STORAGE_DIR / "token.json"))
)

# Auto-hydrate token from environment if configured (convenient for cloud deployment like Render)
env_token = os.getenv("MICROSOFT_TOKEN_JSON") or os.getenv("MICROSOFT_WORKSPACE_TOKEN")
if env_token and not TOKEN_PATH.exists():
    try:
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_PATH, "w") as f:
            f.write(env_token.strip())
    except Exception:
        pass

# Microsoft Azure App Credentials
# Tenant 'common' allows both personal Microsoft accounts (@outlook.com, @hotmail.com)
# and work/school organizational Microsoft 365 accounts.
MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID", "").strip()
MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET", "").strip()
MICROSOFT_TENANT_ID = os.getenv("MICROSOFT_TENANT_ID", "common").strip()
MICROSOFT_REDIRECT_URI = os.getenv("MICROSOFT_REDIRECT_URI", "").strip()

# Microsoft OAuth & Graph Endpoints
AUTH_ENDPOINT = f"https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}/oauth2/v2.0/authorize"
TOKEN_ENDPOINT = f"https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}/oauth2/v2.0/token"
GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"

# Target OAuth Scopes for Outlook
DEFAULT_SCOPES = [
    "offline_access",
    "User.Read",
    "Mail.Read",
    "Mail.ReadWrite",
    "Mail.Send",
]
