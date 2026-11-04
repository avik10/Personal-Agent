"""Google Workspace MCP Feature Bucket (Gmail, Drive, Calendar, Docs, Tasks, Keep)."""

from .auth import is_authenticated, get_account_info
from .config import CREDENTIALS_PATH, TOKEN_PATH, DEFAULT_SCOPES

__all__ = [
    "is_authenticated",
    "get_account_info",
    "CREDENTIALS_PATH",
    "TOKEN_PATH",
    "DEFAULT_SCOPES",
]
