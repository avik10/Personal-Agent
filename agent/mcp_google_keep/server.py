"""Google Keep Model Context Protocol (MCP) Server."""

import functools
import json
import logging
from typing import Any, Callable, Dict, List, Optional
from mcp.server.mcpserver import MCPServer

from .auth import GoogleKeepAuthError, is_keep_authenticated
from . import services as svc

logger = logging.getLogger("mcp.google_keep.server")

# Initialize MCP Server instance
server = MCPServer(
    name="google-keep-mcp",
    instructions=(
        "Google Keep MCP Server. Provides comprehensive tools to interact with "
        "real Google Keep notes, checklists, labels, and pinned items on behalf of the user."
    ),
    version="1.0.0",
)


def safe_tool(fn: Callable) -> Callable:
    """Decorator to catch Google Keep errors or missing credentials."""

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return fn(*args, **kwargs)
        except GoogleKeepAuthError as e:
            return {
                "error": "GoogleKeepAuthenticationError",
                "message": str(e),
                "resolution": (
                    "Please generate a 16-character Google App Password at https://myaccount.google.com/apppasswords "
                    "and set GOOGLE_KEEP_APP_PASSWORD in your environment."
                ),
            }
        except Exception as e:
            return {"error": type(e).__name__, "message": str(e)}

    return wrapper


@server.tool()
@safe_tool
def keep_list_notes(
    query: str = "",
    pinned_only: bool = False,
    archived: bool = False,
    max_results: int = 50,
) -> List[Dict[str, Any]]:
    """List notes from user's real Google Keep account.

    Args:
        query: Optional search keyword to filter by title or note content.
        pinned_only: If True, only returns pinned notes.
        archived: If True, includes archived notes.
        max_results: Maximum number of notes to return (default: 50).
    """
    return svc.keep_list_notes(
        query=query, pinned_only=pinned_only, archived=archived, max_results=max_results
    )


@server.tool()
@safe_tool
def keep_get_note(note_id: str) -> Dict[str, Any]:
    """Retrieve full details of a Google Keep note by ID."""
    return svc.keep_get_note(note_id=note_id)


@server.tool()
@safe_tool
def keep_create_note(
    title: str,
    text: str = "",
    pinned: bool = False,
    color: str = "DEFAULT",
    labels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Create a new text note in Google Keep.

    Args:
        title: Title of the note.
        text: Note text content.
        pinned: Whether to pin the note.
        color: Optional color ('DEFAULT', 'RED', 'BLUE', 'YELLOW', 'GREEN', 'PURPLE').
        labels: Optional list of label strings to attach.
    """
    return svc.keep_create_note(
        title=title, text=text, pinned=pinned, color=color, labels=labels
    )


@server.tool()
@safe_tool
def keep_create_checklist(
    title: str,
    items: Optional[List[str]] = None,
    pinned: bool = False,
) -> Dict[str, Any]:
    """Create a new checklist / to-do list note in Google Keep.

    Args:
        title: Title of the checklist.
        items: List of item strings (e.g., ['Milk', 'Eggs', 'Bread']).
        pinned: Whether to pin the checklist to the top.
    """
    return svc.keep_create_checklist(title=title, items=items, pinned=pinned)


@server.tool()
@safe_tool
def keep_update_note(
    note_id: str,
    title: Optional[str] = None,
    text: Optional[str] = None,
    pinned: Optional[bool] = None,
    archived: Optional[bool] = None,
) -> Dict[str, Any]:
    """Update title, content, pin, or archive status of an existing Google Keep note."""
    return svc.keep_update_note(
        note_id=note_id, title=title, text=text, pinned=pinned, archived=archived
    )


@server.tool()
@safe_tool
def keep_delete_note(note_id: str, permanent: bool = False) -> Dict[str, Any]:
    """Delete a Google Keep note (trashes it by default)."""
    return svc.keep_delete_note(note_id=note_id, permanent=permanent)


@server.tool()
@safe_tool
def keep_search_notes(query: str, max_results: int = 25) -> List[Dict[str, Any]]:
    """Search Google Keep notes by keyword."""
    return svc.keep_search_notes(query=query, max_results=max_results)
