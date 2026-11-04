"""Dedicated Microsoft Outlook Feature Endpoints."""

import asyncio
import os
from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from agent.mcp_outlook.auth import (
    is_authenticated,
    get_account_info,
    get_authorization_url,
    exchange_code_for_token,
    disconnect,
    MicrosoftAuthError,
)
from agent.mcp_outlook.services.mail import (
    outlook_list_messages,
    outlook_get_message,
    outlook_send_message,
    outlook_mark_read,
    outlook_delete_message,
)
from agent.mcp_outlook.config import (
    MICROSOFT_CLIENT_ID,
    TOKEN_PATH,
)
from ..schemas import SendEmailModel

router = APIRouter(prefix="/api/outlook", tags=["Microsoft Outlook"])


@router.get("/auth/url")
def get_outlook_auth_url(request: Request):
    """Generate the Microsoft OAuth 2.0 consent URL for web authorization."""
    if not MICROSOFT_CLIENT_ID:
        raise HTTPException(
            status_code=400,
            detail=(
                "MICROSOFT_CLIENT_ID is not configured. "
                "Please add MICROSOFT_CLIENT_ID to your environment variables or .env file."
            ),
        )

    base_url = str(request.base_url).rstrip("/")
    redirect_uri = f"{base_url}/api/outlook/auth/callback"

    try:
        auth_url = get_authorization_url(redirect_uri=redirect_uri)
        return {"url": auth_url, "redirect_uri": redirect_uri}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auth/login")
def login_with_microsoft(request: Request):
    """Redirect user's browser directly to Microsoft OAuth consent screen."""
    if not MICROSOFT_CLIENT_ID:
        raise HTTPException(
            status_code=400,
            detail="MICROSOFT_CLIENT_ID is not configured. Register an application in Azure Portal.",
        )

    base_url = str(request.base_url).rstrip("/")
    redirect_uri = f"{base_url}/api/outlook/auth/callback"
    auth_url = get_authorization_url(redirect_uri=redirect_uri)
    return RedirectResponse(url=auth_url)


@router.get("/auth/callback")
def microsoft_auth_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
):
    """Handle OAuth callback from Microsoft, exchange code for tokens, and save token.json."""
    frontend_base = os.getenv("FRONTEND_URL", "").rstrip("/")

    if error:
        err_msg = error_description or error
        target = (
            f"{frontend_base}/?microsoft_auth=error&detail={err_msg}"
            if frontend_base
            else f"/?microsoft_auth=error&detail={err_msg}"
        )
        return RedirectResponse(url=target)

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code from Microsoft.")

    base_url = str(request.base_url).rstrip("/")
    redirect_uri = f"{base_url}/api/outlook/auth/callback"

    try:
        exchange_code_for_token(code=code, redirect_uri=redirect_uri)
        target = f"{frontend_base}/?microsoft_auth=success" if frontend_base else "/?microsoft_auth=success"
        return RedirectResponse(url=target)
    except Exception as e:
        target = (
            f"{frontend_base}/?microsoft_auth=error&detail={str(e)}"
            if frontend_base
            else f"/?microsoft_auth=error&detail={str(e)}"
        )
        return RedirectResponse(url=target)


@router.get("/auth/status")
def get_outlook_status():
    """Retrieve connectivity and profile status of the connected Microsoft account."""
    auth = is_authenticated()
    if not auth:
        return {
            "authenticated": False,
            "email": "Not connected",
            "displayName": "",
            "configured": bool(MICROSOFT_CLIENT_ID),
        }

    try:
        info = get_account_info()
        return {
            "authenticated": True,
            "email": info.get("email", ""),
            "displayName": info.get("displayName", ""),
            "configured": True,
        }
    except Exception as e:
        return {
            "authenticated": False,
            "email": "Not connected",
            "error": "Session expired or access token is empty.",
            "configured": bool(MICROSOFT_CLIENT_ID),
        }


@router.post("/auth/disconnect")
def disconnect_outlook():
    """Disconnect connected Microsoft account and delete saved credentials."""
    success = disconnect()
    return {"status": "disconnected", "success": success}


@router.get("/messages")
async def list_outlook_messages(
    folder: str = "inbox",
    query: Optional[str] = None,
    unread_only: bool = False,
    max_results: int = 25,
):
    """Fetch emails from Microsoft Outlook inbox or specific folder."""
    if not is_authenticated():
        return []

    try:
        return await asyncio.to_thread(
            outlook_list_messages,
            folder=folder,
            query=query,
            unread_only=unread_only,
            max_results=max_results,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages/{message_id}")
async def get_outlook_message_details(message_id: str):
    """Retrieve full details of an Outlook email."""
    if not is_authenticated():
        raise HTTPException(status_code=401, detail="Microsoft Outlook is not authenticated.")

    try:
        return await asyncio.to_thread(outlook_get_message, message_id=message_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/messages/send")
async def send_outlook_message(payload: SendEmailModel):
    """Send an email via connected Microsoft Outlook account."""
    if not is_authenticated():
        raise HTTPException(status_code=401, detail="Microsoft Outlook is not authenticated.")

    try:
        return await asyncio.to_thread(
            outlook_send_message,
            to=payload.to,
            subject=payload.subject,
            body=payload.body,
            is_html=getattr(payload, "is_html", False),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages/{message_id}/read")
async def mark_outlook_message_read(message_id: str, is_read: bool = True):
    """Mark an Outlook message as read or unread."""
    if not is_authenticated():
        raise HTTPException(status_code=401, detail="Microsoft Outlook is not authenticated.")

    try:
        return await asyncio.to_thread(outlook_mark_read, message_id=message_id, is_read=is_read)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/messages/{message_id}")
async def delete_outlook_message(message_id: str):
    """Delete an Outlook email message."""
    if not is_authenticated():
        raise HTTPException(status_code=401, detail="Microsoft Outlook is not authenticated.")

    try:
        return await asyncio.to_thread(outlook_delete_message, message_id=message_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
