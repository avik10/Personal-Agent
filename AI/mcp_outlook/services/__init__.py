"""Microsoft Outlook Services Module."""

from .mail import (
    outlook_list_messages,
    outlook_get_message,
    outlook_send_message,
    outlook_mark_read,
    outlook_delete_message,
)

__all__ = [
    "outlook_list_messages",
    "outlook_get_message",
    "outlook_send_message",
    "outlook_mark_read",
    "outlook_delete_message",
]
