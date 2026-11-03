"""Google Workspace MCP Tools adapter for LangChain / LangGraph Agent."""

import json
from typing import Any, List, Optional
from langchain_core.tools import StructuredTool

from mcp_google.server import (
    calendar_create_event,
    calendar_delete_event,
    calendar_get_agenda,
    calendar_list_calendars,
    calendar_list_events,
    calendar_update_event,
    docs_append_text,
    docs_create_document,
    docs_get_document,
    drive_create_folder,
    drive_delete_file,
    drive_get_file_metadata,
    drive_read_file,
    drive_search_files,
    drive_upload_file,
    gmail_create_draft,
    gmail_get_message,
    gmail_list_labels,
    gmail_modify_labels,
    gmail_search_messages,
    gmail_send_message,
    resource_account_info,
    tasks_complete_task,
    tasks_create_task,
    tasks_delete_task,
    tasks_list_tasklists,
    tasks_list_tasks,
)


def _format_output(data: Any) -> str:
    """Format Python dictionaries/lists as formatted JSON string for LLMs."""
    if isinstance(data, (dict, list)):
        return json.dumps(data, indent=2)
    return str(data)


# ------------------------------------------------------------------------------
# Gmail Tool Callers
# ------------------------------------------------------------------------------

def mcp_gmail_search(query: str = "", max_results: int = 10) -> str:
    """Search messages in Gmail using query syntax (e.g. 'is:unread', 'from:alice', 'subject:report')."""
    return _format_output(gmail_search_messages(query=query, max_results=max_results))


def mcp_gmail_get_message(message_id: str) -> str:
    """Retrieve full email content and headers by message ID."""
    return _format_output(gmail_get_message(message_id=message_id))


def mcp_gmail_send_message(
    to: str, subject: str, body: str, cc: Optional[str] = None, bcc: Optional[str] = None
) -> str:
    """Send an email from the user's Gmail account."""
    return _format_output(gmail_send_message(to=to, subject=subject, body=body, cc=cc, bcc=bcc))


def mcp_gmail_create_draft(to: str, subject: str, body: str, cc: Optional[str] = None) -> str:
    """Create a draft email in Gmail without sending it."""
    return _format_output(gmail_create_draft(to=to, subject=subject, body=body, cc=cc))


def mcp_gmail_list_labels() -> str:
    """List all Gmail folders and labels (INBOX, SENT, TRASH, etc.)."""
    return _format_output(gmail_list_labels())


def mcp_gmail_modify_labels(
    message_id: str,
    add_labels: Optional[List[str]] = None,
    remove_labels: Optional[List[str]] = None,
) -> str:
    """Modify labels on an email (e.g. remove 'UNREAD' to mark as read, add 'STARRED' to star)."""
    return _format_output(
        gmail_modify_labels(
            message_id=message_id, add_labels=add_labels, remove_labels=remove_labels
        )
    )


# ------------------------------------------------------------------------------
# Calendar Tool Callers
# ------------------------------------------------------------------------------

def mcp_calendar_get_agenda(days_ahead: int = 7) -> str:
    """Get scheduled events and meetings from Google Calendar for the upcoming N days."""
    return _format_output(calendar_get_agenda(days_ahead=days_ahead))


def mcp_calendar_list_events(
    calendar_id: str = "primary",
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
    query: Optional[str] = None,
    max_results: int = 20,
) -> str:
    """List events from Google Calendar with optional date bounds and search term."""
    return _format_output(
        calendar_list_events(
            calendar_id=calendar_id,
            time_min=time_min,
            time_max=time_max,
            query=query,
            max_results=max_results,
        )
    )


def mcp_calendar_create_event(
    summary: str,
    start_time: str,
    end_time: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    add_meet_link: bool = False,
    calendar_id: str = "primary",
) -> str:
    """Create a new event on Google Calendar with optional Google Meet link."""
    return _format_output(
        calendar_create_event(
            summary=summary,
            start_time=start_time,
            end_time=end_time,
            description=description,
            location=location,
            attendees=attendees,
            add_meet_link=add_meet_link,
            calendar_id=calendar_id,
        )
    )


def mcp_calendar_update_event(
    event_id: str,
    summary: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    calendar_id: str = "primary",
) -> str:
    """Update details of an existing Google Calendar event."""
    return _format_output(
        calendar_update_event(
            event_id=event_id,
            summary=summary,
            start_time=start_time,
            end_time=end_time,
            description=description,
            location=location,
            calendar_id=calendar_id,
        )
    )


def mcp_calendar_delete_event(event_id: str, calendar_id: str = "primary") -> str:
    """Delete an event from Google Calendar."""
    return _format_output(calendar_delete_event(event_id=event_id, calendar_id=calendar_id))


# ------------------------------------------------------------------------------
# Drive Tool Callers
# ------------------------------------------------------------------------------

def mcp_drive_search_files(
    query: str = "", folder_id: Optional[str] = None, page_size: int = 15
) -> str:
    """Search files and folders in Google Drive."""
    return _format_output(
        drive_search_files(query=query, folder_id=folder_id, page_size=page_size)
    )


def mcp_drive_get_file_metadata(file_id: str) -> str:
    """Get metadata, size, owners, and web links for a Google Drive file."""
    return _format_output(drive_get_file_metadata(file_id=file_id))


def mcp_drive_read_file(file_id: str) -> str:
    """Read content of a Google Drive file (auto-exports Google Docs to text and Sheets to CSV)."""
    return _format_output(drive_read_file(file_id=file_id))


