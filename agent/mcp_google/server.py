"""Main entrypoint for Google Workspace Model Context Protocol (MCP) Server."""

import functools
import json
import sys
from typing import Any, Callable, Dict, List, Optional

from googleapiclient.errors import HttpError
from mcp.server.mcpserver import MCPServer

from .auth import GoogleAuthError, get_account_info, is_authenticated
from .services import calendar as cal_svc
from .services import docs as docs_svc
from .services import drive as drive_svc
from .services import gmail as gmail_svc
from .services import tasks as tasks_svc

# Create MCP Server instance
server = MCPServer(
    name="google-workspace-mcp",
    instructions=(
        "Google Workspace MCP Server. Provides comprehensive tools to interact with "
        "Gmail, Google Calendar, Google Drive, Google Docs, and Google Tasks on behalf of the user."
    ),
    version="1.0.0",
)


def safe_tool(fn: Callable) -> Callable:
    """Decorator to catch Google API errors or missing authentication and return informative feedback."""

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return fn(*args, **kwargs)
        except GoogleAuthError as e:
            return {
                "error": "AuthenticationError",
                "message": str(e),
                "resolution": (
                    "Please run `python3 -m mcp_google.setup_auth` in your terminal to authenticate "
                    "with your Google account and grant the requested permissions."
                ),
            }
        except HttpError as e:
            error_details = str(e)
            try:
                error_content = json.loads(e.content.decode("utf-8"))
                error_details = error_content.get("error", {}).get("message", str(e))
            except Exception:
                pass
            return {
                "error": "GoogleApiHttpError",
                "status_code": e.status_code,
                "message": error_details,
            }
        except Exception as e:
            return {"error": type(e).__name__, "message": str(e)}

    return wrapper


# ==============================================================================
# Gmail Tools
# ==============================================================================


@server.tool()
@safe_tool
def gmail_search_messages(query: str = "", max_results: int = 10) -> List[Dict[str, Any]]:
    """Search emails in Gmail using standard query syntax (e.g., 'is:unread', 'from:someone@domain.com', 'subject:report')."""
    return gmail_svc.gmail_search_messages(query=query, max_results=max_results)


@server.tool()
@safe_tool
def gmail_get_message(message_id: str) -> Dict[str, Any]:
    """Retrieve full email details including headers, snippet, and plain text content by message ID."""
    return gmail_svc.gmail_get_message(message_id=message_id)


@server.tool()
@safe_tool
def gmail_send_message(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
) -> Dict[str, Any]:
    """Send an email from the user's Gmail account."""
    return gmail_svc.gmail_send_message(to=to, subject=subject, body=body, cc=cc, bcc=bcc)


