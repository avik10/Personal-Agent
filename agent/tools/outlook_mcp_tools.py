"""Microsoft Outlook MCP Tools adapter for LangChain / LangGraph Agent."""

import json
from typing import Any, List, Optional
from langchain_core.tools import StructuredTool

from mcp_outlook.services.mail import (
    outlook_list_messages,
    outlook_get_message,
    outlook_send_message,
    outlook_mark_read,
    outlook_delete_message,
)
from mcp_outlook.auth import is_authenticated, get_account_info


def _format_output(data: Any) -> str:
    """Format Python dictionaries/lists as formatted JSON string for LLMs."""
    if isinstance(data, (dict, list)):
        return json.dumps(data, indent=2)
    return str(data)


def mcp_outlook_account_info() -> str:
    """Check Microsoft Outlook connection status and authenticated email address."""
    if not is_authenticated():
        return (
            "Microsoft Outlook is currently NOT connected. "
            "Please go to Microsoft Bucket in the application to connect your Microsoft/Outlook account."
        )
    try:
        info = get_account_info()
        return f"Microsoft Outlook Connected: {info.get('email')} ({info.get('displayName')})"
    except Exception as e:
        return f"Error retrieving Outlook account info: {e}"


def mcp_outlook_list_messages(folder: str = "inbox", max_results: int = 15, unread_only: bool = False) -> str:
    """List recent emails from Microsoft Outlook inbox or specified folder."""
    if not is_authenticated():
        return "Microsoft Outlook is not connected. Please connect your Outlook account in Microsoft Bucket."
    try:
        messages = outlook_list_messages(folder=folder, max_results=max_results, unread_only=unread_only)
        if not messages:
            unread_str = "unread " if unread_only else ""
            return f"No {unread_str}emails found in Outlook {folder}."

        lines = [f"Found {len(messages)} Outlook message(s):"]
        for idx, m in enumerate(messages, 1):
            status = "Unread" if not m.get("isRead") else "Read"
            lines.append(
                f"{idx}. [{status}] From: {m.get('from')} <{m.get('from_email')}> | "
                f"Subject: {m.get('subject')} | Date: {m.get('receivedDateTime')} | ID: {m.get('id')}\n"
                f"   Preview: {m.get('bodyPreview', '')[:140]}"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"Could not list Outlook emails: {e}"


def mcp_outlook_search_messages(query: str, max_results: int = 15) -> str:
    """Search emails in Microsoft Outlook by keyword, sender, or subject."""
    if not is_authenticated():
        return "Microsoft Outlook is not connected. Please connect your Outlook account in Microsoft Bucket."
    try:
        messages = outlook_list_messages(query=query, max_results=max_results)
        if not messages:
            return f"No Outlook messages found matching query: '{query}'."

        lines = [f"Found {len(messages)} Outlook message(s) matching '{query}':"]
        for idx, m in enumerate(messages, 1):
            status = "Unread" if not m.get("isRead") else "Read"
            lines.append(
                f"{idx}. [{status}] From: {m.get('from')} | Subject: {m.get('subject')} | "
                f"Date: {m.get('receivedDateTime')} | ID: {m.get('id')}\n"
                f"   Preview: {m.get('bodyPreview', '')[:140]}"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"Could not search Outlook emails: {e}"


def mcp_outlook_get_message(message_id: str) -> str:
    """Retrieve full body and header details of a specific Outlook email message."""
    if not is_authenticated():
        return "Microsoft Outlook is not connected. Please connect your Outlook account in Microsoft Bucket."
    try:
        msg = outlook_get_message(message_id=message_id)
        return _format_output(msg)
    except Exception as e:
        return f"Could not retrieve Outlook message {message_id}: {e}"


def mcp_outlook_send_message(to: str, subject: str, body: str, is_html: bool = False) -> str:
    """Send an email via Microsoft Outlook to recipient address(es)."""
    if not is_authenticated():
        return "Microsoft Outlook is not connected. Please connect your Outlook account in Microsoft Bucket."
    try:
        res = outlook_send_message(to=to, subject=subject, body=body, is_html=is_html)
        return f"Email successfully sent via Microsoft Outlook to: {to} with subject '{subject}'."
    except Exception as e:
        return f"Failed to send email via Outlook: {e}"


def mcp_outlook_mark_read(message_id: str, is_read: bool = True) -> str:
    """Mark an Outlook email as read or unread."""
    if not is_authenticated():
        return "Microsoft Outlook is not connected."
    try:
        outlook_mark_read(message_id=message_id, is_read=is_read)
        status = "read" if is_read else "unread"
        return f"Outlook message {message_id} marked as {status}."
    except Exception as e:
        return f"Failed to update Outlook message read status: {e}"


# List of StructuredTools ready for LangChain / LangGraph agents
outlook_mcp_tools = [
    StructuredTool.from_function(
        mcp_outlook_account_info,
        name="outlook_account_info",
        description="Check if Microsoft Outlook account is connected, view user email and account status.",
    ),
    StructuredTool.from_function(
        mcp_outlook_list_messages,
        name="outlook_list_messages",
        description="List emails from Microsoft Outlook inbox or mail folders with unread filter.",
    ),
    StructuredTool.from_function(
        mcp_outlook_search_messages,
        name="outlook_search_messages",
        description="Search Microsoft Outlook emails by sender, subject, or body keyword.",
    ),
    StructuredTool.from_function(
        mcp_outlook_get_message,
        name="outlook_get_message",
        description="Retrieve full email content and details for an Outlook message ID.",
    ),
    StructuredTool.from_function(
        mcp_outlook_send_message,
        name="outlook_send_message",
        description="Send an email message via the user's connected Microsoft Outlook account.",
    ),
    StructuredTool.from_function(
        mcp_outlook_mark_read,
        name="outlook_mark_read",
        description="Mark an Outlook message as read or unread.",
    ),
]
