"""Gmail API Tools for MCP."""

import base64
from email.message import EmailMessage
from typing import Any, Dict, List, Optional

from ..auth import get_service


import html
import re


def _clean_body_text(text: str) -> str:
    """Clean HTML tags, unescape entities, strip invisible characters, and normalize line endings."""
    if not text:
        return ""

    # Strip zero-width non-joiners, BOM, and direction marks
    text = re.sub(r"[\u200b-\u200f\ufeff\u202a-\u202e]", "", text)
    # Replace non-breaking spaces with standard space
    text = text.replace("\u00a0", " ")

    if any(tag in text.lower() for tag in ("<html", "<body", "<div", "<table", "<!doctype", "<p")):
        # Remove style and script blocks
        text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", text, flags=re.DOTALL | re.IGNORECASE)
        # Convert <br>, <p>, and <tr> to newlines before stripping tags
        text = re.sub(r"<(br|p|tr|/tr)[^>]*>", "\n", text, flags=re.IGNORECASE)
        # Remove all other HTML tags
        text = re.sub(r"<[^>]+>", " ", text)
        # Decode entities (&nbsp;, &#39;, &amp;, etc.)
        text = html.unescape(text)

    # Normalize carriage returns and line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse multiple inline spaces and tabs
    text = re.sub(r"[ \t]+", " ", text)
    # Collapse 3 or more newlines into 2
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text).strip()
    return text[:3500].strip()


def _decode_body(payload: Dict[str, Any]) -> str:
    """Helper to extract and decode plain text body from Gmail message payload."""
    # First priority: find a part explicitly marked text/plain
    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data", "")
                if data:
                    raw = base64.urlsafe_b64decode(data.encode("UTF-8")).decode(
                        "UTF-8", errors="replace"
                    )
                    return _clean_body_text(raw)
        # Second priority: recursively check subparts
        for part in payload["parts"]:
            if "parts" in part:
                sub = _decode_body(part)
                if sub:
                    return _clean_body_text(sub)
        # Third priority: text/html part
        for part in payload["parts"]:
            if part.get("mimeType") == "text/html":
                data = part.get("body", {}).get("data", "")
                if data:
                    raw = base64.urlsafe_b64decode(data.encode("UTF-8")).decode(
                        "UTF-8", errors="replace"
                    )
                    return _clean_body_text(raw)

    data = payload.get("body", {}).get("data", "")
    if data:
        raw = base64.urlsafe_b64decode(data.encode("UTF-8")).decode(
            "UTF-8", errors="replace"
        )
        return _clean_body_text(raw)
    return ""


def _extract_headers(headers: List[Dict[str, str]]) -> Dict[str, str]:
    """Helper to extract standard header fields into a dictionary."""
    wanted = {"From", "To", "Subject", "Date", "Cc", "Bcc", "Reply-To"}
    return {h["name"]: h["value"] for h in headers if h.get("name") in wanted}


def gmail_search_messages(query: str = "", max_results: int = 10) -> List[Dict[str, Any]]:
    """Search messages in Gmail with standard Gmail search syntax.

    Args:
        query: Gmail search query (e.g., 'is:unread', 'from:colleague@company.com', 'has:attachment').
        max_results: Maximum number of messages to return (default 10, max 50).
    """
    service = get_service("gmail", "v1")
    max_results = max(1, min(max_results, 50))
    res = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=max_results)
        .execute()
    )
    messages = res.get("messages", [])

    results = []
    for msg_stub in messages:
        try:
            m = (
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=msg_stub["id"],
                    format="metadata",
                    metadataHeaders=["From", "Subject", "Date"],
                )
                .execute()
            )
            headers = _extract_headers(m.get("payload", {}).get("headers", []))
            results.append(
                {
                    "id": m.get("id"),
                    "threadId": m.get("threadId"),
                    "snippet": m.get("snippet"),
                    "subject": headers.get("Subject", "(no subject)"),
                    "from": headers.get("From", "unknown"),
                    "date": headers.get("Date", ""),
                    "labelIds": m.get("labelIds", []),
                }
            )
        except Exception as e:
            results.append({"id": msg_stub["id"], "error": str(e)})

    return results


