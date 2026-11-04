"""Google Keep Core Service Operations for MCP."""

import logging
from typing import Any, Dict, List, Optional
from .auth import get_keep_client

logger = logging.getLogger("mcp.google_keep.services")


def _format_note(note) -> Dict[str, Any]:
    """Extract standard JSON dictionary representation of a gkeepapi Note."""
    # Check if note is a list/checklist
    items = []
    if hasattr(note, "items") and note.items:
        for it in note.items:
            items.append({
                "text": getattr(it, "text", ""),
                "checked": getattr(it, "checked", False),
            })

    labels = []
    if hasattr(note, "labels"):
        for l in note.labels.all():
            labels.append(l.name)

    return {
        "id": note.id,
        "title": note.title or "Untitled Note",
        "text": note.text or "",
        "pinned": bool(note.pinned),
        "archived": bool(note.archived),
        "trashed": bool(note.trashed),
        "color": str(getattr(note, "color", "DEFAULT")),
        "is_checklist": bool(items),
        "items": items,
        "labels": labels,
        "url": f"https://keep.google.com/#NOTE/{note.id}",
    }


def keep_list_notes(
    query: str = "",
    pinned_only: bool = False,
    archived: bool = False,
    trashed: bool = False,
    max_results: int = 50,
) -> List[Dict[str, Any]]:
    """List notes from Google Keep.

    Args:
        query: Optional search keyword in title or content.
        pinned_only: If True, only returns pinned notes.
        archived: If True, includes archived notes.
        trashed: If True, includes trashed notes.
        max_results: Maximum notes to return (default: 50).
    """
    keep = get_keep_client()
    try:
        keep.sync()
    except Exception as e:
        logger.warning("Keep sync notice: %s", e)

    results = []
    clean_query = query.lower().strip() if query else ""

    for note in keep.all():
        if not trashed and note.trashed:
            continue
        if trashed and not note.trashed:
            continue
        if not archived and note.archived:
            continue
        if pinned_only and not note.pinned:
            continue

        if clean_query:
            title_match = clean_query in (note.title or "").lower()
            text_match = clean_query in (note.text or "").lower()
            if not (title_match or text_match):
                continue

        results.append(_format_note(note))
        if len(results) >= max_results:
            break

    return results


def keep_get_note(note_id: str) -> Dict[str, Any]:
    """Retrieve full details of a specific note by ID."""
    keep = get_keep_client()
    note = keep.get(note_id)
    if not note:
        raise ValueError(f"Note with ID '{note_id}' not found in Google Keep.")
    return _format_note(note)


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
        text: Note body text.
        pinned: Whether to pin note to top.
        color: Keep color name (e.g. 'RED', 'BLUE', 'YELLOW', 'GREEN', 'PURPLE', 'DEFAULT').
        labels: Optional list of label names to attach.
    """
    keep = get_keep_client()
    note = keep.createNote(title.strip(), text.strip())
    note.pinned = pinned

    # Set color if valid
    try:
        import gkeepapi
        color_enum = getattr(gkeepapi.node.ColorValue, color.upper(), None)
        if color_enum:
            note.color = color_enum
    except Exception:
        pass

    # Attach labels
    if labels:
        for lbl_name in labels:
            lbl = keep.findLabel(lbl_name.strip())
            if not lbl:
                lbl = keep.createLabel(lbl_name.strip())
            note.labels.add(lbl)

    keep.sync()
    return _format_note(note)


def keep_create_checklist(
    title: str,
    items: Optional[List[str]] = None,
    pinned: bool = False,
) -> Dict[str, Any]:
    """Create a checklist/to-do note in Google Keep.

    Args:
        title: Title of the checklist.
        items: List of item strings.
        pinned: Whether to pin note to top.
    """
    keep = get_keep_client()
    raw_items = [(item, False) for item in (items or [])]
    note = keep.createList(title.strip(), raw_items)
    note.pinned = pinned
    keep.sync()
    return _format_note(note)


def keep_update_note(
    note_id: str,
    title: Optional[str] = None,
    text: Optional[str] = None,
    pinned: Optional[bool] = None,
    archived: Optional[bool] = None,
) -> Dict[str, Any]:
    """Update an existing note in Google Keep."""
    keep = get_keep_client()
    note = keep.get(note_id)
    if not note:
        raise ValueError(f"Note '{note_id}' not found.")

    if title is not None:
        note.title = title.strip()
    if text is not None:
        note.text = text.strip()
    if pinned is not None:
        note.pinned = pinned
    if archived is not None:
        note.archived = archived

    keep.sync()
    return _format_note(note)


def keep_delete_note(note_id: str, permanent: bool = False) -> Dict[str, Any]:
    """Delete a note from Google Keep (moves to trash by default)."""
    keep = get_keep_client()
    note = keep.get(note_id)
    if not note:
        raise ValueError(f"Note '{note_id}' not found.")

    if permanent:
        note.delete()
    else:
        note.trash()

    keep.sync()
    return {"status": "deleted", "id": note_id, "permanent": permanent}


def keep_search_notes(query: str, max_results: int = 25) -> List[Dict[str, Any]]:
    """Search Google Keep notes by query string."""
    return keep_list_notes(query=query, max_results=max_results)
