"""Tools package exporting all specialist tool functions."""

from .weather_tools import (
    get_current_weather,
    get_weather_forecast,
)
from .utility_tools import (
    add_todo,
    calculate,
    complete_todo,
    convert_units,
    days_until,
    delete_todo,
    fetch_url_text,
    get_current_time,
    get_system_status,
    list_files,
    list_todos,
    log_activity,
    read_file_content,
    read_notes,
    save_note,
    update_note,
    update_todo,
)
from .research_tools import (
    web_search,
    fetch_news,
    summarize_url,
)
from .finance_tools import (
    log_expense,
    get_expense_summary,
    list_expenses,
    set_budget,
)
from .habit_tools import (
    log_habit,
    log_water,
    log_workout,
    get_habit_status,
)
from .briefing_tools import (
    get_daily_briefing,
)
from .drafting_tools import (
    draft_email,
    polish_message,
    draft_meeting_agenda,
)
from .dev_tools import (
    inspect_code,
    check_python_syntax,
    git_helper,
    run_command_safe,
)
from .knowledge_tools import (
    save_knowledge,
    search_knowledge,
    list_knowledge_topics,
)

__all__ = [
    # Weather
    "get_current_weather",
    "get_weather_forecast",
    # Utility & Storage
    "calculate",
    "convert_units",
    "get_current_time",
    "days_until",
    "save_note",
    "read_notes",
    "update_note",
    "add_todo",
    "list_todos",
    "update_todo",
    "complete_todo",
    "delete_todo",
    "list_files",
    "read_file_content",
    "get_system_status",
    "fetch_url_text",
    "log_activity",
    # Research
    "web_search",
    "fetch_news",
    "summarize_url",
    # Finance
    "log_expense",
    "get_expense_summary",
    "list_expenses",
    "set_budget",
    # Habit & Health
    "log_habit",
    "log_water",
    "log_workout",
    "get_habit_status",
    # Briefing
    "get_daily_briefing",
    # Drafting
    "draft_email",
    "polish_message",
    "draft_meeting_agenda",
    # Dev
    "inspect_code",
    "check_python_syntax",
    "git_helper",
    "run_command_safe",
    # Knowledge
    "save_knowledge",
    "search_knowledge",
    "list_knowledge_topics",
]
