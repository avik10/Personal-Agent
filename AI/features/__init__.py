"""Features module segregating Google Workspace, Microsoft Outlook, and Productivity buckets."""

from . import google
from . import microsoft
from . import productivity

__all__ = ["google", "microsoft", "productivity"]
