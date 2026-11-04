"""Backward-compatibility shim redirecting to AI package."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import AI
from AI import *

# Proxy submodules
import AI.core as core
import AI.agents as agents
import AI.tools as tools
import AI.config as config
import AI.features.google as mcp_google
import AI.features.microsoft as mcp_outlook

sys.modules["agent.core"] = core
sys.modules["agent.core.graph"] = AI.core.graph
sys.modules["agent.core.router"] = AI.core.router
sys.modules["agent.core.state"] = AI.core.state
sys.modules["agent.agents"] = agents
sys.modules["agent.tools"] = tools
sys.modules["agent.config"] = config
sys.modules["agent.config.settings"] = AI.config.settings
sys.modules["agent.mcp_google"] = mcp_google
sys.modules["agent.mcp_outlook"] = mcp_outlook

__all__ = [
    "multi_agent_graph",
    "MultiAgentState",
    "decompose_query",
    "supervisor_router",
    "MODEL_NAME",
    "LLM_PROVIDER",
    "GROQ_MODEL",
]
