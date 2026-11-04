"""Main entrypoint for Microsoft Outlook Model Context Protocol (MCP) Server."""

import functools
import json
import logging
import sys
from typing import Any, Callable, Dict, List, Optional
from mcp.server.mcpserver import MCPServer

from .auth import MicrosoftAuthError, get_account_info, is_authenticated
from .services import mail as mail_svc

logger = logging.getLogger("mcp.outlook.server")

# Create MCP Server instance
server = MCPServer(
    name="microsoft-outlook-mcp",
    instructions=(
        "Microsoft Outlook MCP Server. Provides comprehensive tools to interact with "
        "Outlook Mail via Microsoft Graph API on behalf of the user."
    ),
    version="1.0.0",
)


def safe_tool(fn: Callable) -> Callable:
    """Decorator to catch Microsoft API errors or missing authentication."""
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return fn(*args, **kwargs)
        except MicrosoftAuthError as e:
            return {
                "error": "MicrosoftAuthError",
                "message": str(e),
                "resolution": "Please sign in to your Microsoft Account via the Microsoft Bucket in the application.",
            }
        except Exception as e:
            logger.error("Unexpected error in Outlook tool %s: %s", fn.__name__, e)
            return {"error": type(e).__name__, "message": str(e)}

    return wrapper


@server.tool(
    name="outlook_get_account_info",
    description="Check Microsoft Outlook authentication status and view connected email address and account info.",
)
@safe_tool
def get_outlook_account_info() -> Dict[str, Any]:
    if not is_authenticated():
        return {
            "authenticated": False,
            "status": "not_authenticated",
            "message": "Microsoft Outlook is not connected. Use the Microsoft Bucket to sign in.",
        }
    return get_account_info()


@server.tool(
    name="outlook_list_messages",
    description="List or search email messages from Microsoft Outlook inbox or specific mail folder.",
)
@safe_tool
def list_messages(
    folder: str = "inbox",
    max_results: int = 25,
    query: Optional[str] = None,
    unread_only: bool = False,
) -> List[Dict[str, Any]]:
    return mail_svc.outlook_list_messages(
        folder=folder,
        max_results=max_results,
        query=query,
        unread_only=unread_only,
    )


@server.tool(
    name="outlook_get_message",
    description="Retrieve full email content, sender, headers, and body for a specific Outlook message ID.",
)
@safe_tool
def get_message(message_id: str) -> Dict[str, Any]:
    return mail_svc.outlook_get_message(message_id=message_id)


@server.tool(
    name="outlook_send_message",
    description="Compose and send an email message through the user's connected Microsoft Outlook account.",
)
@safe_tool
def send_message(
    to: str,
    subject: str,
    body: str,
    is_html: bool = False,
) -> Dict[str, Any]:
    return mail_svc.outlook_send_message(
        to=to,
        subject=subject,
        body=body,
        is_html=is_html,
    )


@server.tool(
    name="outlook_mark_read",
    description="Mark an Outlook email message as read (is_read=True) or unread (is_read=False).",
)
@safe_tool
def mark_read(message_id: str, is_read: bool = True) -> Dict[str, Any]:
    return mail_svc.outlook_mark_read(message_id=message_id, is_read=is_read)


@server.tool(
    name="outlook_delete_message",
    description="Delete an Outlook email message (moves it to the Deleted Items folder).",
)
@safe_tool
def delete_message(message_id: str) -> Dict[str, Any]:
    return mail_svc.outlook_delete_message(message_id=message_id)


def main():
    """Run the MCP server over standard input/output."""
    server.run_stdio()


if __name__ == "__main__":
    main()
