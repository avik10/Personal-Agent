"""Dedicated Google Workspace Feature Endpoints."""

import asyncio
import json
import os
from typing import Dict
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow

try:
    from AI.features.google.auth import is_authenticated, get_account_info
    from AI.features.google.services.gmail import gmail_search_messages, gmail_send_message
    from AI.features.google.services.calendar import calendar_get_agenda, calendar_create_event
    from AI.features.google.services.drive import drive_search_files
    from AI.features.google.services.tasks import (
        tasks_list_tasks,
        tasks_create_task,
        tasks_complete_task,
        tasks_delete_task,
    )
    from AI.features.google.services.keep import (
        keep_list_notes,
        keep_create_note,
        keep_delete_note,
    )
    from AI.features.google.setup_auth import run_auth_flow
    from AI.features.google.config import CREDENTIALS_PATH, TOKEN_PATH, DEFAULT_SCOPES
except ImportError:
    from agent.mcp_google.auth import is_authenticated, get_account_info
    from agent.mcp_google.services.gmail import gmail_search_messages, gmail_send_message
    from agent.mcp_google.services.calendar import calendar_get_agenda, calendar_create_event
    from agent.mcp_google.services.drive import drive_search_files
    from agent.mcp_google.services.tasks import (
        tasks_list_tasks,
        tasks_create_task,
        tasks_complete_task,
        tasks_delete_task,
    )
    from agent.mcp_google.services.keep import (
        keep_list_notes,
        keep_create_note,
        keep_delete_note,
    )
    from agent.mcp_google.setup_auth import run_auth_flow
    from agent.mcp_google.config import CREDENTIALS_PATH, TOKEN_PATH, DEFAULT_SCOPES
from ..schemas import SendEmailModel, CreateEventModel, CreateNoteModel

router = APIRouter(prefix="/api/google", tags=["Google Workspace"])

# In-memory store for active OAuth flows to preserve PKCE code_verifier between redirect and callback
_active_oauth_flows: Dict[str, Flow] = {}


@router.get("/auth/url")
def get_google_auth_url(request: Request):
    """Generate the Google OAuth 2.0 consent URL for web authorization."""
    if not CREDENTIALS_PATH.exists():
        raise HTTPException(
            status_code=400,
            detail=f"Google OAuth client credentials not found at {CREDENTIALS_PATH}.",
        )

    with open(CREDENTIALS_PATH) as f:
        client_config = json.load(f)

    base_url = str(request.base_url).rstrip("/")
    redirect_uri = f"{base_url}/api/google/auth/callback"

    try:
        flow = Flow.from_client_config(
            client_config, scopes=DEFAULT_SCOPES, redirect_uri=redirect_uri
        )
        auth_url, state = flow.authorization_url(access_type="offline", prompt="consent")
        _active_oauth_flows[state] = flow
        return {"url": auth_url, "state": state, "redirect_uri": redirect_uri}
    except Exception as e:
        flow = Flow.from_client_config(
            client_config, scopes=DEFAULT_SCOPES, redirect_uri="http://localhost"
        )
        auth_url, state = flow.authorization_url(access_type="offline", prompt="consent")
        _active_oauth_flows[state] = flow
        return {"url": auth_url, "state": state, "redirect_uri": "http://localhost"}


@router.get("/auth/login")
def login_with_google(request: Request):
    """Redirect user's browser directly to Google OAuth consent screen."""
    if not CREDENTIALS_PATH.exists():
        raise HTTPException(
            status_code=400,
            detail=f"Google OAuth client credentials not found at {CREDENTIALS_PATH}.",
        )

    with open(CREDENTIALS_PATH) as f:
        client_config = json.load(f)

    base_url = str(request.base_url).rstrip("/")
    redirect_uri = f"{base_url}/api/google/auth/callback"

    try:
        flow = Flow.from_client_config(
            client_config, scopes=DEFAULT_SCOPES, redirect_uri=redirect_uri
        )
        auth_url, state = flow.authorization_url(access_type="offline", prompt="consent")
        _active_oauth_flows[state] = flow
        return RedirectResponse(url=auth_url)
    except Exception as e:
        flow = Flow.from_client_config(
            client_config, scopes=DEFAULT_SCOPES, redirect_uri="http://localhost"
        )
        auth_url, state = flow.authorization_url(access_type="offline", prompt="consent")
        _active_oauth_flows[state] = flow
        return RedirectResponse(url=auth_url)


@router.get("/auth/callback")
def google_auth_callback(request: Request, code: str = None, state: str = None, error: str = None):
    """Handle OAuth callback from Google, exchange code for tokens, and save token.json."""
    frontend_base = os.getenv("FRONTEND_URL", "").rstrip("/")

    if error:
        target = f"{frontend_base}/?google_auth=error&detail={error}" if frontend_base else f"/?google_auth=error&detail={error}"
        return RedirectResponse(url=target)

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code from Google.")

    flow = _active_oauth_flows.pop(state, None) if state else None
    if not flow:
        with open(CREDENTIALS_PATH) as f:
            client_config = json.load(f)
        base_url = str(request.base_url).rstrip("/")
        redirect_uri = f"{base_url}/api/google/auth/callback"
        flow = Flow.from_client_config(
            client_config, scopes=DEFAULT_SCOPES, redirect_uri=redirect_uri
        )

    try:
        flow.fetch_token(code=code)
        creds = flow.credentials

        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())

        target = f"{frontend_base}/?google_auth=success" if frontend_base else "/?google_auth=success"
        return RedirectResponse(url=target)
    except Exception as e:
        target = f"{frontend_base}/?google_auth=error&detail={str(e)}" if frontend_base else f"/?google_auth=error&detail={str(e)}"
        return RedirectResponse(url=target)


