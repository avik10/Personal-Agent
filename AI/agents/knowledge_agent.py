"""Personal Knowledge Base & Fact Retrieval Specialist Agent."""

from langchain_core.tools import StructuredTool
from langgraph.prebuilt import create_react_agent

from agents.base import llm
from tools.knowledge_tools import (
    SaveKnowledgeInput,
    SearchKnowledgeInput,
    list_knowledge_topics,
    save_knowledge,
    search_knowledge,
)

knowledge_tools = [
    StructuredTool.from_function(
        save_knowledge,
        args_schema=SaveKnowledgeInput,
        description="Save a piece of personal knowledge or fact given topic and content."
    ),
    StructuredTool.from_function(
        search_knowledge,
        args_schema=SearchKnowledgeInput,
        description="Search personal knowledge base by keyword or topic."
    ),
    StructuredTool.from_function(
        list_knowledge_topics,
        description="List all topics stored in the personal knowledge base."
    ),
]

KNOWLEDGE_PROMPT = (
    "You are the Personal Knowledge & Memory Specialist Agent. "
    "Your responsibility is to store important personal facts, documents, configurations, "
    "and cheat-sheets in your knowledge base using `save_knowledge`, and accurately retrieve them using `search_knowledge`.\n"
    "CRITICAL RULES:\n"
    "1. When asked to remember or save information, call `save_knowledge(topic='...', content='...')`.\n"
    "2. When asked to recall or search information, call `search_knowledge(query='...')`.\n"
    "3. Always report facts accurately, concisely, and strictly in English."
)

knowledge_agent = create_react_agent(llm, knowledge_tools, prompt=KNOWLEDGE_PROMPT)
