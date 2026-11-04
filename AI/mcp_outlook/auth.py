"""Microsoft Outlook Authentication & Token Management Manager."""

import json
import logging
import time
import urllib.parse
from typing import Any, Dict, Optional
import httpx

from .config import (
    AUTH_ENDPOINT,
    DEFAULT_SCOPES,
    GRAPH_BASE_URL,
    MICROSOFT_CLIENT_ID,
    MICROSOFT_CLIENT_SECRET,
    TOKEN_ENDPOINT,
    TOKEN_PATH,
)

logger = logging.getLogger("mcp.outlook.auth")


class MicrosoftAuthError(Exception):
    """Raised when authentication credentials or tokens are missing or invalid."""
    pass


def get_authorization_url(redirect_uri: str, state: str = "outlook_auth") -> str:
    """Generate Microsoft OAuth 2.0 authorization URL for user consent."""
    if not MICROSOFT_CLIENT_ID:
        raise MicrosoftAuthError(
            "MICROSOFT_CLIENT_ID is not configured in .env. "
            "Please register an application in Azure Portal (portal.azure.com)."
        )

    params = {
        "client_id": MICROSOFT_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "response_mode": "query",
        "scope": " ".join(DEFAULT_SCOPES),
        "state": state,
        "prompt": "select_account",
    }
    return f"{AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}"


def _parse_id_token(id_token: str) -> Dict[str, Any]:
    """Extract claims from JWT id_token payload without external dependencies."""
    try:
        import base64
        parts = id_token.split(".")
        if len(parts) >= 2:
            payload_b64 = parts[1]
            rem = len(payload_b64) % 4
            if rem > 0:
                payload_b64 += "=" * (4 - rem)
            payload_json = base64.urlsafe_b64decode(payload_b64).decode("utf-8")
            return json.loads(payload_json)
    except Exception as e:
        logger.debug("Could not parse id_token: %s", e)
    return {}


def exchange_code_for_token(code: str, redirect_uri: str) -> Dict[str, Any]:
    """Exchange authorization code for access and refresh tokens."""
    if not MICROSOFT_CLIENT_ID:
        raise MicrosoftAuthError("MICROSOFT_CLIENT_ID is required for token exchange.")

    data = {
        "client_id": MICROSOFT_CLIENT_ID,
        "scope": " ".join(DEFAULT_SCOPES),
        "code": code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    if MICROSOFT_CLIENT_SECRET:
        data["client_secret"] = MICROSOFT_CLIENT_SECRET

    with httpx.Client(timeout=15.0) as client:
        res = client.post(TOKEN_ENDPOINT, data=data)
        if res.status_code != 200:
            logger.error("Token exchange failed: %s - %s", res.status_code, res.text)
            raise MicrosoftAuthError(f"Microsoft token exchange failed: {res.text}")

        token_data = res.json()
        token_data["created_at"] = time.time()
        token_data["expires_at"] = time.time() + token_data.get("expires_in", 3600)

        # Extract claims from id_token if available (provides real personal email)
        if "id_token" in token_data:
            claims = _parse_id_token(token_data["id_token"])
            if claims.get("preferred_username"):
                token_data["preferred_username"] = claims["preferred_username"]
            if claims.get("email"):
                token_data["email_claim"] = claims["email"]
            if claims.get("name"):
                token_data["name_claim"] = claims["name"]

        # Save to token storage
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_PATH, "w") as f:
            json.dump(token_data, f, indent=2)

        return token_data


def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    """Refresh an expired access token using the refresh token."""
    data = {
        "client_id": MICROSOFT_CLIENT_ID,
        "scope": " ".join(DEFAULT_SCOPES),
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    if MICROSOFT_CLIENT_SECRET:
        data["client_secret"] = MICROSOFT_CLIENT_SECRET

    with httpx.Client(timeout=15.0) as client:
        res = client.post(TOKEN_ENDPOINT, data=data)
        if res.status_code != 200:
            raise MicrosoftAuthError(f"Failed to refresh Microsoft token: {res.text}")

        token_data = res.json()
        token_data["created_at"] = time.time()
        token_data["expires_at"] = time.time() + token_data.get("expires_in", 3600)
        # Preserve existing refresh token if not returned in refresh response
        if "refresh_token" not in token_data:
            token_data["refresh_token"] = refresh_token

        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_PATH, "w") as f:
            json.dump(token_data, f, indent=2)

        return token_data


