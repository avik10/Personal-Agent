"""Microsoft Outlook MCP Server Module."""

from .auth import is_authenticated, get_account_info, MicrosoftAuthError
from .services.mail import (
    outlook_list_messages,
    outlook_get_message,
    outlook_send_message,
    outlook_mark_read,
    outlook_delete_message,
)

__all__ = [
    "is_authenticated",
    "get_account_info",
    "MicrosoftAuthError",
    "outlook_list_messages",
    "outlook_get_message",
    "outlook_send_message",
    "outlook_mark_read",
    "outlook_delete_message",
]
