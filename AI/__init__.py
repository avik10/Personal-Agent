"""Personal Agent Multi-Agent Framework Package (AI)."""

import sys
from pathlib import Path

# Ensure the AI directory and project root are in sys.path
AI_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = AI_DIR.parent
if str(AI_DIR) not in sys.path:
    sys.path.insert(0, str(AI_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Convenient package exports
from core.graph import multi_agent_graph
from core.state import MultiAgentState
from core.router import decompose_query, supervisor_router
from config.settings import MODEL_NAME, LLM_PROVIDER, GROQ_MODEL

__all__ = [
    "multi_agent_graph",
    "MultiAgentState",
    "decompose_query",
    "supervisor_router",
    "MODEL_NAME",
    "LLM_PROVIDER",
    "GROQ_MODEL",
    "AI_DIR",
]