def get_access_token() -> str:
    """Retrieve a valid, unexpired Microsoft Graph access token."""
    if not TOKEN_PATH.exists():
        raise MicrosoftAuthError(
            f"Microsoft credentials not found at {TOKEN_PATH}. "
            "Please authenticate via the Microsoft Bucket in the application."
        )

    try:
        with open(TOKEN_PATH, "r") as f:
            token_data = json.load(f)
    except Exception as e:
        raise MicrosoftAuthError(f"Failed to read token file: {e}")

    access_token = (token_data.get("access_token") or "").strip()
    expires_at = token_data.get("expires_at", 0)
    refresh_tok = (token_data.get("refresh_token") or "").strip()

    # Refresh if expired or expiring within 60 seconds
    if time.time() >= (expires_at - 60):
        if refresh_tok:
            try:
                new_tokens = refresh_access_token(refresh_tok)
                refreshed_token = (new_tokens.get("access_token") or "").strip()
                if refreshed_token:
                    return refreshed_token
            except Exception as e:
                logger.warning("Token refresh failed: %s", e)
                raise MicrosoftAuthError(f"Token refresh failed: {e}. Please re-authenticate.")
        else:
            raise MicrosoftAuthError("Access token expired and no refresh token is present.")

    if not access_token:
        raise MicrosoftAuthError("Access token is empty. Please authenticate via Microsoft Bucket.")

    return access_token


def is_authenticated() -> bool:
    """Check if valid Microsoft authentication exists without raising exceptions."""
    if not TOKEN_PATH.exists():
        return False
    try:
        token = get_access_token()
        return bool(token and token.strip())
    except Exception:
        return False


def get_account_info() -> Dict[str, Any]:
    """Retrieve profile and mailbox details for the authenticated Microsoft user."""
    token = get_access_token()
    if not token or not token.strip():
        raise MicrosoftAuthError("Access token is empty.")

    headers = {"Authorization": f"Bearer {token.strip()}"}
    profile: Dict[str, Any] = {}

    with httpx.Client(timeout=10.0) as client:
        res = client.get(f"{GRAPH_BASE_URL}/me", headers=headers)
        if res.status_code == 200:
            profile = res.json()
        elif res.status_code == 401:
            # Try refreshing token once
            try:
                if TOKEN_PATH.exists():
                    with open(TOKEN_PATH, "r") as f:
                        tok = json.load(f)
                    if tok.get("refresh_token"):
                        new_toks = refresh_access_token(tok["refresh_token"])
                        new_tok_val = (new_toks.get("access_token") or "").strip()
                        if new_tok_val:
                            res2 = client.get(f"{GRAPH_BASE_URL}/me", headers={"Authorization": f"Bearer {new_tok_val}"})
                            if res2.status_code == 200:
                                profile = res2.json()
            except Exception as ref_err:
                logger.warning("Token refresh inside get_account_info failed: %s", ref_err)
        else:
            logger.warning("Microsoft Graph /me returned status %s: %s", res.status_code, res.text)

    # Multi-field fallback for personal accounts (@outlook.com, @hotmail.com, or custom Microsoft MSA)
    email = (
        profile.get("mail")
        or profile.get("userPrincipalName")
        or (profile.get("otherMails") and profile.get("otherMails")[0])
        or ""
    )

    # Check cached token claims from OAuth if email is empty or internal ID format
    cached_name = ""
    if TOKEN_PATH.exists():
        try:
            with open(TOKEN_PATH, "r") as f:
                tok_data = json.load(f)
            cached_email = tok_data.get("preferred_username") or tok_data.get("email_claim")
            cached_name = tok_data.get("name_claim") or ""
            if not email or "@" not in email:
                if cached_email:
                    email = cached_email
        except Exception:
            pass

    if not email and not profile:
        raise MicrosoftAuthError("Failed to fetch Microsoft profile and no cached identity found.")

    display_name = (
        profile.get("displayName")
        or cached_name
        or (email.split("@")[0] if "@" in email else "")
        or "Microsoft User"
    )

    return {
        "authenticated": True,
        "email": email,
        "displayName": display_name,
        "id": profile.get("id"),
        "status": "connected",
    }


def disconnect() -> bool:
    """Clear saved Microsoft credentials to disconnect the account."""
    if TOKEN_PATH.exists():
        try:
            TOKEN_PATH.unlink()
            return True
        except Exception as e:
            logger.error("Failed to remove token file: %s", e)
            return False
    return True
