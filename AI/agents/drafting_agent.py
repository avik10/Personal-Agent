"""Communication, Email, & Message Drafting Specialist Agent."""

from langchain_core.tools import StructuredTool
from langgraph.prebuilt import create_react_agent

from agents.base import llm
from tools.drafting_tools import (
    draft_email,
    draft_meeting_agenda,
    polish_message,
)

drafting_tools = [
    StructuredTool.from_function(draft_email),
    StructuredTool.from_function(polish_message),
    StructuredTool.from_function(draft_meeting_agenda),
]

DRAFTING_PROMPT = (
    "You are the Communication & Writing Specialist Agent. "
    "Your responsibility is to compose well-structured professional emails, polish rough messages, "
    "and create meeting agendas using your tools.\n"
    "Ensure impeccable grammar, professional and courteous tone, and clear structure. Always reply strictly in English."
)

drafting_agent = create_react_agent(llm, drafting_tools, prompt=DRAFTING_PROMPT)
