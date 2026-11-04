"""Personal Knowledge Base and Fact Retrieval Tools."""

import json
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from config.settings import KNOWLEDGE_FILE, STORAGE_DIR


def _load_knowledge_data() -> dict:
    if not KNOWLEDGE_FILE.exists():
        return {"entries": []}
    try:
        with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return {"entries": []}
            data.setdefault("entries", [])
            return data
    except Exception:
        return {"entries": []}


def _save_knowledge_data(data: dict) -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


class SaveKnowledgeInput(BaseModel):
    topic: str = Field(description="Brief topic or title, e.g. 'Bike License' or 'WiFi Password'")
    content: str = Field(description="The detailed fact, note, or information to remember")


def save_knowledge(topic: str, content: str) -> str:
    """Save a piece of knowledge, personal fact, or configuration to your personal knowledge base."""
    top = topic.strip()
    cnt = content.strip()
    if not top or not cnt:
        return "Both topic and content are required to save knowledge."

    data = _load_knowledge_data()
    entries = data.setdefault("entries", [])

    existing = next((e for e in entries if e.get("topic", "").lower() == top.lower()), None)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if existing:
        existing["content"] = cnt
        existing["updated_at"] = now_str
        _save_knowledge_data(data)
        return f"Knowledge topic '{top}' updated successfully: '{cnt}'."

    new_id = (max([e.get("id", 0) for e in entries], default=0)) + 1
    new_entry = {
        "id": new_id,
        "topic": top,
        "content": cnt,
        "created_at": now_str,
    }
    entries.append(new_entry)
    _save_knowledge_data(data)
    return f"Saved to knowledge base #{new_id} under '{top}': '{cnt}'."


class SearchKnowledgeInput(BaseModel):
    query: str = Field(description="Keyword or topic to search for in knowledge base")


def search_knowledge(query: str) -> str:
    """Search personal knowledge base by keyword or topic."""
    q = query.strip().lower()
    if not q:
        return "Please provide a search term."

    data = _load_knowledge_data()
    entries = data.get("entries", [])
    if not entries:
        return "Your knowledge base is currently empty."

    terms = q.split()
    matched = []

    for e in entries:
        topic = e.get("topic", "").lower()
        content = e.get("content", "").lower()
        full_text = f"{topic} {content}"

        score = sum(1 for term in terms if term in full_text)
        if score > 0:
            matched.append((score, e))

    matched.sort(key=lambda x: x[0], reverse=True)

    if not matched:
        return f"No knowledge entries found matching '{query}'."

    lines = [f"Found {len(matched)} matching knowledge item(s):"]
    for _, item in matched[:5]:
        lines.append(f"• **{item['topic']}**:\n  {item['content']}")

    return "\n\n".join(lines)


def list_knowledge_topics() -> str:
    """List all topics stored in the personal knowledge base."""
    data = _load_knowledge_data()
    entries = data.get("entries", [])
    if not entries:
        return "Knowledge base is empty."

    lines = ["Stored Knowledge Topics:"]
    for e in entries:
        lines.append(f"  #{e['id']}: {e['topic']}")
    return "\n".join(lines)
