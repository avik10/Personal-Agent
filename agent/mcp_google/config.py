"""Configuration for Google Workspace MCP Server."""

import os
from pathlib import Path
from dotenv import load_dotenv

AGENT_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = AGENT_DIR.parent

# Load .env from agent directory or project root
load_dotenv(AGENT_DIR / ".env")
load_dotenv(PROJECT_ROOT / ".env")

# Base storage directory for credentials inside agent/storage/google_credentials
DEFAULT_STORAGE_DIR = AGENT_DIR / "storage" / "google_credentials"
DEFAULT_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Credentials & Token file paths
CREDENTIALS_PATH = Path(
    os.getenv("GOOGLE_CREDENTIALS_FILE", str(DEFAULT_STORAGE_DIR / "credentials.json"))
)
# Also check root for credentials.json as convenient fallback
if not CREDENTIALS_PATH.exists() and (PROJECT_ROOT / "credentials.json").exists():
    CREDENTIALS_PATH = PROJECT_ROOT / "credentials.json"

TOKEN_PATH = Path(
    os.getenv("GOOGLE_TOKEN_FILE", str(DEFAULT_STORAGE_DIR / "token.json"))
)

# Target OAuth Scopes
DEFAULT_SCOPES = [
    # Gmail: read, compose, send, modify message labels/stars
    "https://www.googleapis.com/auth/gmail.modify",
    # Calendar: read, create, update, delete events and agendas
    "https://www.googleapis.com/auth/calendar",
    # Drive: search, read, export, upload documents and files
    "https://www.googleapis.com/auth/drive",
    # Docs: read and edit Google Docs
    "https://www.googleapis.com/auth/documents",
    # Tasks: read, create, and complete tasks
    "https://www.googleapis.com/auth/tasks",
]
