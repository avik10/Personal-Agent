"""Microsoft Outlook Mail API Service (Microsoft Graph)."""

import logging
from typing import Any, Dict, List, Optional
import httpx

from ..auth import get_access_token, is_authenticated
from ..config import GRAPH_BASE_URL

logger = logging.getLogger("mcp.outlook.services.mail")


def outlook_list_messages(
    folder: str = "inbox",
    max_results: int = 25,
    query: Optional[str] = None,
    unread_only: bool = False,
) -> List[Dict[str, Any]]:
    """List or search emails from Microsoft Outlook mailbox.

    Args:
        folder: Folder name ('inbox', 'sentitems', 'drafts', 'archive', 'deleteditems').
        max_results: Maximum messages to return (default: 25).
        query: Optional search keyword to filter by sender, subject, or content.
        unread_only: If True, only returns unread emails.

    Returns:
        List of structured email dictionaries.
    """
    if not is_authenticated():
        logger.info("Outlook is not authenticated. Returning empty message list.")
        return []

    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Prefer": 'outlook.body-content-type="text"',
    }

    url = f"{GRAPH_BASE_URL}/me/mailFolders/{folder}/messages" if folder else f"{GRAPH_BASE_URL}/me/messages"
    params = {
        "$top": min(max_results, 50),
        "$select": "id,subject,from,toRecipients,receivedDateTime,isRead,bodyPreview,body,hasAttachments,webLink,importance",
    }

    if unread_only:
        params["$filter"] = "isRead eq false"

    if query and query.strip():
        # Microsoft Graph $search requires KQL or keyword quotes
        params["$search"] = f'"{query.strip()}"'
    else:
        # $orderby cannot be combined with $search in Graph API
        params["$orderby"] = "receivedDateTime desc"

    with httpx.Client(timeout=15.0) as client:
        res = client.get(url, headers=headers, params=params)
        if res.status_code != 200:
            logger.error("Failed to list Outlook messages: %s - %s", res.status_code, res.text)
            return []

        raw_items = res.json().get("value", [])
        messages = []
        for item in raw_items:
            sender_obj = item.get("from", {}).get("emailAddress", {})
            sender_name = sender_obj.get("name") or sender_obj.get("address") or "Unknown"
            sender_email = sender_obj.get("address") or ""

            to_recipients = [
                r.get("emailAddress", {}).get("address", "")
                for r in item.get("toRecipients", [])
                if r.get("emailAddress", {}).get("address")
            ]

            body_obj = item.get("body", {})
            messages.append({
                "id": item.get("id"),
                "subject": item.get("subject") or "(No Subject)",
                "from": sender_name,
                "from_email": sender_email,
                "to": to_recipients,
                "receivedDateTime": item.get("receivedDateTime"),
                "isRead": item.get("isRead", False),
                "bodyPreview": item.get("bodyPreview") or "",
                "body": body_obj.get("content") or item.get("bodyPreview") or "",
                "bodyType": body_obj.get("contentType", "text"),
                "hasAttachments": item.get("hasAttachments", False),
                "importance": item.get("importance", "normal"),
                "webLink": item.get("webLink", ""),
                "source": "outlook",
            })

        return messages


def outlook_get_message(message_id: str) -> Dict[str, Any]:
    """Retrieve full details of a specific Outlook email message.

    Args:
        message_id: Microsoft Graph message ID.

    Returns:
        Structured email dictionary.
    """
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    url = f"{GRAPH_BASE_URL}/me/messages/{message_id}"
    with httpx.Client(timeout=15.0) as client:
        res = client.get(url, headers=headers)
        if res.status_code != 200:
            raise RuntimeError(f"Outlook message not found or inaccessible: {res.text}")

        item = res.json()
        sender_obj = item.get("from", {}).get("emailAddress", {})
        return {
            "id": item.get("id"),
            "subject": item.get("subject") or "(No Subject)",
            "from": sender_obj.get("name") or sender_obj.get("address") or "Unknown",
            "from_email": sender_obj.get("address") or "",
            "to": [r.get("emailAddress", {}).get("address") for r in item.get("toRecipients", [])],
            "cc": [r.get("emailAddress", {}).get("address") for r in item.get("ccRecipients", [])],
            "receivedDateTime": item.get("receivedDateTime"),
            "isRead": item.get("isRead", False),
            "bodyPreview": item.get("bodyPreview") or "",
            "body": item.get("body", {}).get("content", ""),
            "bodyType": item.get("body", {}).get("contentType", "text"),
            "hasAttachments": item.get("hasAttachments", False),
            "webLink": item.get("webLink", ""),
            "source": "outlook",
        }


def outlook_send_message(
    to: str,
    subject: str,
    body: str,
    is_html: bool = False,
) -> Dict[str, Any]:
    """Compose and send an email message via Microsoft Outlook.

    Args:
        to: Comma-separated recipient email address(es).
        subject: Email subject line.
        body: Email body content.
        is_html: True if body content is HTML.

    Returns:
        Status dictionary confirming delivery.
    """
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    recipients_list = [addr.strip() for addr in to.split(",") if addr.strip()]
    if not recipients_list:
        raise ValueError("At least one recipient email address is required.")

    payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML" if is_html else "Text",
                "content": body,
            },
            "toRecipients": [
                {"emailAddress": {"address": addr}} for addr in recipients_list
            ],
        },
        "saveToSentItems": True,
    }

    url = f"{GRAPH_BASE_URL}/me/sendMail"
    with httpx.Client(timeout=20.0) as client:
        res = client.post(url, headers=headers, json=payload)
        if res.status_code not in (200, 202):
            raise RuntimeError(f"Failed to send email via Outlook: {res.status_code} - {res.text}")

        return {
            "status": "sent",
            "to": recipients_list,
            "subject": subject,
            "source": "outlook",
        }


def outlook_mark_read(message_id: str, is_read: bool = True) -> Dict[str, Any]:
    """Mark an Outlook message as read or unread."""
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    url = f"{GRAPH_BASE_URL}/me/messages/{message_id}"
    with httpx.Client(timeout=10.0) as client:
        res = client.patch(url, headers=headers, json={"isRead": is_read})
        if res.status_code != 200:
            raise RuntimeError(f"Failed to update message read status: {res.text}")

        return {"status": "updated", "id": message_id, "isRead": is_read, "source": "outlook"}


def outlook_delete_message(message_id: str) -> Dict[str, Any]:
    """Delete an email message in Outlook (moves to Deleted Items)."""
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    url = f"{GRAPH_BASE_URL}/me/messages/{message_id}"
    with httpx.Client(timeout=10.0) as client:
        res = client.delete(url, headers=headers)
        if res.status_code not in (200, 204):
            raise RuntimeError(f"Failed to delete Outlook message: {res.text}")

        return {"status": "deleted", "id": message_id, "source": "outlook"}
