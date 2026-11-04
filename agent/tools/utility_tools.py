"""System Utility, Computations, and Data Storage Tools."""

import json
import math
import os
import platform
import re
import shutil
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.settings import (
    ACTIVITY_LOG_FILE,
    NOTES_FILE,
    STORAGE_DIR,
    TODO_FILE,
)


# ---------------------------------------------------------
# Time & Date Tools
# ---------------------------------------------------------

def get_current_time() -> str:
    """Get the current local date and time in human-readable format."""
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y - %H:%M:%S")


def days_until(target_date: str) -> str:
    """Calculate the number of days until or since a specific date (format: YYYY-MM-DD)."""
    try:
        target = datetime.strptime(target_date.strip(), "%Y-%m-%d").date()
        today = datetime.now().date()
        diff = (target - today).days

        if diff == 0:
            return f"{target_date} is today!"
        elif diff > 0:
            return f"There are {diff} day(s) until {target_date}."
        else:
            return f"{target_date} was {abs(diff)} day(s) ago."
    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD (e.g., 2026-12-25)."


# ---------------------------------------------------------
# Math & Unit Conversion Tools
# ---------------------------------------------------------

def calculate(expression: str) -> str:
    """Calculate a mathematical expression safely (supports standard math functions like sqrt, sin, cos, pow, etc.)."""
    try:
        allowed = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
        allowed.update({"abs": abs, "round": round, "min": min, "max": max})
        result = eval(expression, {"__builtins__": {}}, allowed)
        return str(result)
    except Exception as e:
        return f"Error calculating expression: {e}"


