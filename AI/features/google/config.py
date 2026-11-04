"""Configuration for Google Workspace MCP Server."""

import os
from pathlib import Path
from dotenv import load_dotenv

AI_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = AI_DIR.parent

# Load .env from AI directory or project root
load_dotenv(AI_DIR / ".env")
load_dotenv(PROJECT_ROOT / ".env")
if not os.getenv("GROQ_API_KEY") and (PROJECT_ROOT / ".env.prod").exists():
    load_dotenv(PROJECT_ROOT / ".env.prod")

# Base storage directory for credentials inside AI/storage/google_credentials
DEFAULT_STORAGE_DIR = AI_DIR / "storage" / "google_credentials"
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

# Auto-hydrate credentials from environment variable if set (ideal for Render / Cloud production)
env_creds = os.getenv("GOOGLE_CREDENTIALS_JSON") or os.getenv("GOOGLE_WORKSPACE_CREDENTIALS")
if env_creds and not CREDENTIALS_PATH.exists():
    try:
        CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CREDENTIALS_PATH, "w") as f:
            f.write(env_creds.strip())
    except Exception as e:
        pass

env_token = os.getenv("GOOGLE_TOKEN_JSON") or os.getenv("GOOGLE_WORKSPACE_TOKEN")
if env_token and not TOKEN_PATH.exists():
    try:
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_PATH, "w") as f:
            f.write(env_token.strip())
    except Exception as e:
        pass

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
    # Tasks: read, create, and complete tasks & notes
    "https://www.googleapis.com/auth/tasks",
]
