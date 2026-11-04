"""Chat Endpoint executing LangGraph Multi-Agent pipeline."""

import asyncio
from fastapi import APIRouter, HTTPException

try:
    from AI import multi_agent_graph
except ImportError:
    from agent import multi_agent_graph
from ..schemas import ChatQueryRequest, ChatQueryResponse

router = APIRouter(tags=["Chat"])


@router.post("/api/chat", response_model=ChatQueryResponse)
async def chat_endpoint(payload: ChatQueryRequest):
    """Execute user query across the multi-agent graph asynchronously."""
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    def run_graph():
        return multi_agent_graph.invoke({
            "user_query": query,
            "active_agents": [],
            "agent_tasks": {},
            "agent_outputs": {},
            "final_response": "",
        })

    try:
        result = await asyncio.to_thread(run_graph)
        return ChatQueryResponse(
            query=query,
            response=result.get("final_response", ""),
            active_agents=result.get("active_agents", []),
            agent_outputs=result.get("agent_outputs", {}),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution error: {str(e)}")
