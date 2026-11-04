"""Authentication manager for Google Keep MCP Server."""

import json
import logging
from typing import Optional, Tuple

from .config import (
    GOOGLE_KEEP_APP_PASSWORD,
    GOOGLE_KEEP_EMAIL,
    GOOGLE_KEEP_MASTER_TOKEN,
    KEEP_TOKEN_FILE,
)

logger = logging.getLogger("mcp.google_keep.auth")

_keep_instance = None


class GoogleKeepAuthError(Exception):
    """Raised when Google Keep authentication fails."""
    pass


def get_keep_client():
    """Obtain or restore an authenticated gkeepapi.Keep instance.

    Uses stored master token if available, or authenticates using App Password.
    """
    global _keep_instance

    if _keep_instance is not None:
        return _keep_instance

    try:
        import gkeepapi
    except ImportError:
        raise GoogleKeepAuthError(
            "The 'gkeepapi' package is not installed. Please run:\n"
            "  pip install gkeepapi\n"
            "to enable Google Keep MCP server."
        )

    keep = gkeepapi.Keep()

    # 1. Try restoring from Master Token (fastest, zero password needed)
    token = GOOGLE_KEEP_MASTER_TOKEN
    if not token and KEEP_TOKEN_FILE.exists():
        try:
            with open(KEEP_TOKEN_FILE, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
                token = saved_data.get("master_token")
        except Exception as e:
            logger.warning("Could not read stored Keep master token: %s", e)

    email = GOOGLE_KEEP_EMAIL

    if token and email:
        try:
            keep.resume(email, token)
            _keep_instance = keep
            logger.info("Successfully resumed Google Keep session for %s via master token.", email)
            return _keep_instance
        except Exception as e:
            logger.warning("Failed to resume Keep session with token: %s. Re-authenticating...", e)

    # 2. Authenticate with Google App Password
    password = GOOGLE_KEEP_APP_PASSWORD
    if not password:
        raise GoogleKeepAuthError(
            "Google Keep requires an App Password to access your personal Keep notes.\n"
            "Steps to generate your free Google App Password (takes 30 seconds):\n"
            "  1. Go to: https://myaccount.google.com/apppasswords\n"
            "  2. Sign in with your Google account.\n"
            "  3. Name the app: 'Personal Agent'\n"
            "  4. Click 'Create' and copy the 16-character password (e.g., abcd efgh ijkl mnop)\n"
            "  5. Add to your .env or Render Environment Variables:\n"
            "     GOOGLE_KEEP_APP_PASSWORD=your_16_char_password\n"
            f"     GOOGLE_KEEP_EMAIL={email or 'your-email@gmail.com'}"
        )

    try:
        # Clean password from spaces if pasted with spaces
        clean_pwd = password.replace(" ", "")
        keep.authenticate(email, clean_pwd)

        # Cache master token to disk for persistent zero-auth re-use
        master_token = keep.getMasterToken()
        if master_token:
            KEEP_TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(KEEP_TOKEN_FILE, "w", encoding="utf-8") as f:
                json.dump({"email": email, "master_token": master_token}, f, indent=2)

        _keep_instance = keep
        logger.info("Successfully authenticated with Google Keep for %s.", email)
        return _keep_instance
    except Exception as e:
        raise GoogleKeepAuthError(f"Failed to authenticate with Google Keep: {e}")


def is_keep_authenticated() -> bool:
    """Check if Google Keep has valid credentials or saved token."""
    if _keep_instance is not None:
        return True
    if GOOGLE_KEEP_MASTER_TOKEN or KEEP_TOKEN_FILE.exists() or GOOGLE_KEEP_APP_PASSWORD:
        return True
    return False
