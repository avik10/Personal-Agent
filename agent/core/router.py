"""Supervisor Intent Router and Sub-task Decomposition for Multi-Agent System."""

import re
from typing import Dict, List, Tuple


def decompose_query(user_query: str) -> Tuple[List[str], Dict[str, str]]:
    """Analyze the user query, determine target agent(s), and scope sub-tasks for each.
    
    This ensures each agent only receives the part of the query it is responsible for,
    preventing unintended data contamination.
    """
    raw_parts = [p.strip() for p in re.split(r'[,;]|\band\b|\balso\b', user_query, flags=re.IGNORECASE) if p.strip()]
    tasks: Dict[str, str] = {}

    for p in raw_parts:
        pl = p.lower()

        # Briefing check (composite request)
        if any(k in pl for k in ["briefing", "daily digest", "morning summary", "my day look like", "day snapshot"]):
            tasks["briefing"] = (tasks.get("briefing", "") + " " + p).strip()

        # Weather
        elif any(k in pl for k in ["weather", "temperature", "forecast", "rain", "sunny", "climate", "temp"]):
            tasks["weather"] = (tasks.get("weather", "") + " " + p).strip()

        # Finance
        elif (
            any(k in pl for k in ["expense", "spent", "spending", "cost", "bought", "budget", "rupee", "rupees", "₹", "paid", "bill"])
            or bool(re.search(r'(?:spent|paid|cost)\s*(?:rs\.?|₹)?\s*\d+', pl))
        ):
            tasks["finance"] = (tasks.get("finance", "") + " " + p).strip()

        # Habit & Health
        elif any(k in pl for k in ["habit", "streak", "workout", "gym", "water", "drank", "exercise", "hydration", "pushup"]):
            tasks["habit"] = (tasks.get("habit", "") + " " + p).strip()

        # Google Workspace & Services (Sending emails, Gmail, Calendar, Drive, Docs, Tasks, Account)
        elif (
            any(k in pl for k in [
                "send email", "send mail", "send an email", "send a mail", "email to", "mail to", "reply to email",
                "gmail", "emails", "inbox", "unread mail", "read mail",
                "calendar", "agenda", "google meet", "events today", "upcoming meeting", "schedule meeting",
                "google drive", "drive file", "drive files", "my drive",
                "google doc", "google docs",
                "google task", "google tasks",
                "google account", "google service", "google services", "google mcp", "connect to google"
            ])
            and not any(k in pl for k in ["google search", "search google", "search the web"])
        ):
            tasks["google"] = (tasks.get("google", "") + " " + p).strip()

        # Drafting (Composing draft templates and polishing text without direct execution)
        elif any(k in pl for k in ["draft", "write an email", "compose", "polish text", "meeting agenda"]):
            tasks["drafting"] = (tasks.get("drafting", "") + " " + p).strip()

        # Task & Notes
        elif any(k in pl for k in ["note", "todo", "to-do", "task", "meeting", "schedule", "remind", "reminder"]):
            tasks["task_notes"] = (tasks.get("task_notes", "") + " " + p).strip()

        # Research & Web
        elif any(k in pl for k in ["search", "google", "lookup", "news", "headline", "browse", "article"]):
            tasks["research"] = (tasks.get("research", "") + " " + p).strip()

        # Utility & Computation
        elif (
            any(k in pl for k in ["calculate", "calc", "convert", "unit", "time", "clock", "system status"])
            or bool(re.search(r'\d+\s*[\+\-\*\/\^]\s*\d+', pl))
        ):
            tasks["utility"] = (tasks.get("utility", "") + " " + p).strip()

        # General
        else:
            tasks["general"] = (tasks.get("general", "") + " " + p).strip()

    valid_order = [
        "briefing",
        "google",
        "weather",
        "finance",
        "habit",
        "drafting",
        "dev",
        "knowledge",
        "task_notes",
        "research",
        "utility",
    ]
    active_agents = [k for k in valid_order if k in tasks]

    if not active_agents:
        active_agents = ["general"]
        tasks["general"] = user_query

    # If only one agent is active, pass the full user query
    if len(active_agents) == 1:
        tasks[active_agents[0]] = user_query

    return active_agents, tasks


def supervisor_router(user_query: str) -> List[str]:
    """Determine active agents for routing."""
    active, _ = decompose_query(user_query)
    return active