@router.post("/auth/connect")
async def trigger_one_click_auth():
    """Trigger desktop loopback Google OAuth flow in user's browser."""
    if not CREDENTIALS_PATH.exists():
        raise HTTPException(
            status_code=400,
            detail=f"Google OAuth client credentials not found at {CREDENTIALS_PATH}.",
        )

    try:
        success = await asyncio.to_thread(run_auth_flow, CREDENTIALS_PATH, TOKEN_PATH)
        if success:
            info = get_account_info()
            return {
                "success": True,
                "message": "Google Workspace connected successfully!",
                "email": info.get("emailAddress"),
            }
        else:
            raise HTTPException(
                status_code=500, detail="Google OAuth authorization was cancelled or failed."
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/disconnect")
async def disconnect_google_account():
    """Disconnect Google account by removing the stored OAuth token."""
    try:
        if TOKEN_PATH.exists():
            os.remove(TOKEN_PATH)
        return {"success": True, "message": "Google account disconnected successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/overview")
async def get_google_overview():
    """Retrieve combined Google Workspace status, recent emails, calendar agenda, and drive files."""
    authenticated = is_authenticated()
    if not authenticated:
        return {
            "authenticated": False,
            "email": None,
            "emails": [],
            "agenda": [],
            "files": [],
            "token_exists": TOKEN_PATH.exists(),
            "credentials_exist": CREDENTIALS_PATH.exists(),
        }

    account_info = get_account_info()

    def fetch_data():
        emails = []
        try:
            emails = gmail_search_messages(query="maxResults:5", max_results=5)
        except Exception as e:
            emails = [{"error": str(e)}]

        agenda = []
        try:
            agenda = calendar_get_agenda(days_ahead=7)
        except Exception as e:
            agenda = [{"error": str(e)}]

        files = []
        try:
            files = drive_search_files(page_size=8)
        except Exception as e:
            files = [{"error": str(e)}]

        return emails, agenda, files

    emails, agenda, files = await asyncio.to_thread(fetch_data)

    return {
        "authenticated": True,
        "email": account_info.get("emailAddress"),
        "emails": emails,
        "agenda": agenda,
        "files": files,
        "token_exists": True,
        "credentials_exist": True,
    }


@router.get("/emails")
async def get_google_emails(q: str = "", max_results: int = 15):
    """Fetch emails with optional search query."""
    if not is_authenticated():
        raise HTTPException(status_code=401, detail="Google account not authenticated")
    try:
        return await asyncio.to_thread(gmail_search_messages, query=q, max_results=max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/emails/send")
async def send_google_email(payload: SendEmailModel):
    """Send an email from the connected Gmail account."""
    if not is_authenticated():
        raise HTTPException(status_code=401, detail="Google account not authenticated")
    try:
        return await asyncio.to_thread(
            gmail_send_message, to=payload.to, subject=payload.subject, body=payload.body
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calendar")
async def get_google_calendar(days: int = 7):
    """Fetch upcoming calendar agenda."""
    if not is_authenticated():
        raise HTTPException(status_code=401, detail="Google account not authenticated")
    try:
        return await asyncio.to_thread(calendar_get_agenda, days_ahead=days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calendar/create")
async def create_google_event(payload: CreateEventModel):
    """Schedule an event on Google Calendar."""
    if not is_authenticated():
        raise HTTPException(status_code=401, detail="Google account not authenticated")
    try:
        return await asyncio.to_thread(
            calendar_create_event,
            summary=payload.summary,
            start_time=payload.start_time,
            end_time=payload.end_time,
            description=payload.description,
            add_meet_link=payload.add_meet_link,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drive")
async def get_google_drive(query: str = "", page_size: int = 20):
    """Fetch files from Google Drive."""
    if not is_authenticated():
        raise HTTPException(status_code=401, detail="Google account not authenticated")
    try:
        return await asyncio.to_thread(drive_search_files, query=query, page_size=page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notes")
async def get_google_notes(show_completed: bool = True, max_results: int = 50):
    """Fetch notes and tasks from Google Keep & Tasks."""
    if not is_authenticated():
        raise HTTPException(status_code=401, detail="Google account not authenticated")
    try:
        return await asyncio.to_thread(keep_list_notes, max_results=max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notes/create")
async def create_google_note(payload: CreateNoteModel):
    """Create a new note or task in Google Keep & Tasks."""
    if not is_authenticated():
        raise HTTPException(status_code=401, detail="Google account not authenticated")
    try:
        return await asyncio.to_thread(
            keep_create_note,
            title=payload.title,
            text=payload.notes,
            due_date=payload.due_date,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notes/{task_id}/complete")
async def complete_google_note(task_id: str):
    """Mark a note/task as completed."""
    if not is_authenticated():
        raise HTTPException(status_code=401, detail="Google account not authenticated")
    try:
        return await asyncio.to_thread(tasks_complete_task, task_id=task_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/notes/{task_id}")
async def delete_google_note(task_id: str):
    """Delete a note or task in Google Keep & Tasks."""
    if not is_authenticated():
        raise HTTPException(status_code=401, detail="Google account not authenticated")
    try:
        return await asyncio.to_thread(keep_delete_note, note_id=task_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