def gmail_get_message(message_id: str) -> Dict[str, Any]:
    """Retrieve full details of a specific email message by ID, including plain text content.

    Args:
        message_id: The unique Gmail ID of the message.
    """
    service = get_service("gmail", "v1")
    message = (
        service.users().messages().get(userId="me", id=message_id, format="full").execute()
    )

    payload = message.get("payload", {})
    headers = _extract_headers(payload.get("headers", []))
    body = _decode_body(payload)

    return {
        "id": message.get("id"),
        "threadId": message.get("threadId"),
        "labelIds": message.get("labelIds", []),
        "snippet": message.get("snippet", ""),
        "headers": headers,
        "body": body if body else message.get("snippet", ""),
    }


def gmail_send_message(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
) -> Dict[str, Any]:
    """Send an email from the user's Gmail account.

    Args:
        to: Recipient email address(es), comma-separated.
        subject: Email subject.
        body: Plain text content of the message.
        cc: Optional CC email address(es).
        bcc: Optional BCC email address(es).
    """
    clean_to = (to or "").strip()
    if not clean_to:
        raise ValueError("Recipient 'to' email address is required and cannot be empty.")

    clean_subject = (subject or "").strip()
    clean_body = (body or "").strip()

    service = get_service("gmail", "v1")

    message = EmailMessage()
    message.set_content(clean_body)
    message["To"] = clean_to
    message["Subject"] = clean_subject
    if cc:
        message["Cc"] = cc.strip()
    if bcc:
        message["Bcc"] = bcc.strip()

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    result = (
        service.users()
        .messages()
        .send(userId="me", body={"raw": raw_message})
        .execute()
    )

    return {
        "status": "sent",
        "to": clean_to,
        "subject": clean_subject,
        "id": result.get("id"),
        "threadId": result.get("threadId"),
        "labelIds": result.get("labelIds", []),
    }


def gmail_create_draft(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a draft email in the user's Gmail mailbox without sending.

    Args:
        to: Recipient email address(es).
        subject: Draft email subject line.
        body: Draft message body text.
        cc: Optional CC email address(es).
    """
    service = get_service("gmail", "v1")

    message = EmailMessage()
    message.set_content(body)
    message["To"] = to
    message["Subject"] = subject
    if cc:
        message["Cc"] = cc

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    draft = (
        service.users()
        .drafts()
        .create(userId="me", body={"message": {"raw": raw_message}})
        .execute()
    )

    return {
        "status": "draft_created",
        "draftId": draft.get("id"),
        "messageId": draft.get("message", {}).get("id"),
    }


def gmail_list_labels() -> List[Dict[str, Any]]:
    """List all mailbox labels (system folders like INBOX, SENT, TRASH, plus user-defined labels)."""
    service = get_service("gmail", "v1")
    res = service.users().labels().list(userId="me").execute()
    return res.get("labels", [])


def gmail_modify_labels(
    message_id: str,
    add_labels: Optional[List[str]] = None,
    remove_labels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Add or remove labels from a message (e.g. mark read, star, unstar, archive).

    Args:
        message_id: Target email message ID.
        add_labels: Labels to add (e.g., ['STARRED', 'IMPORTANT']).
        remove_labels: Labels to remove (e.g., ['UNREAD', 'INBOX'] to mark read/archive).
    """
    service = get_service("gmail", "v1")
    body: Dict[str, Any] = {}
    if add_labels:
        body["addLabelIds"] = add_labels
    if remove_labels:
        body["removeLabelIds"] = remove_labels

    res = (
        service.users()
        .messages()
        .modify(userId="me", id=message_id, body=body)
        .execute()
    )
    return {
        "status": "updated",
        "id": res.get("id"),
        "labelIds": res.get("labelIds", []),
    }
