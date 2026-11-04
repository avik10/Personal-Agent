"""Google Keep & Notes API Tools for MCP."""

import logging
from typing import Any, Dict, List, Optional
from ..auth import get_service
from .tasks import tasks_list_tasks, tasks_create_task, tasks_delete_task

logger = logging.getLogger("mcp_google.keep")


def keep_list_notes(max_results: int = 50) -> List[Dict[str, Any]]:
    """Fetch notes from Google Keep, with seamless fallback to Google Tasks notes.

    Args:
        max_results: Maximum notes to return (default: 50).
    """
    notes: List[Dict[str, Any]] = []

    # 1. Attempt to fetch notes via Google Keep API
    try:
        service = get_service("keep", "v1")
        res = service.notes().list(pageSize=min(max_results, 100)).execute()
        raw_notes = res.get("notes", [])
        for n in raw_notes:
            name = n.get("name", "")
            note_id = name.split("/")[-1] if "/" in name else name
            body_text = ""
            body_obj = n.get("body", {})
            if "text" in body_obj:
                body_text = body_obj["text"].get("text", "")
            elif "list" in body_obj:
                list_items = body_obj["list"].get("listItems", [])
                body_text = "\n".join(
                    f"- {item.get('text', {}).get('text', '')}" for item in list_items
                )

            notes.append({
                "id": f"keep_{note_id}",
                "source": "google_keep",
                "title": n.get("title") or "Untitled Note",
                "notes": body_text,
                "status": "active",
                "updated": n.get("updateTime") or n.get("createTime"),
            })
    except Exception as e:
        logger.info("Google Keep API list notes notice: %s. Using Google Workspace Tasks fallback.", e)

    # 2. Also fetch Google Tasks (which store notes & task items)
    try:
        task_items = tasks_list_tasks(show_completed=True, max_results=max_results)
        for t in task_items:
            notes.append({
                "id": t.get("id"),
                "source": "google_tasks",
                "title": t.get("title"),
                "notes": t.get("notes", ""),
                "status": t.get("status", "needsAction"),
                "due": t.get("due"),
                "updated": t.get("updated"),
            })
    except Exception as e:
        logger.warning("Failed to fetch Google Tasks notes: %s", e)

    return notes


def keep_create_note(
    title: str,
    text: Optional[str] = None,
    due_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a note in Google Keep, falling back to Google Tasks notes.

    Args:
        title: Note title.
        text: Note description or content body.
        due_date: Optional due date.
    """
    # 1. Try Google Keep API
    try:
        service = get_service("keep", "v1")
        body_payload = {}
        if text:
            body_payload = {"text": {"text": text}}

        res = service.notes().create(body={
            "title": title,
            "body": body_payload,
        }).execute()

        name = res.get("name", "")
        note_id = name.split("/")[-1] if "/" in name else name
        return {
            "status": "created",
            "source": "google_keep",
            "id": f"keep_{note_id}",
            "title": res.get("title", title),
            "notes": text or "",
        }
    except Exception as e:
        logger.info("Google Keep API create notice: %s. Saving via Google Tasks notes.", e)

    # 2. Fallback to Google Tasks notes
    created = tasks_create_task(title=title, notes=text, due_date=due_date)
    created["source"] = "google_tasks"
    return created


def keep_delete_note(note_id: str) -> Dict[str, Any]:
    """Delete a note from Google Keep or Google Tasks.

    Args:
        note_id: Note ID.
    """
    if note_id.startswith("keep_"):
        raw_id = note_id.replace("keep_", "")
        try:
            service = get_service("keep", "v1")
            service.notes().delete(name=f"notes/{raw_id}").execute()
            return {"status": "deleted", "id": note_id, "source": "google_keep"}
        except Exception as e:
            logger.warning("Failed to delete from Keep: %s", e)

    # Fallback/default to tasks deletion
    return tasks_delete_task(task_id=note_id)