def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Convert common units of length, weight, and temperature.
    Supported length units: km, m, cm, mm, mile, ft, inch
    Supported weight units: kg, g, lb, oz
    Supported temp units: c, f, k
    """
    f = from_unit.lower().strip()
    t = to_unit.lower().strip()

    length_to_m = {
        "km": 1000.0,
        "m": 1.0,
        "cm": 0.01,
        "mm": 0.001,
        "mile": 1609.344,
        "miles": 1609.344,
        "ft": 0.3048,
        "feet": 0.3048,
        "inch": 0.0254,
        "inches": 0.0254,
    }
    if f in length_to_m and t in length_to_m:
        val_m = value * length_to_m[f]
        res = val_m / length_to_m[t]
        return f"{value} {from_unit} = {res:.4f} {to_unit}"

    weight_to_kg = {
        "kg": 1.0,
        "g": 0.001,
        "lb": 0.45359237,
        "lbs": 0.45359237,
        "oz": 0.0283495,
    }
    if f in weight_to_kg and t in weight_to_kg:
        val_kg = value * weight_to_kg[f]
        res = val_kg / weight_to_kg[t]
        return f"{value} {from_unit} = {res:.4f} {to_unit}"

    if f in ("c", "celsius") and t in ("f", "fahrenheit"):
        res = (value * 9 / 5) + 32
        return f"{value}°C = {res:.2f}°F"
    elif f in ("f", "fahrenheit") and t in ("c", "celsius"):
        res = (value - 32) * 5 / 9
        return f"{value}°F = {res:.2f}°C"
    elif f in ("c", "celsius") and t in ("k", "kelvin"):
        res = value + 273.15
        return f"{value}°C = {res:.2f}K"
    elif f in ("k", "kelvin") and t in ("c", "celsius"):
        res = value - 273.15
        return f"{value}K = {res:.2f}°C"

    return f"Conversion from '{from_unit}' to '{to_unit}' is not supported."


# ---------------------------------------------------------
# Activity Logging
# ---------------------------------------------------------

def log_activity(event_type: str, sender: str, details: str) -> None:
    """Log an activity or action with timestamp, category, and details to storage/activity.log."""
    try:
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sender_clean = sender.strip() if sender else "User"
        log_line = f"[{timestamp}] [{event_type}] [Source: {sender_clean}] {details.strip()}\n"
        with open(ACTIVITY_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception:
        pass


# ---------------------------------------------------------
# Notes Management Tools
# ---------------------------------------------------------

def save_note(note: str, sender: str = "") -> str:
    """Save a quick timestamped note to storage/notes.txt.
    
    IMPORTANT: `note` must contain ONLY the specific text or task to be noted down
    (e.g. 'Buy bread tomorrow', 'Doctor appointment at 4 PM').
    Do NOT include weather, calculations, or unrelated conversation in the note!
    """
    try:
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        clean_sender = sender.strip() if sender else ""
        if clean_sender.lower() in ("me", "self", "user", "unknown", "none"):
            clean_sender = ""
        sender_tag = f" [Participant: {clean_sender}]" if clean_sender else ""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}]{sender_tag} {note.strip()}\n"
        with open(NOTES_FILE, "a", encoding="utf-8") as f:
            f.write(line)
        log_activity("NOTE_SAVED", clean_sender, f"Note: {note}")
        return f"Note saved successfully{' [Participant: ' + clean_sender + ']' if clean_sender else ''}: '{note}'."
    except Exception as e:
        return f"Error saving note: {e}"


def read_notes() -> str:
    """Read all notes from storage/notes.txt."""
    try:
        if not NOTES_FILE.exists():
            return "No notes found."
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return content if content else "Notes file is empty."
    except Exception as e:
        return f"Error reading notes: {e}"


def update_note(note: str = "", new_note: str = "", search_keyword: str = "meeting", sender: str = "") -> str:
    """Update or modify an existing note in storage/notes.txt."""
    try:
        final_note = (note or new_note).strip()
        if not final_note:
            return "No updated note text provided."

        if not NOTES_FILE.exists():
            return "No notes found to update."
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        found = False
        new_lines = []
        clean_sender = sender.strip() if sender else ""
        sender_tag = f" [Sender: {clean_sender}]" if clean_sender else ""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        kw = (search_keyword or "meeting").lower().strip()
        for line in reversed(lines):
            if not found and kw in line.lower():
                new_lines.append(f"[{timestamp}]{sender_tag} {final_note}\n")
                found = True
            else:
                new_lines.append(line)
        new_lines.reverse()

        if not found:
            new_lines.append(f"[{timestamp}]{sender_tag} {final_note}\n")

        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        log_activity("NOTE_UPDATED", clean_sender, f"Updated Note (keyword '{kw}'): {final_note}")
        return f"Note updated successfully{' [Sender: ' + clean_sender + ']' if clean_sender else ''}: '{final_note}'."
    except Exception as e:
        return f"Error updating note: {e}"


# ---------------------------------------------------------
# To-Do List Management Tools
# ---------------------------------------------------------

def _load_todos() -> list[dict]:
    if not TODO_FILE.exists():
        return []
    try:
        with open(TODO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_todos(todos: list[dict]) -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2)


def add_todo(task: str, priority: str = "medium", sender: str = "") -> str:
    """Add a new task or reminder to the to-do list with a priority ('low', 'medium', 'high')."""
    todos = _load_todos()
    new_id = (max([t.get("id", 0) for t in todos], default=0)) + 1
    clean_sender = sender.strip() if sender else ""
    item = {
        "id": new_id,
        "task": task.strip(),
        "sender": clean_sender,
        "priority": priority.lower(),
        "completed": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    todos.append(item)
    _save_todos(todos)
    log_activity("TODO_ADDED", clean_sender, f"Task #{new_id}: '{task}' (Priority: {priority})")
    sender_str = f" [Contact: {clean_sender}]" if clean_sender else ""
    return f"Task #{new_id} added: '{task}'{sender_str} (Priority: {priority})"


def list_todos(show_completed: bool = False) -> str:
    """List to-do tasks. Set show_completed=True to include completed tasks."""
    todos = _load_todos()
    if not todos:
        return "Your to-do list is empty."

    filtered = todos if show_completed else [t for t in todos if not t.get("completed")]
    if not filtered:
        return "No pending tasks. Great job!"

    lines = ["Current To-Do List:"]
    for t in filtered:
        status = "[x]" if t.get("completed") else "[ ]"
        sender_info = f" [From: {t['sender']}]" if t.get("sender") else ""
        lines.append(f"  {status} #{t['id']}: {t['task']}{sender_info} (Priority: {t.get('priority', 'medium')})")
    return "\n".join(lines)


def complete_todo(task_id: int) -> str:
    """Mark a task as completed by its ID number."""
    todos = _load_todos()
    for t in todos:
        if t.get("id") == task_id:
            t["completed"] = True
            t["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _save_todos(todos)
            log_activity("TODO_COMPLETED", t.get("sender", ""), f"Task #{task_id}: '{t['task']}'")
            return f"Task #{task_id} ('{t['task']}') marked as completed."
    return f"Task #{task_id} not found."


def delete_todo(task_id: int) -> str:
    """Delete a task from the to-do list by its ID number."""
    todos = _load_todos()
    initial_len = len(todos)
    deleted_item = next((t for t in todos if t.get("id") == task_id), None)
    todos = [t for t in todos if t.get("id") != task_id]
    if len(todos) < initial_len:
        _save_todos(todos)
        sender = deleted_item.get("sender", "") if deleted_item else ""
        task_name = deleted_item.get("task", "") if deleted_item else ""
        log_activity("TODO_DELETED", sender, f"Task #{task_id}: '{task_name}'")
        return f"Task #{task_id} deleted."
    return f"Task #{task_id} not found."


def update_todo(
    task: str = "",
    new_task: str = "",
    search_keyword: str = "meeting",
    priority: str = "",
    sender: str = "",
    task_id: Optional[int] = None,
) -> str:
    """Update or reschedule an existing task in the to-do list by keyword or task_id."""
    todos = _load_todos()
    if not todos:
        return "No tasks found to update."

    target = None
    if task_id is not None:
        target = next((t for t in todos if t.get("id") == task_id), None)

    if not target and search_keyword:
        kw = (search_keyword or "meeting").lower().strip()
        for t in reversed(todos):
            if kw in t.get("task", "").lower() or kw in t.get("sender", "").lower():
                target = t
                break

    if not target and todos:
        target = todos[-1]

    final_task = (task or new_task).strip()
    if target:
        if final_task:
            target["task"] = final_task
        if priority:
            target["priority"] = priority.lower()
        if sender:
            target["sender"] = sender.strip()
        target["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        _save_todos(todos)
        log_activity("TODO_UPDATED", target.get("sender", ""), f"Task #{target['id']}: '{target['task']}'")
        return f"Task #{target['id']} updated: '{target['task']}' (Priority: {target.get('priority', 'medium')})"

    return "Task not found to update."


# ---------------------------------------------------------
# File System & Workspace Tools
# ---------------------------------------------------------

def list_files(directory: str = ".") -> str:
    """List files and subdirectories in the specified directory path."""
    try:
        path = Path(directory)
        if not path.exists():
            return f"Directory '{directory}' does not exist."
        if not path.is_dir():
            return f"Path '{directory}' is not a directory."

        entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        lines = [f"Contents of '{directory}':"]
        for p in entries[:50]:
            tag = "[DIR]" if p.is_dir() else f"[{p.stat().st_size} B]"
            lines.append(f"  {tag:<10} {p.name}")
        if len(entries) > 50:
            lines.append(f"  ... and {len(entries) - 50} more items.")
        return "\n".join(lines)
    except Exception as e:
        return f"Error listing directory: {e}"


def read_file_content(filepath: str, max_lines: int = 100) -> str:
    """Read the content of a text or code file (up to max_lines)."""
    try:
        path = Path(filepath)
        if not path.exists():
            return f"File '{filepath}' does not exist."
        if path.is_dir():
            return f"'{filepath}' is a directory, not a file."

        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = [f.readline() for _ in range(max_lines)]
        return "".join(lines)
    except Exception as e:
        return f"Error reading file: {e}"


# ---------------------------------------------------------
# System & Information Tools
# ---------------------------------------------------------

def get_system_status() -> str:
    """Get system overview including operating system, machine architecture, and disk space."""
    try:
        os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
        py_version = platform.python_version()

        disk = shutil.disk_usage(".")
        total_gb = disk.total / (1024 ** 3)
        free_gb = disk.free / (1024 ** 3)
        used_gb = disk.used / (1024 ** 3)

        return (
            f"OS: {os_info}\n"
            f"Python: {py_version}\n"
            f"Disk Total: {total_gb:.1f} GB | Used: {used_gb:.1f} GB | Free: {free_gb:.1f} GB"
        )
    except Exception as e:
        return f"Error retrieving system status: {e}"


def fetch_url_text(url: str = "", max_chars: int = 2000) -> str:
    """Fetch text content from a web URL and extract readable text."""
    if not url or not url.strip():
        return "No URL provided to fetch."
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (PersonalAgent/1.0)"}
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            content_type = response.headers.get("Content-Type", "")
            raw = response.read(100000).decode("utf-8", errors="replace")

        if "html" in content_type.lower() or "<html" in raw.lower():
            text = re.sub(r"<script.*?</script>", "", raw, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<style.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
        else:
            text = raw.strip()

        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        return text if text else "No readable text content found at URL."
    except Exception as e:
        return f"Error fetching URL: {e}"
