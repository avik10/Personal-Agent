"""Google Workspace Authentication and Service Manager."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource, build

from .config import CREDENTIALS_PATH, DEFAULT_SCOPES, TOKEN_PATH


class GoogleAuthError(Exception):
    """Raised when authentication credentials or tokens are missing or invalid."""
    pass


import threading

_SERVICES_LOCAL = threading.local()
_AUTH_LOCK = threading.Lock()


def get_credentials(scopes: Optional[list] = None) -> Credentials:
    """Retrieve valid user credentials from disk or refresh if needed.

    Raises:
        GoogleAuthError: If no valid token is found or credentials file is missing.
    """
    target_scopes = scopes or DEFAULT_SCOPES
    creds: Optional[Credentials] = None

    with _AUTH_LOCK:
        if TOKEN_PATH.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), target_scopes)
            except Exception:
                creds = None

        if creds and creds.valid:
            return creds

        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Save refreshed token
                TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
                with open(TOKEN_PATH, "w") as token_file:
                    token_file.write(creds.to_json())
                return creds
            except Exception as e:
                raise GoogleAuthError(
                    f"Failed to refresh existing Google token: {e}. "
                    "Please run `python3 -m mcp_google.setup_auth` to re-authorize."
                ) from e

    # If we get here, no valid or refreshable token is present
    cred_hint = (
        f"Credentials file found at {CREDENTIALS_PATH}."
        if CREDENTIALS_PATH.exists()
        else f"Missing client credentials at {CREDENTIALS_PATH}."
    )
    raise GoogleAuthError(
        f"Google services are not authorized. {cred_hint} "
        "Please run `python3 -m mcp_google.setup_auth` to complete the one-time OAuth authorization."
    )


def get_service(service_name: str, version: str) -> Resource:
    """Get or build a thread-local Google API service client instance.

    Google API Resource instances wrapping httplib2 are not thread-safe.
    Using thread-local storage guarantees each thread has its own isolated
    Resource and SSL socket connection.
    """
    if not hasattr(_SERVICES_LOCAL, "cache"):
        _SERVICES_LOCAL.cache = {}

    cache_key = f"{service_name}:{version}"
    if cache_key in _SERVICES_LOCAL.cache:
        return _SERVICES_LOCAL.cache[cache_key]

    creds = get_credentials()
    service = build(service_name, version, credentials=creds, cache_discovery=False)
    _SERVICES_LOCAL.cache[cache_key] = service
    return service


def is_authenticated() -> bool:
    """Check if valid credentials exist without raising exceptions."""
    try:
        creds = get_credentials()
        return creds is not None and creds.valid
    except GoogleAuthError:
        return False


def get_account_info() -> Dict[str, Any]:
    """Retrieve basic email info for the authenticated account."""
    try:
        service = get_service("gmail", "v1")
        profile = service.users().getProfile(userId="me").execute()
        return {
            "emailAddress": profile.get("emailAddress"),
            "messagesTotal": profile.get("messagesTotal"),
            "threadsTotal": profile.get("threadsTotal"),
            "status": "authenticated",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
