"""Multi-Agent State Definition for LangGraph."""

import operator
from typing import Annotated, Dict, List, TypedDict


class MultiAgentState(TypedDict):
    """Shared state dictionary representing the lifecycle of a multi-agent orchestration pass."""
    user_query: str
    active_agents: List[str]
    agent_tasks: Dict[str, str]
    agent_outputs: Annotated[Dict[str, str], operator.ior]
    final_response: str
