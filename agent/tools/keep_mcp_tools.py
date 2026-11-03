"""Google Keep MCP Tools adapter for LangChain / LangGraph Multi-Agent System."""

import json
from typing import Any, List, Optional
from langchain_core.tools import StructuredTool

from mcp_google_keep import services as svc
from mcp_google_keep.auth import is_keep_authenticated


def _format_output(data: Any) -> str:
    """Format Python dictionaries/lists as clean string for LLMs to avoid Groq 400 errors."""
    if isinstance(data, list):
        if not data:
            return "No notes found in Google Keep."
        lines = []
        for idx, item in enumerate(data, 1):
            title = item.get("title") or "Untitled Note"
            text = (item.get("text") or "").strip()
            pinned = " [Pinned]" if item.get("pinned") else ""
            desc = f"\n   Content: {text}" if text else ""
            lines.append(f"{idx}. {title}{pinned}{desc}")
        return "\n".join(lines)
    elif isinstance(data, dict):
        if "error" in data:
            return f"Notice: {data.get('message', data.get('error'))}"
        return json.dumps(data, indent=2)
    return str(data)


def mcp_keep_list_notes(query: str = "", pinned_only: bool = False, max_results: int = 25) -> str:
    """List notes from user's real Google Keep account."""
    try:
        data = svc.keep_list_notes(query=query, pinned_only=pinned_only, max_results=max_results)
        return _format_output(data)
    except Exception as e:
        return f"Google Keep Notice: {e}"


def mcp_keep_create_note(title: str, text: str = "", pinned: bool = False, color: str = "DEFAULT") -> str:
    """Create a new note in Google Keep."""
    try:
        note = svc.keep_create_note(title=title, text=text, pinned=pinned, color=color)
        return f"Successfully created Google Keep note: '{note.get('title')}'."
    except Exception as e:
        return f"Could not create Google Keep note: {e}"


def mcp_keep_create_checklist(title: str, items: Optional[List[str]] = None, pinned: bool = False) -> str:
    """Create a checklist/to-do list note in Google Keep."""
    try:
        note = svc.keep_create_checklist(title=title, items=items or [], pinned=pinned)
        return f"Successfully created Google Keep checklist: '{note.get('title')}' with {len(items or [])} items."
    except Exception as e:
        return f"Could not create Google Keep checklist: {e}"


def mcp_keep_delete_note(note_id: str) -> str:
    """Delete a note in Google Keep."""
    try:
        svc.keep_delete_note(note_id=note_id)
        return f"Note '{note_id}' successfully moved to trash in Google Keep."
    except Exception as e:
        return f"Could not delete Google Keep note: {e}"


google_keep_mcp_tools = [
    StructuredTool.from_function(
        mcp_keep_list_notes,
        name="google_keep_list_notes",
        description="List real notes from Google Keep. Can filter by search query or pinned status.",
    ),
    StructuredTool.from_function(
        mcp_keep_create_note,
        name="google_keep_create_note",
        description="Create a real text note in Google Keep with title and text.",
    ),
    StructuredTool.from_function(
        mcp_keep_create_checklist,
        name="google_keep_create_checklist",
        description="Create a to-do list / checklist note in Google Keep with list items.",
    ),
    StructuredTool.from_function(
        mcp_keep_delete_note,
        name="google_keep_delete_note",
        description="Delete a note from Google Keep by note ID.",
    ),
]
