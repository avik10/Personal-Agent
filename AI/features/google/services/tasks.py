"""Google Tasks API Tools for MCP."""

from typing import Any, Dict, List, Optional

from ..auth import get_service


def tasks_list_tasklists() -> List[Dict[str, Any]]:
    """List all Google Tasks task lists belonging to the user."""
    service = get_service("tasks", "v1")
    res = service.tasklists().list().execute()
    return [
        {
            "id": tl.get("id"),
            "title": tl.get("title"),
            "updated": tl.get("updated"),
        }
        for tl in res.get("items", [])
    ]


def tasks_list_tasks(
    tasklist_id: str = "@default",
    show_completed: bool = False,
    show_hidden: bool = False,
    due_max: Optional[str] = None,
    max_results: int = 50,
) -> List[Dict[str, Any]]:
    """List tasks inside a specified Google Tasks list.

    Args:
        tasklist_id: Task list ID (default is '@default').
        show_completed: If True, includes completed tasks.
        show_hidden: If True, includes hidden items.
        due_max: Optional upper bound for a task's due date (RFC 3339 timestamp).
        max_results: Maximum items to return (default 50, max 100).
    """
    service = get_service("tasks", "v1")
    params: Dict[str, Any] = {
        "tasklist": tasklist_id,
        "showCompleted": show_completed,
        "showHidden": show_hidden,
        "maxResults": max(1, min(max_results, 100)),
    }
    if due_max:
        params["dueMax"] = due_max

    res = service.tasks().list(**params).execute()
    items = res.get("items", [])

    return [
        {
            "id": t.get("id"),
            "title": t.get("title"),
            "status": t.get("status"),
            "notes": t.get("notes", ""),
            "due": t.get("due"),
            "completed": t.get("completed"),
            "updated": t.get("updated"),
        }
        for t in items
    ]


def tasks_create_task(
    title: str,
    notes: Optional[str] = None,
    due_date: Optional[str] = None,
    tasklist_id: str = "@default",
) -> Dict[str, Any]:
    """Create a new task item in Google Tasks.

    Args:
        title: Title/name of the task.
        notes: Optional details or notes for the task.
        due_date: Optional RFC 3339 due date (e.g., '2026-11-05T00:00:00Z').
        tasklist_id: Target task list ID (default '@default').
    """
    service = get_service("tasks", "v1")

    task_body: Dict[str, Any] = {"title": title}
    if notes:
        task_body["notes"] = notes
    if due_date:
        task_body["due"] = due_date

    created = (
        service.tasks()
        .insert(tasklist=tasklist_id, body=task_body)
        .execute()
    )

    return {
        "status": "created",
        "id": created.get("id"),
        "title": created.get("title"),
        "due": created.get("due"),
        "notes": created.get("notes"),
    }


def tasks_complete_task(
    task_id: str,
    tasklist_id: str = "@default",
) -> Dict[str, Any]:
    """Mark a task as completed in Google Tasks.

    Args:
        task_id: Task ID to complete.
        tasklist_id: Task list ID containing the task (default '@default').
    """
    service = get_service("tasks", "v1")
    task = service.tasks().get(tasklist=tasklist_id, task=task_id).execute()
    task["status"] = "completed"
    updated = (
        service.tasks()
        .update(tasklist=tasklist_id, task=task_id, body=task)
        .execute()
    )
    return {
        "status": "completed",
        "id": updated.get("id"),
        "title": updated.get("title"),
        "completed": updated.get("completed"),
    }


def tasks_delete_task(
    task_id: str,
    tasklist_id: str = "@default",
) -> Dict[str, Any]:
    """Delete a task from Google Tasks.

    Args:
        task_id: Task ID to delete.
        tasklist_id: Task list ID (default '@default').
    """
    service = get_service("tasks", "v1")
    service.tasks().delete(tasklist=tasklist_id, task=task_id).execute()
    return {"status": "deleted", "id": task_id, "tasklistId": tasklist_id}
