"""Configuration for Google Keep MCP Server."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base agent and storage directories
AGENT_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = AGENT_DIR.parent

# Load environment files
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(AGENT_DIR / ".env")

# Dedicated storage directory for Google Keep master tokens & caches
KEEP_STORAGE_DIR = AGENT_DIR / "storage" / "google_keep"
KEEP_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

KEEP_TOKEN_FILE = KEEP_STORAGE_DIR / "token.json"

# Credentials from environment
GOOGLE_KEEP_EMAIL = (
    os.getenv("GOOGLE_KEEP_EMAIL")
    or os.getenv("GOOGLE_EMAIL")
    or "avik.bhattacharjya28@gmail.com"
).strip()

GOOGLE_KEEP_APP_PASSWORD = os.getenv("GOOGLE_KEEP_APP_PASSWORD", "").strip()
GOOGLE_KEEP_MASTER_TOKEN = os.getenv("GOOGLE_KEEP_MASTER_TOKEN", "").strip()
