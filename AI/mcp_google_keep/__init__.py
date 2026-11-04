"""Google Keep Model Context Protocol (MCP) Server package."""

from .server import server
from .auth import is_keep_authenticated, get_keep_client, GoogleKeepAuthError
from .services import (
    keep_list_notes,
    keep_get_note,
    keep_create_note,
    keep_create_checklist,
    keep_update_note,
    keep_delete_note,
    keep_search_notes,
)

__all__ = [
    "server",
    "is_keep_authenticated",
    "get_keep_client",
    "GoogleKeepAuthError",
    "keep_list_notes",
    "keep_get_note",
    "keep_create_note",
    "keep_create_checklist",
    "keep_update_note",
    "keep_delete_note",
    "keep_search_notes",
]
