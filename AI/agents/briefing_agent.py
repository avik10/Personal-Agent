"""Morning Briefing & Daily Digest Specialist Agent."""

from langchain_core.tools import StructuredTool
from langgraph.prebuilt import create_react_agent

from agents.base import llm
from tools.briefing_tools import get_daily_briefing

briefing_tools = [
    StructuredTool.from_function(get_daily_briefing),
]

BRIEFING_PROMPT = (
    "You are the Morning Briefing & Daily Digest Specialist Agent. "
    "Your responsibility is to generate an empowering, structured, and comprehensive daily briefing "
    "incorporating current weather conditions, pending to-do tasks, and health/habit metrics using `get_daily_briefing`.\n"
    "Present the summary in an organized, motivating, and fluent English format."
)

briefing_agent = create_react_agent(llm, briefing_tools, prompt=BRIEFING_PROMPT)
