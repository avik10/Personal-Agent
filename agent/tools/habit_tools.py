"""Health, Habit, Water Intake, and Fitness Tracking Tools."""

import json
from datetime import datetime, timedelta
from typing import Dict, List
from config.settings import HABITS_FILE, STORAGE_DIR


def _load_habit_data() -> dict:
    if not HABITS_FILE.exists():
        return {"habits": {}, "water": {}, "workouts": []}
    try:
        with open(HABITS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return {"habits": {}, "water": {}, "workouts": []}
            data.setdefault("habits", {})
            data.setdefault("water", {})
            data.setdefault("workouts", [])
            return data
    except Exception:
        return {"habits": {}, "water": {}, "workouts": []}


def _save_habit_data(data: dict) -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    with open(HABITS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _calculate_streak(dates: list[str]) -> int:
    """Calculate consecutive daily streak ending today or yesterday."""
    if not dates:
        return 0
    unique_dates = sorted(set(dates), reverse=True)
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    try:
        latest = datetime.strptime(unique_dates[0], "%Y-%m-%d").date()
    except Exception:
        return 0

    if latest != today and latest != yesterday:
        return 0

    streak = 1
    current = latest
    for d_str in unique_dates[1:]:
        try:
            d = datetime.strptime(d_str, "%Y-%m-%d").date()
            if d == current - timedelta(days=1):
                streak += 1
                current = d
            elif d == current:
                continue
            else:
                break
        except Exception:
            break
    return streak


def log_habit(habit_name: str, notes: str = "") -> str:
    """Mark a daily habit as completed for today (e.g. 'reading', 'meditation', 'coding', 'walking')."""
    h_name = habit_name.strip().lower()
    if not h_name:
        return "Please provide a habit name."

    data = _load_habit_data()
    habits = data.setdefault("habits", {})
    entry = habits.setdefault(h_name, {"dates": [], "notes": []})

    today_str = datetime.now().strftime("%Y-%m-%d")
    if today_str not in entry["dates"]:
        entry["dates"].append(today_str)
    if notes:
        entry["notes"].append({"date": today_str, "note": notes.strip()})

    streak = _calculate_streak(entry["dates"])
    entry["streak"] = streak
    _save_habit_data(data)

    notes_msg = f" (Notes: '{notes}')" if notes else ""
    return f"Habit '{habit_name.title()}' marked as completed today! Current streak: {streak} day(s).{notes_msg}"


def log_water(amount_ml: int) -> str:
    """Log water intake in milliliters (e.g. 250, 500, 1000) for today."""
    try:
        ml = int(amount_ml)
        if ml <= 0:
            return "Water amount must be positive."

        data = _load_habit_data()
        water = data.setdefault("water", {})
        today_str = datetime.now().strftime("%Y-%m-%d")

        current_total = water.get(today_str, 0) + ml
        water[today_str] = current_total
        _save_habit_data(data)

        target = 2500
        pct = min(100, round((current_total / target) * 100))
        return (
            f"Logged {ml} ml of water. Total today: {current_total} ml "
            f"({current_total / 1000:.2f} L / {target / 1000} L target - {pct}%)."
        )
    except Exception as e:
        return f"Error logging water: {e}"


def log_workout(workout_type: str, duration_mins: int) -> str:
    """Log a physical workout or exercise session (e.g. 'running', 'gym', 'cycling', 'yoga') and duration in minutes."""
    try:
        dur = int(duration_mins)
        if dur <= 0:
            return "Workout duration must be positive."

        data = _load_habit_data()
        workouts = data.setdefault("workouts", [])
        now = datetime.now()

        item = {
            "type": workout_type.strip().title(),
            "duration": dur,
            "date": now.strftime("%Y-%m-%d"),
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        }
        workouts.append(item)
        _save_habit_data(data)

        # Log to habit streak as well
        log_habit(f"workout: {workout_type.strip().lower()}")
        return f"Logged {dur} mins of {item['type']} on {item['date']}. Keep up the great work!"
    except Exception as e:
        return f"Error logging workout: {e}"


def get_habit_status() -> str:
    """Get a comprehensive summary of today's health, water intake, workouts, and active habit streaks."""
    data = _load_habit_data()
    today_str = datetime.now().strftime("%Y-%m-%d")

    # Water
    water_today = data.get("water", {}).get(today_str, 0)

    # Workouts today
    workouts_today = [w for w in data.get("workouts", []) if w.get("date") == today_str]

    # Habits
    habits = data.get("habits", {})
    habit_lines = []
    for name, info in habits.items():
        done_today = "[x]" if today_str in info.get("dates", []) else "[ ]"
        streak = _calculate_streak(info.get("dates", []))
        habit_lines.append(f"  {done_today} {name.title()}: {streak} day streak")

    lines = [f"Daily Health & Habit Tracker ({today_str}):"]
    lines.append(f"• Water Intake: {water_today} ml ({water_today / 1000:.2f} L / 2.5 L target)")

    if workouts_today:
        w_summary = ", ".join(f"{w['type']} ({w['duration']}m)" for w in workouts_today)
        lines.append(f"• Workouts Today: {w_summary}")
    else:
        lines.append("• Workouts Today: None logged yet.")

    lines.append("• Active Habits:")
    if habit_lines:
        lines.extend(habit_lines)
    else:
        lines.append("  No habits registered yet.")

    return "\n".join(lines)
