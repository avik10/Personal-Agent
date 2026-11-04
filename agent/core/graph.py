"""LangGraph Multi-Agent Orchestration Graph.

Coordinates 10 specialized agents and 1 general dialogue agent:
1. WeatherAgent
2. TaskNotesAgent
3. UtilityAgent
4. ResearchAgent
5. FinanceAgent
6. HabitHealthAgent
7. BriefingAgent
8. DraftingAgent
9. DevAssistantAgent
10. MemoryRAGAgent
11. GeneralAgent
"""

from typing import Dict, List
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

from agents import (
    llm,
    clean_agent_output,
    weather_agent,
    task_notes_agent,
    utility_agent,
    research_agent,
    finance_agent,
    habit_agent,
    briefing_agent,
    drafting_agent,
    dev_agent,
    knowledge_agent,
    google_agent,
    outlook_agent,
)
import json
import re

from core.state import MultiAgentState
from core.router import decompose_query


def _format_raw_json_to_readable(raw_text: str, query: str = "") -> str:
    """Detect if output is a raw JSON string or technical dump, and convert to clean Markdown."""
    if not raw_text or not isinstance(raw_text, str):
        return raw_text

    trimmed = raw_text.strip()
    data = None
    if (trimmed.startswith("{") and trimmed.endswith("}")) or (trimmed.startswith("[") and trimmed.endswith("]")):
        try:
            data = json.loads(trimmed)
        except Exception:
            data = None

    # Handle structured email dictionary (e.g. from gmail_get_message)
    if isinstance(data, dict) and ("headers" in data or ("snippet" in data and "id" in data)):
        headers = data.get("headers", {})
        subject = headers.get("Subject") or data.get("subject") or "(No Subject)"
        sender = headers.get("From") or data.get("from") or "Unknown"
        to = headers.get("To") or data.get("to") or ""
        date = headers.get("Date") or data.get("date") or ""
        body = data.get("body") or data.get("snippet") or ""

        # Clean body text
        body = re.sub(r"[\u200b-\u200f\ufeff\u202a-\u202e]", "", body)
        body = body.replace("\u00a0", " ").replace("\r\n", "\n").replace("\r", "\n")
        body = re.sub(r"\n{3,}", "\n\n", body).strip()

        lines = [
            f"### ✉️ {subject}",
            f"**From:** {sender}",
        ]
        if to:
            lines.append(f"**To:** {to}")
        if date:
            lines.append(f"**Date:** {date}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(body if body else "_No body text in this message._")
        return "\n".join(lines)

    # Fallback regex extraction if json.loads failed on escaped email JSON
    if ("headers" in trimmed or "threadId" in trimmed) and ("From" in trimmed or "Subject" in trimmed):
        subj_m = re.search(r'["\']Subject["\']:\s*["\']([^"\']+)["\']', trimmed)
        from_m = re.search(r'["\']From["\']:\s*["\']([^"\']+)["\']', trimmed)
        to_m = re.search(r'["\']To["\']:\s*["\']([^"\']+)["\']', trimmed)
        date_m = re.search(r'["\']Date["\']:\s*["\']([^"\']+)["\']', trimmed)
        body_m = re.search(r'["\']body["\']:\s*["\']((?:\\.|[^"\'])*)["\']', trimmed, re.DOTALL)

        if from_m or subj_m:
            subj = subj_m.group(1) if subj_m else "(No Subject)"
            sender = from_m.group(1) if from_m else "Unknown"
            to_val = to_m.group(1) if to_m else ""
            date_val = date_m.group(1) if date_m else ""
            body_val = body_m.group(1) if body_m else ""
            body_val = body_val.encode('utf-8').decode('unicode_escape', errors='ignore')
            body_val = re.sub(r"[\u200b-\u200f\ufeff\u202a-\u202e]", "", body_val)
            body_val = body_val.replace("\u00a0", " ").replace("\r\n", "\n").replace("\r", "\n")
            body_val = re.sub(r"\n{3,}", "\n\n", body_val).strip()

            lines = [
                f"### ✉️ {subj}",
                f"**From:** {sender}",
            ]
            if to_val:
                lines.append(f"**To:** {to_val}")
            if date_val:
                lines.append(f"**Date:** {date_val}")
            lines.append("")
            lines.append("---")
            lines.append("")
            lines.append(body_val if body_val else "_No body text in this message._")
            return "\n".join(lines)

    # Handle list of emails (e.g. from gmail_search_messages)
    if isinstance(data, list) and data and isinstance(data[0], dict) and "subject" in data[0]:
        lines = ["### 📬 Email Search Results:\n"]
        for idx, item in enumerate(data[:10], 1):
            sub = item.get("subject", "(No Subject)")
            sndr = item.get("from", "Unknown")
            dt = item.get("date", "")
            snip = item.get("snippet", "").strip()
            lines.append(f"{idx}. **{sub}**\n   - **From:** {sndr} {f'({dt})' if dt else ''}\n   - {snip}\n")
        return "\n".join(lines)

    # Handle list of calendar events
    if isinstance(data, list) and data and isinstance(data[0], dict) and ("summary" in data[0] or "start" in data[0]):
        lines = ["### 📅 Scheduled Events:\n"]
        for idx, ev in enumerate(data[:10], 1):
            summary = ev.get("summary", "Event")
            start = ev.get("start", {}).get("dateTime") or ev.get("start", {}).get("date") or ""
            link = ev.get("hangoutLink") or ev.get("htmlLink") or ""
            lines.append(f"{idx}. **{summary}** — {start}")
            if link:
                lines.append(f"   - [Join Meeting]({link})")
        return "\n".join(lines)

    # Handle status dictionary
    if isinstance(data, dict) and "status" in data:
        status = data.get("status")
        to_addr = data.get("to")
        subj = data.get("subject")
        if status == "sent":
            return f"✓ **Email successfully sent!**\n\n- **To:** {to_addr}\n- **Subject:** {subj}"
        return f"**Status:** {status}"

    return raw_text


def _extract_last_content(res_messages: list, fallback_query: str = "") -> str:
    """Extract the last meaningful text content from an agent's message trajectory.
    
    Guarantees that raw ToolMessages are not passed as user responses without human-readable formatting.
    """
    # 1. Prefer substantive AIMessage content
    for msg in reversed(res_messages):
        msg_type = getattr(msg, "type", "")
        if msg_type == "ai":
            content = getattr(msg, "content", None)
            if content and isinstance(content, str) and content.strip():
                cleaned = clean_agent_output(content)
                if cleaned:
                    return _format_raw_json_to_readable(cleaned, fallback_query)

    # 2. If AI message is empty (e.g. only had stripped thought tags), inspect ToolMessages and format
    for msg in reversed(res_messages):
        msg_type = getattr(msg, "type", "")
        if msg_type == "tool":
            content = getattr(msg, "content", None)
            if content and isinstance(content, str) and content.strip():
                return _format_raw_json_to_readable(content, fallback_query)

    return "Action completed."


# ---------------------------------------------------------------------------
# Node Functions
# ---------------------------------------------------------------------------

def supervisor_node(state: MultiAgentState) -> Dict:
    """Analyze query and route to one or more specialized agents concurrently with scoped tasks."""
    query = state.get("user_query", "").strip()
    active, tasks = decompose_query(query)
    return {"active_agents": active, "agent_tasks": tasks}


def weather_node(state: MultiAgentState) -> Dict:
    """Execute Weather Specialist Agent."""
    sub_task = state.get("agent_tasks", {}).get("weather") or state.get("user_query", "")
    try:
        res = weather_agent.invoke({"messages": [HumanMessage(content=sub_task)]})
        output = _extract_last_content(res.get("messages", []))
    except Exception as e:
        output = f"Weather lookup encountered an error: {e}"
    return {"agent_outputs": {"WeatherAgent": output}}


def task_notes_node(state: MultiAgentState) -> Dict:
    """Execute Task & Notes Specialist Agent."""
    sub_task = state.get("agent_tasks", {}).get("task_notes") or state.get("user_query", "")
    try:
        res = task_notes_agent.invoke({"messages": [HumanMessage(content=sub_task)]})
        output = _extract_last_content(res.get("messages", []))
    except Exception as e:
        output = f"Task/Notes operation encountered an error: {e}"
    return {"agent_outputs": {"TaskNotesAgent": output}}


def utility_node(state: MultiAgentState) -> Dict:
    """Execute System Utility & Computation Specialist Agent."""
    sub_task = state.get("agent_tasks", {}).get("utility") or state.get("user_query", "")
    try:
        res = utility_agent.invoke({"messages": [HumanMessage(content=sub_task)]})
        output = _extract_last_content(res.get("messages", []))
    except Exception as e:
        output = f"Utility operation encountered an error: {e}"
    return {"agent_outputs": {"UtilityAgent": output}}


def research_node(state: MultiAgentState) -> Dict:
    """Execute Web Research Specialist Agent."""
    sub_task = state.get("agent_tasks", {}).get("research") or state.get("user_query", "")
    try:
        res = research_agent.invoke({"messages": [HumanMessage(content=sub_task)]})
        output = _extract_last_content(res.get("messages", []))
    except Exception as e:
        output = f"Research lookup encountered an error: {e}"
    return {"agent_outputs": {"ResearchAgent": output}}


def finance_node(state: MultiAgentState) -> Dict:
    """Execute Finance & Expense Specialist Agent."""
    sub_task = state.get("agent_tasks", {}).get("finance") or state.get("user_query", "")
    try:
        res = finance_agent.invoke({"messages": [HumanMessage(content=sub_task)]})
        output = _extract_last_content(res.get("messages", []))
    except Exception as e:
        output = f"Finance operation encountered an error: {e}"
    return {"agent_outputs": {"FinanceAgent": output}}


def habit_node(state: MultiAgentState) -> Dict:
    """Execute Health & Habit Specialist Agent."""
    sub_task = state.get("agent_tasks", {}).get("habit") or state.get("user_query", "")
    try:
        res = habit_agent.invoke({"messages": [HumanMessage(content=sub_task)]})
        output = _extract_last_content(res.get("messages", []))
    except Exception as e:
        output = f"Habit tracking operation encountered an error: {e}"
    return {"agent_outputs": {"HabitHealthAgent": output}}


def briefing_node(state: MultiAgentState) -> Dict:
    """Execute Morning Briefing Specialist Agent."""
    sub_task = state.get("agent_tasks", {}).get("briefing") or state.get("user_query", "")
    try:
        res = briefing_agent.invoke({"messages": [HumanMessage(content=sub_task)]})
        output = _extract_last_content(res.get("messages", []))
    except Exception as e:
        output = f"Briefing generation encountered an error: {e}"
    return {"agent_outputs": {"BriefingAgent": output}}


def drafting_node(state: MultiAgentState) -> Dict:
    """Execute Communication & Drafting Specialist Agent."""
    sub_task = state.get("agent_tasks", {}).get("drafting") or state.get("user_query", "")
    try:
        res = drafting_agent.invoke({"messages": [HumanMessage(content=sub_task)]})
        output = _extract_last_content(res.get("messages", []))
    except Exception as e:
        output = f"Drafting operation encountered an error: {e}"
    return {"agent_outputs": {"DraftingAgent": output}}


def dev_node(state: MultiAgentState) -> Dict:
    """Execute Developer Assistant Specialist Agent."""
    sub_task = state.get("agent_tasks", {}).get("dev") or state.get("user_query", "")
    try:
        res = dev_agent.invoke({"messages": [HumanMessage(content=sub_task)]})
        output = _extract_last_content(res.get("messages", []))
    except Exception as e:
        output = f"Developer assistant encountered an error: {e}"
    return {"agent_outputs": {"DevAssistantAgent": output}}


def knowledge_node(state: MultiAgentState) -> Dict:
    """Execute Personal Knowledge Base Specialist Agent."""
    sub_task = state.get("agent_tasks", {}).get("knowledge") or state.get("user_query", "")
    try:
        res = knowledge_agent.invoke({"messages": [HumanMessage(content=sub_task)]})
        output = _extract_last_content(res.get("messages", []))
    except Exception as e:
        output = f"Knowledge retrieval encountered an error: {e}"
    return {"agent_outputs": {"MemoryRAGAgent": output}}


def google_node(state: MultiAgentState) -> Dict:
    """Execute Google Workspace Specialist Agent (powered by MCP)."""
    sub_task = state.get("agent_tasks", {}).get("google") or state.get("user_query", "")
    try:
        res = google_agent.invoke({"messages": [HumanMessage(content=sub_task)]})
        output = _extract_last_content(res.get("messages", []))
    except Exception as e:
        output = f"Google services operation encountered an error: {e}"
    return {"agent_outputs": {"GoogleAgent": output}}


def outlook_node(state: MultiAgentState) -> Dict:
    """Execute Microsoft Outlook Specialist Agent (powered by MCP)."""
    sub_task = state.get("agent_tasks", {}).get("outlook") or state.get("user_query", "")
    try:
        res = outlook_agent.invoke({"messages": [HumanMessage(content=sub_task)]})
        output = _extract_last_content(res.get("messages", []))
    except Exception as e:
        output = f"Microsoft Outlook operation encountered an error: {e}"
    return {"agent_outputs": {"OutlookAgent": output}}


def general_node(state: MultiAgentState) -> Dict:
    """Execute General Dialogue Agent for non-tool conversations and greetings."""
    sub_task = state.get("agent_tasks", {}).get("general") or state.get("user_query", "")
    prompt = (
        f"You are a friendly, helpful AI Personal Assistant.\n"
        f"User message: {sub_task}\n"
        f"Reply conversationally, briefly, and strictly in English."
    )
    try:
        res = llm.invoke(prompt)
        output = clean_agent_output(res.content)
    except Exception as e:
        # If connection failed (e.g. Ollama refused connection) and Groq is available:
        from config.settings import GROQ_API_KEY
        if GROQ_API_KEY:
            try:
                from agents.groq_llm import get_groq_llm
                cloud_llm = get_groq_llm()
                res = cloud_llm.invoke(prompt)
                output = clean_agent_output(res.content)
            except Exception as fe:
                output = f"Error generating response: {fe}"
        else:
            output = f"Error generating response: {e}"
    return {"agent_outputs": {"GeneralAgent": output}}


def synthesizer_node(state: MultiAgentState) -> Dict:
    """Synthesize outputs from all activated agents into a single coherent response."""
    outputs = state.get("agent_outputs", {})
    query = state.get("user_query", "")

    if not outputs:
        return {"final_response": "I processed your request, but no agents returned output."}

    # If only one agent responded, ensure output is formatted and human-readable
    if len(outputs) == 1:
        single_output = next(iter(outputs.values()))
        return {"final_response": _format_raw_json_to_readable(single_output, query)}

    # If multiple agents ran concurrently, synthesize their outputs cohesively
    combined_context = "\n\n".join(
        f"[{agent_name}]:\n{text}" for agent_name, text in outputs.items()
    )

    synthesis_prompt = (
        f"You are an AI Personal Assistant.\n"
        f"The user asked: '{query}'\n\n"
        f"Multiple specialized agents ran in parallel and provided the following findings:\n"
        f"{combined_context}\n\n"
        f"Synthesize these findings into one clear, cohesive, strictly English response for the user. "
        f"Do not mention agent names, internal workflows, or <think> tags. Provide only the direct answer."
    )

    try:
        res = llm.invoke(synthesis_prompt)
        final_text = clean_agent_output(res.content)
    except Exception:
        final_text = "\n\n".join(outputs.values())

    return {"final_response": final_text}


# ---------------------------------------------------------------------------
# Routing Function (Fan-out)
# ---------------------------------------------------------------------------

def route_agents(state: MultiAgentState) -> List[str]:
    """Return the list of target nodes to activate in parallel."""
    return state.get("active_agents", ["general"])


# ---------------------------------------------------------------------------
# StateGraph Assembly
# ---------------------------------------------------------------------------

workflow = StateGraph(MultiAgentState)

# Add all nodes
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("weather", weather_node)
workflow.add_node("google", google_node)
workflow.add_node("outlook", outlook_node)
workflow.add_node("task_notes", task_notes_node)
workflow.add_node("utility", utility_node)
workflow.add_node("research", research_node)
workflow.add_node("finance", finance_node)
workflow.add_node("habit", habit_node)
workflow.add_node("briefing", briefing_node)
workflow.add_node("drafting", drafting_node)
workflow.add_node("dev", dev_node)
workflow.add_node("knowledge", knowledge_node)
workflow.add_node("general", general_node)
workflow.add_node("synthesizer", synthesizer_node)

# Flow: START -> Supervisor -> Conditional Fan-out -> Synthesizer -> END
workflow.add_edge(START, "supervisor")

all_specialists = [
    "weather",
    "google",
    "outlook",
    "task_notes",
    "utility",
    "research",
    "finance",
    "habit",
    "briefing",
    "drafting",
    "dev",
    "knowledge",
    "general",
]

workflow.add_conditional_edges(
    "supervisor",
    route_agents,
    all_specialists,
)

# Fan-in edges from every specialist to synthesizer
for node_name in all_specialists:
    workflow.add_edge(node_name, "synthesizer")

workflow.add_edge("synthesizer", END)

# Compile graph
multi_agent_graph = workflow.compile()
