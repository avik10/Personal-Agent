"""API Route Modules."""

from .status import router as status_router
from .google import router as google_router
from .outlook import router as outlook_router
from .chat import router as chat_router

__all__ = ["status_router", "google_router", "outlook_router", "chat_router"]
