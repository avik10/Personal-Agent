"""Task & Notes Specialist Agent with Google Workspace Cloud & Local Storage."""

import json
from typing import Optional
from langchain_core.tools import StructuredTool
from langgraph.prebuilt import create_react_agent

from agents.base import llm
from tools.utility_tools import (
    add_todo,
    complete_todo,
    delete_todo,
    list_todos,
    read_notes,
    save_note,
    update_note,
    update_todo,
)
from mcp_google.services.tasks import (
    tasks_create_task,
    tasks_list_tasks,
    tasks_complete_task,
    tasks_delete_task,
)
from mcp_google.services.keep import (
    keep_create_note,
    keep_list_notes,
    keep_delete_note,
)


def agent_google_list_notes_or_tasks(max_results: int = 50) -> str:
    """List all notes and tasks from Google Workspace cloud storage."""
    try:
        items = keep_list_notes(max_results=max_results)
        if not items:
            return "No notes or tasks found in connected Google Workspace account."

        lines = []
        for idx, item in enumerate(items, 1):
            title = item.get("title") or "Untitled Note"
            notes = (item.get("notes") or "").strip()
            source = item.get("source", "google_tasks")
            source_label = "Google Tasks (Gmail/Calendar sidebar)" if source == "google_tasks" else "Google Keep"
            status = "Completed" if item.get("status") == "completed" else "Active"
            due = f" [Due: {item.get('due')}]" if item.get("due") else ""
            desc = f" - Details: {notes}" if notes else ""
            lines.append(f"{idx}. [{status}] [{source_label}] {title}{due}{desc}")

        return "\n".join(lines)
    except Exception as e:
        return f"Could not retrieve Google notes: {e}"


def agent_google_create_note(title: str, notes: Optional[str] = None, due_date: Optional[str] = None) -> str:
    """Create a note or task in Google cloud storage."""
    try:
        clean_title = (title or "").strip()
        if not clean_title:
            return "Error: Note title cannot be empty."

        res = keep_create_note(title=clean_title, text=notes, due_date=due_date)
        source = res.get("source", "google_tasks")
        if source == "google_tasks":
            return (
                f"Successfully saved note to your Google account via Google Tasks: '{clean_title}'. "
                f"It is live in your Google account and viewable in the Gmail right-sidebar (Tasks icon), "
                f"Google Calendar (calendar.google.com), and the Notes & Tasks studio tab."
            )
        else:
            return f"Successfully saved note to Google Keep: '{clean_title}'. Viewable at https://keep.google.com."
    except Exception as e:
        return f"Could not save note to Google: {e}"


def agent_google_complete_task(task_id: str) -> str:
    """Mark a task as completed in Google Tasks."""
    try:
        res = tasks_complete_task(task_id=task_id)
        return f"Task '{res.get('title', task_id)}' marked as completed."
    except Exception as e:
        return f"Could not complete task in Google: {e}"


def agent_google_delete_note(note_id: str) -> str:
    """Delete a note or task in Google Tasks / Keep."""
    try:
        res = keep_delete_note(note_id=note_id)
        return f"Item '{note_id}' successfully deleted from Google."
    except Exception as e:
        return f"Could not delete note in Google: {e}"


task_notes_tools = [
    # Google Workspace Cloud Notes & Tasks (String outputs safe for Groq & OpenAI)
    StructuredTool.from_function(
        agent_google_create_note,
        name="google_create_note_or_task",
        description="Create a note or task in Google Keep/Tasks cloud storage. Saves title, optional notes body, and optional due date.",
    ),
    StructuredTool.from_function(
        agent_google_list_notes_or_tasks,
        name="google_list_notes_or_tasks",
        description="List all notes and tasks from Google Keep and Google Tasks cloud. Shows active and completed items.",
    ),
    StructuredTool.from_function(
        agent_google_complete_task,
        name="google_complete_task",
        description="Mark a task as completed in Google Tasks.",
    ),
    StructuredTool.from_function(
        agent_google_delete_note,
        name="google_delete_note_or_task",
        description="Delete a note or task from Google Keep or Google Tasks.",
    ),
    # Local Storage fallback
    StructuredTool.from_function(
        save_note,
        name="local_save_note",
        description="Save a note to local disk storage.",
    ),
    StructuredTool.from_function(
        read_notes,
        name="local_read_notes",
        description="Read notes from local disk storage.",
    ),
    StructuredTool.from_function(
        update_note,
        name="local_update_note",
        description="Update a note in local disk storage.",
    ),
    StructuredTool.from_function(
        add_todo,
        name="local_add_todo",
        description="Add a todo item to local disk storage.",
    ),
    StructuredTool.from_function(
        list_todos,
        name="local_list_todos",
        description="List todo items from local disk storage.",
    ),
    StructuredTool.from_function(
        complete_todo,
        name="local_complete_todo",
        description="Mark a todo item as completed in local storage.",
    ),
    StructuredTool.from_function(
        delete_todo,
        name="local_delete_todo",
        description="Delete a todo item from local storage.",
    ),
]

TASK_NOTES_PROMPT = (
    "You are the Task & Notes Specialist Agent.\n"
    "You support both Google Workspace Cloud Notes (Google Keep / Tasks) and local storage.\n\n"
    "ROUTING & PREFERENCE RULES:\n"
    "1. When the user asks to view, show, list, save, or complete notes or tasks:\n"
    "   - First try `google_list_notes_or_tasks` or `google_create_note_or_task`.\n"
    "   - If no notes are found in Google Workspace or if Google is not connected, also check `local_read_notes` or `local_list_todos`.\n"
    "   - If the user explicitly asks for 'local' or 'disk', use the local storage tools.\n\n"
    "CRITICAL FORMATTING & EXTRACTION:\n"
    "1. When showing notes, format them clearly with bullet points, titles, and dates.\n"
    "2. When saving a note, extract ONLY the specific item the user asked to record.\n"
    "3. Never dump raw system/error messages. Always provide a clear, polite final response in plain English."
)

task_notes_agent = create_react_agent(llm, task_notes_tools, prompt=TASK_NOTES_PROMPT)
