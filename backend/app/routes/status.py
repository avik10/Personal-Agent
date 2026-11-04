"""System Status & Agent Directory Routes."""

from fastapi import APIRouter
from agent.config.settings import MODEL_NAME, LLM_PROVIDER, GROQ_MODEL
from agent.mcp_google.auth import is_authenticated as is_google_authenticated, get_account_info as get_google_account_info
from agent.mcp_outlook.auth import is_authenticated as is_microsoft_authenticated, get_account_info as get_microsoft_account_info

router = APIRouter(tags=["Status"])


@router.get("/api/status")
def get_system_status():
    """Retrieve health and connectivity status of the agent, Google Workspace, and Microsoft Outlook."""
    google_auth = is_google_authenticated()
    google_email = "Not authenticated"
    if google_auth:
        try:
            info = get_google_account_info()
            google_email = info.get("emailAddress", "Connected")
        except Exception:
            google_email = "Connected"

    ms_auth = is_microsoft_authenticated()
    ms_email = "Not authenticated"
    if ms_auth:
        try:
            ms_info = get_microsoft_account_info()
            ms_email = ms_info.get("email", "Connected")
        except Exception:
            ms_email = "Connected"

    active_model = f"{GROQ_MODEL} (Groq Cloud)" if LLM_PROVIDER == "groq" else MODEL_NAME

    return {
        "status": "online",
        "backend_model": active_model,
        "llm_provider": LLM_PROVIDER,
        "agents_count": 13,
        "google": {
            "authenticated": google_auth,
            "email": google_email,
            "connected_services": [
                "Gmail",
                "Google Calendar",
                "Google Drive",
                "Google Docs",
                "Google Tasks",
            ],
        },
        "microsoft": {
            "authenticated": ms_auth,
            "email": ms_email,
            "connected_services": [
                "Outlook Mail",
            ],
        },
    }


@router.get("/api/agents")
def get_agents():
    """List all 12 specialized agents with description and tags."""
    return {
        "agents": [
            {
                "id": "google",
                "name": "Google Workspace Agent",
                "description": "Real data from Gmail, Calendar, Drive, Docs, and Tasks via MCP",
                "icon": "mail",
                "tag": "MCP Integrated",
            },
            {
                "id": "outlook",
                "name": "Microsoft Outlook Agent",
                "description": "Real data from Microsoft Outlook mailbox, search & sending via Microsoft Graph MCP",
                "icon": "mail",
                "tag": "MCP Integrated",
            },
            {
                "id": "weather",
                "name": "Weather Specialist",
                "description": "Real-time conditions and 5-day forecasts via OpenWeatherMap",
                "icon": "cloud-sun",
                "tag": "API",
            },
            {
                "id": "task_notes",
                "name": "Task & Notes Specialist",
                "description": "Structured local notes, to-dos, and scheduled reminders",
                "icon": "check-square",
                "tag": "Local",
            },
            {
                "id": "utility",
                "name": "Utility Specialist",
                "description": "Math computations, unit conversions, time, system metrics",
                "icon": "calculator",
                "tag": "Local",
            },
            {
                "id": "research",
                "name": "Research Specialist",
                "description": "Web searches, article summaries, and information lookup",
                "icon": "search",
                "tag": "Web",
            },
            {
                "id": "finance",
                "name": "Finance Specialist",
                "description": "Expense logging, category breakdowns, and budget limits",
                "icon": "dollar-sign",
                "tag": "Local",
            },
            {
                "id": "habit_health",
                "name": "Habits & Health Specialist",
                "description": "Habit streak tracking, water logging, and workouts",
                "icon": "heart",
                "tag": "Local",
            },
            {
                "id": "briefing",
                "name": "Briefing Specialist",
                "description": "Executive morning briefings aggregating schedule and metrics",
                "icon": "sun",
                "tag": "Workflow",
            },
            {
                "id": "drafting",
                "name": "Drafting Specialist",
                "description": "Email drafts, polished messages, and meeting agendas",
                "icon": "edit-3",
                "tag": "Language",
            },
            {
                "id": "dev_assistant",
                "name": "Developer Assistant",
                "description": "Code inspection, git tips, syntax verification, dev commands",
                "icon": "code",
                "tag": "Code",
            },
            {
                "id": "memory_rag",
                "name": "Memory & Knowledge Specialist",
                "description": "Persistent personal knowledge base and fact retrieval",
                "icon": "database",
                "tag": "RAG",
            },
            {
                "id": "general",
                "name": "General Assistant",
                "description": "Natural dialogue, questions, and open conversational help",
                "icon": "message-circle",
                "tag": "Core",
            },
        ]
    }
