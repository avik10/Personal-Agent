"""Central Configuration & Environment Settings for Personal Agent."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base agent directory and project root
AGENT_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = AGENT_DIR  # Backwards compatibility
PROJECT_ROOT = AGENT_DIR.parent

# Load environment variables (.env and .env.prod support)
# 1. Load default .env from project root or agent directory
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(AGENT_DIR / ".env")

# 2. Support custom environment files (e.g. ENV_FILE=.env.prod or APP_ENV=production)
custom_env = os.getenv("ENV_FILE")
app_env = os.getenv("APP_ENV", "").lower().strip()

if custom_env:
    custom_path = Path(custom_env) if Path(custom_env).is_absolute() else PROJECT_ROOT / custom_env
    if custom_path.exists():
        load_dotenv(custom_path, override=True)
elif app_env in ("prod", "production") and (PROJECT_ROOT / ".env.prod").exists():
    load_dotenv(PROJECT_ROOT / ".env.prod", override=True)
elif (PROJECT_ROOT / ".env.prod").exists() and not (PROJECT_ROOT / ".env").exists():
    # In cloud environments where only .env.prod is provided
    load_dotenv(PROJECT_ROOT / ".env.prod", override=True)

# Storage directory and data file paths (inside agent/storage)
STORAGE_DIR = AGENT_DIR / "storage"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

NOTES_FILE = STORAGE_DIR / "notes.txt"
TODO_FILE = STORAGE_DIR / "todos.json"
ACTIVITY_LOG_FILE = STORAGE_DIR / "activity.log"
EXPENSES_FILE = STORAGE_DIR / "expenses.json"
HABITS_FILE = STORAGE_DIR / "habits.json"
KNOWLEDGE_FILE = STORAGE_DIR / "knowledge.json"

# Instructions path (inside agent/instructions)
INSTRUCTIONS_DIR = AGENT_DIR / "instructions"
INSTRUCTIONS_FILE = INSTRUCTIONS_DIR / "instructions.md"

# Groq Cloud API Configuration (for 24/7 cloud deployment)
# Get a free key at https://console.groq.com/keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b").strip()
GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "800"))

# Ollama LLM Configuration (Local Mode)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen3.5:8b")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.8"))

# Detection of Cloud Deployment (Render, Railway, Fly, Heroku, etc.)
IS_CLOUD_ENV = bool(
    os.getenv("RENDER")
    or os.getenv("RENDER_SERVICE_ID")
    or os.getenv("PORT")
    or os.getenv("DYNO")
    or os.getenv("RAILWAY_ENVIRONMENT")
    or os.getenv("FLY_APP_NAME")
)

# LLM Provider Resolution ('ollama' for local development, 'groq' for cloud production)
# Auto-detect Groq when GROQ_API_KEY is configured or running on cloud platforms (e.g. Render)
raw_provider = os.getenv("LLM_PROVIDER", "").lower().strip()
if raw_provider == "groq":
    LLM_PROVIDER = "groq"
elif raw_provider == "ollama":
    # If explicitly requested ollama, but we're in cloud container where localhost:11434 does not exist:
    if IS_CLOUD_ENV and GROQ_API_KEY:
        LLM_PROVIDER = "groq"
    else:
        LLM_PROVIDER = "ollama"
elif GROQ_API_KEY or IS_CLOUD_ENV:
    LLM_PROVIDER = "groq"
else:
    LLM_PROVIDER = "ollama"

# OpenWeatherMap API Configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
WEATHER_GEO_URL = "http://api.openweathermap.org/geo/1.0/direct"
