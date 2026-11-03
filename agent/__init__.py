"""Personal Agent Multi-Agent Framework Package."""

import sys
from pathlib import Path

# Ensure the agent directory is in sys.path so internal imports resolve seamlessly
AGENT_DIR = Path(__file__).resolve().parent
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

# Convenient package exports
from core.graph import multi_agent_graph
from core.state import MultiAgentState
from config.settings import MODEL_NAME, OLLAMA_BASE_URL

__all__ = [
    "multi_agent_graph",
    "MultiAgentState",
    "MODEL_NAME",
    "OLLAMA_BASE_URL",
    "AGENT_DIR",
]
