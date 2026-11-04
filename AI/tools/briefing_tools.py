"""Daily Digest & Morning Briefing Tools."""

from datetime import datetime
from tools.habit_tools import get_habit_status
from tools.utility_tools import get_current_time, list_todos, read_notes
from tools.weather_tools import get_current_weather


def get_daily_briefing(location: str = "Midnapore") -> str:
    """Generate a comprehensive morning briefing including today's date, live weather, pending tasks, and habits."""
    loc = location.strip() if location else "Midnapore"
    now_str = get_current_time()
    weather_info = get_current_weather(loc)
    todos_info = list_todos(show_completed=False)
    habit_info = get_habit_status()

    briefing_text = (
        f"═══════════════════════════════════════════════════════════════\n"
        f" 🌅  DAILY EXECUTIVE BRIEFING\n"
        f"     {now_str}\n"
        f"═══════════════════════════════════════════════════════════════\n\n"
        f"【WEATHER OUTLOOK】\n"
        f"{weather_info}\n\n"
        f"【PENDING TO-DOS & ACTION ITEMS】\n"
        f"{todos_info}\n\n"
        f"【HEALTH & HABIT SNAPSHOT】\n"
        f"{habit_info}\n\n"
        f"Have a productive and wonderful day!"
    )
    return briefing_text