@server.tool()
@safe_tool
def gmail_create_draft(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a draft email in the user's Gmail account without sending it."""
    return gmail_svc.gmail_create_draft(to=to, subject=subject, body=body, cc=cc)


@server.tool()
@safe_tool
def gmail_list_labels() -> List[Dict[str, Any]]:
    """List all Gmail folders and user labels (INBOX, SENT, TRASH, custom labels)."""
    return gmail_svc.gmail_list_labels()


@server.tool()
@safe_tool
def gmail_modify_labels(
    message_id: str,
    add_labels: Optional[List[str]] = None,
    remove_labels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Modify labels on an email message (e.g. mark read with remove_labels=['UNREAD'], star with add_labels=['STARRED'])."""
    return gmail_svc.gmail_modify_labels(
        message_id=message_id, add_labels=add_labels, remove_labels=remove_labels
    )


# ==============================================================================
# Google Calendar Tools
# ==============================================================================


@server.tool()
@safe_tool
def calendar_list_calendars() -> List[Dict[str, Any]]:
    """List all Google Calendars accessible by the user."""
    return cal_svc.calendar_list_calendars()


@server.tool()
@safe_tool
def calendar_list_events(
    calendar_id: str = "primary",
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
    query: Optional[str] = None,
    max_results: int = 20,
) -> List[Dict[str, Any]]:
    """List events from a calendar filtered by start/end time and optional search term."""
    return cal_svc.calendar_list_events(
        calendar_id=calendar_id,
        time_min=time_min,
        time_max=time_max,
        query=query,
        max_results=max_results,
    )


@server.tool()
@safe_tool
def calendar_get_agenda(
    days_ahead: int = 7, calendar_id: str = "primary"
) -> List[Dict[str, Any]]:
    """Get scheduled events and meetings for the upcoming N days (default 7 days)."""
    return cal_svc.calendar_get_agenda(days_ahead=days_ahead, calendar_id=calendar_id)


@server.tool()
@safe_tool
def calendar_create_event(
    summary: str,
    start_time: str,
    end_time: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    add_meet_link: bool = False,
    calendar_id: str = "primary",
) -> Dict[str, Any]:
    """Create a new event on Google Calendar with optional Google Meet link and attendees."""
    return cal_svc.calendar_create_event(
        summary=summary,
        start_time=start_time,
        end_time=end_time,
        description=description,
        location=location,
        attendees=attendees,
        add_meet_link=add_meet_link,
        calendar_id=calendar_id,
    )


@server.tool()
@safe_tool
def calendar_update_event(
    event_id: str,
    summary: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    calendar_id: str = "primary",
) -> Dict[str, Any]:
    """Update details of an existing Google Calendar event."""
    return cal_svc.calendar_update_event(
        event_id=event_id,
        summary=summary,
        start_time=start_time,
        end_time=end_time,
        description=description,
        location=location,
        calendar_id=calendar_id,
    )


@server.tool()
@safe_tool
def calendar_delete_event(
    event_id: str, calendar_id: str = "primary"
) -> Dict[str, Any]:
    """Delete an event from Google Calendar."""
    return cal_svc.calendar_delete_event(event_id=event_id, calendar_id=calendar_id)


# ==============================================================================
# Google Drive Tools
# ==============================================================================


@server.tool()
@safe_tool
def drive_search_files(
    query: str = "",
    folder_id: Optional[str] = None,
    page_size: int = 15,
) -> List[Dict[str, Any]]:
    """Search files and folders in Google Drive by name, query or parent folder."""
    return drive_svc.drive_search_files(
        query=query, folder_id=folder_id, page_size=page_size
    )


@server.tool()
@safe_tool
def drive_get_file_metadata(file_id: str) -> Dict[str, Any]:
    """Retrieve metadata, sharing status, and links for a Google Drive file."""
    return drive_svc.drive_get_file_metadata(file_id=file_id)


@server.tool()
@safe_tool
def drive_read_file(file_id: str) -> Dict[str, Any]:
    """Read the content of a Google Drive file (auto-exports Google Docs to text and Sheets to CSV)."""
    return drive_svc.drive_read_file(file_id=file_id)


@server.tool()
@safe_tool
def drive_upload_file(
    name: str,
    content: str,
    folder_id: Optional[str] = None,
    mime_type: str = "text/plain",
) -> Dict[str, Any]:
    """Upload or create a new text, markdown, or code file in Google Drive."""
    return drive_svc.drive_upload_file(
        name=name, content=content, folder_id=folder_id, mime_type=mime_type
    )


@server.tool()
@safe_tool
def drive_create_folder(
    name: str, parent_folder_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new folder in Google Drive."""
    return drive_svc.drive_create_folder(name=name, parent_folder_id=parent_folder_id)


@server.tool()
@safe_tool
def drive_delete_file(file_id: str, permanent: bool = False) -> Dict[str, Any]:
    """Move a file to trash or permanently delete it from Google Drive."""
    return drive_svc.drive_delete_file(file_id=file_id, permanent=permanent)


# ==============================================================================
# Google Docs Tools
# ==============================================================================


@server.tool()
@safe_tool
def docs_get_document(document_id: str) -> Dict[str, Any]:
    """Extract and read the full text content and structure of a Google Document."""
    return docs_svc.docs_get_document(document_id=document_id)


@server.tool()
@safe_tool
def docs_create_document(
    title: str, initial_content: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new Google Document with an optional initial body text."""
    return docs_svc.docs_create_document(title=title, initial_content=initial_content)


@server.tool()
@safe_tool
def docs_append_text(document_id: str, text: str) -> Dict[str, Any]:
    """Append text to the end of an existing Google Document."""
    return docs_svc.docs_append_text(document_id=document_id, text=text)


# ==============================================================================
# Google Tasks Tools
# ==============================================================================


@server.tool()
@safe_tool
def tasks_list_tasklists() -> List[Dict[str, Any]]:
    """List all Google Tasks task lists."""
    return tasks_svc.tasks_list_tasklists()


@server.tool()
@safe_tool
def tasks_list_tasks(
    tasklist_id: str = "@default",
    show_completed: bool = False,
    show_hidden: bool = False,
    due_max: Optional[str] = None,
    max_results: int = 50,
) -> List[Dict[str, Any]]:
    """List tasks inside a Google Tasks list."""
    return tasks_svc.tasks_list_tasks(
        tasklist_id=tasklist_id,
        show_completed=show_completed,
        show_hidden=show_hidden,
        due_max=due_max,
        max_results=max_results,
    )


@server.tool()
@safe_tool
def tasks_create_task(
    title: str,
    notes: Optional[str] = None,
    due_date: Optional[str] = None,
    tasklist_id: str = "@default",
) -> Dict[str, Any]:
    """Create a new task item in Google Tasks."""
    return tasks_svc.tasks_create_task(
        title=title, notes=notes, due_date=due_date, tasklist_id=tasklist_id
    )


@server.tool()
@safe_tool
def tasks_complete_task(
    task_id: str,
    tasklist_id: str = "@default",
) -> Dict[str, Any]:
    """Mark a task as completed in Google Tasks."""
    return tasks_svc.tasks_complete_task(task_id=task_id, tasklist_id=tasklist_id)


@server.tool()
@safe_tool
def tasks_delete_task(
    task_id: str,
    tasklist_id: str = "@default",
) -> Dict[str, Any]:
    """Delete a task from Google Tasks."""
    return tasks_svc.tasks_delete_task(task_id=task_id, tasklist_id=tasklist_id)


# ==============================================================================
# Resources & Prompts
# ==============================================================================


@server.resource("google://account/info")
def resource_account_info() -> str:
    """Resource returning the current Google account authorization status and email."""
    if not is_authenticated():
        return json.dumps(
            {
                "authenticated": False,
                "message": "Not authenticated. Run `python3 -m mcp_google.setup_auth` to sign in.",
            },
            indent=2,
        )
    info = get_account_info()
    return json.dumps(info, indent=2)


def main() -> None:
    """Run the Google Workspace MCP server over stdio transport."""
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
