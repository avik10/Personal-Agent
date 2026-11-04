"""Microsoft Outlook MCP Feature Bucket (Mail, Microsoft Graph, Entra ID OAuth)."""

from .auth import (
    is_authenticated,
    get_account_info,
    get_authorization_url,
    exchange_code_for_token,
    disconnect,
    MicrosoftAuthError,
)
from .config import (
    AUTH_ENDPOINT,
    DEFAULT_SCOPES,
    GRAPH_BASE_URL,
    MICROSOFT_CLIENT_ID,
    MICROSOFT_CLIENT_SECRET,
    MICROSOFT_REDIRECT_URI,
    MICROSOFT_TENANT_ID,
    TOKEN_ENDPOINT,
    TOKEN_PATH,
)

__all__ = [
    "is_authenticated",
    "get_account_info",
    "get_authorization_url",
    "exchange_code_for_token",
    "disconnect",
    "MicrosoftAuthError",
    "AUTH_ENDPOINT",
    "DEFAULT_SCOPES",
    "GRAPH_BASE_URL",
    "MICROSOFT_CLIENT_ID",
    "MICROSOFT_CLIENT_SECRET",
    "MICROSOFT_REDIRECT_URI",
    "MICROSOFT_TENANT_ID",
    "TOKEN_ENDPOINT",
    "TOKEN_PATH",
]