def mcp_drive_upload_file(
    name: str, content: str, folder_id: Optional[str] = None, mime_type: str = "text/plain"
) -> str:
    """Upload or create a text or markdown file in Google Drive."""
    return _format_output(
        drive_upload_file(name=name, content=content, folder_id=folder_id, mime_type=mime_type)
    )


def mcp_drive_create_folder(name: str, parent_folder_id: Optional[str] = None) -> str:
    """Create a new folder in Google Drive."""
    return _format_output(drive_create_folder(name=name, parent_folder_id=parent_folder_id))


def mcp_drive_delete_file(file_id: str, permanent: bool = False) -> str:
    """Delete or trash a file in Google Drive."""
    return _format_output(drive_delete_file(file_id=file_id, permanent=permanent))


# ------------------------------------------------------------------------------
# Docs Tool Callers
# ------------------------------------------------------------------------------

def mcp_docs_get_document(document_id: str) -> str:
    """Extract and read the full text and structure of a Google Document."""
    return _format_output(docs_get_document(document_id=document_id))


def mcp_docs_create_document(title: str, initial_content: Optional[str] = None) -> str:
    """Create a new Google Document."""
    return _format_output(docs_create_document(title=title, initial_content=initial_content))


def mcp_docs_append_text(document_id: str, text: str) -> str:
    """Append text to the end of an existing Google Document."""
    return _format_output(docs_append_text(document_id=document_id, text=text))


# ------------------------------------------------------------------------------
# Tasks Tool Callers
# ------------------------------------------------------------------------------

def mcp_tasks_list_tasks(
    tasklist_id: str = "@default",
    show_completed: bool = False,
    due_max: Optional[str] = None,
    max_results: int = 50,
) -> str:
    """List tasks inside a Google Tasks list."""
    return _format_output(
        tasks_list_tasks(
            tasklist_id=tasklist_id,
            show_completed=show_completed,
            due_max=due_max,
            max_results=max_results,
        )
    )


def mcp_tasks_create_task(
    title: str,
    notes: Optional[str] = None,
    due_date: Optional[str] = None,
    tasklist_id: str = "@default",
) -> str:
    """Create a new task in Google Tasks."""
    return _format_output(
        tasks_create_task(
            title=title, notes=notes, due_date=due_date, tasklist_id=tasklist_id
        )
    )


def mcp_tasks_complete_task(task_id: str, tasklist_id: str = "@default") -> str:
    """Mark a task as completed in Google Tasks."""
    return _format_output(tasks_complete_task(task_id=task_id, tasklist_id=tasklist_id))


def mcp_tasks_delete_task(task_id: str, tasklist_id: str = "@default") -> str:
    """Delete a task from Google Tasks."""
    return _format_output(tasks_delete_task(task_id=task_id, tasklist_id=tasklist_id))


# ------------------------------------------------------------------------------
# Account Status Tool Caller
# ------------------------------------------------------------------------------

def mcp_google_account_status() -> str:
    """Check the connection status and authenticated email address for Google services."""
    return resource_account_info()


# ------------------------------------------------------------------------------
# LangChain StructuredTool List
# ------------------------------------------------------------------------------

google_mcp_tools = [
    # Gmail
    StructuredTool.from_function(mcp_gmail_search, name="gmail_search"),
    StructuredTool.from_function(mcp_gmail_get_message, name="gmail_get_message"),
    StructuredTool.from_function(mcp_gmail_send_message, name="gmail_send_message"),
    StructuredTool.from_function(mcp_gmail_create_draft, name="gmail_create_draft"),
    StructuredTool.from_function(mcp_gmail_list_labels, name="gmail_list_labels"),
    StructuredTool.from_function(mcp_gmail_modify_labels, name="gmail_modify_labels"),
    # Calendar
    StructuredTool.from_function(mcp_calendar_get_agenda, name="calendar_get_agenda"),
    StructuredTool.from_function(mcp_calendar_list_events, name="calendar_list_events"),
    StructuredTool.from_function(mcp_calendar_create_event, name="calendar_create_event"),
    StructuredTool.from_function(mcp_calendar_update_event, name="calendar_update_event"),
    StructuredTool.from_function(mcp_calendar_delete_event, name="calendar_delete_event"),
    # Drive
    StructuredTool.from_function(mcp_drive_search_files, name="drive_search_files"),
    StructuredTool.from_function(mcp_drive_get_file_metadata, name="drive_get_file_metadata"),
    StructuredTool.from_function(mcp_drive_read_file, name="drive_read_file"),
    StructuredTool.from_function(mcp_drive_upload_file, name="drive_upload_file"),
    StructuredTool.from_function(mcp_drive_create_folder, name="drive_create_folder"),
    StructuredTool.from_function(mcp_drive_delete_file, name="drive_delete_file"),
    # Docs
    StructuredTool.from_function(mcp_docs_get_document, name="docs_get_document"),
    StructuredTool.from_function(mcp_docs_create_document, name="docs_create_document"),
    StructuredTool.from_function(mcp_docs_append_text, name="docs_append_text"),
    # Tasks
    StructuredTool.from_function(mcp_tasks_list_tasks, name="tasks_list_tasks"),
    StructuredTool.from_function(mcp_tasks_create_task, name="tasks_create_task"),
    StructuredTool.from_function(mcp_tasks_complete_task, name="tasks_complete_task"),
    StructuredTool.from_function(mcp_tasks_delete_task, name="tasks_delete_task"),
    # Account
    StructuredTool.from_function(mcp_google_account_status, name="google_account_status"),
]
