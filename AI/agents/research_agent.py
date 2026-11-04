"""Research & Live Web Specialist Agent."""

from langchain_core.tools import StructuredTool
from langgraph.prebuilt import create_react_agent

from agents.base import llm
from tools.research_tools import fetch_news, summarize_url, web_search

research_tools = [
    StructuredTool.from_function(web_search),
    StructuredTool.from_function(fetch_news),
    StructuredTool.from_function(summarize_url),
]

RESEARCH_PROMPT = (
    "You are the Web Research & News Specialist Agent. "
    "Your responsibility is to search the web, fetch news headlines, and read web pages "
    "to provide accurate, up-to-date, fact-checked answers.\n"
    "Always provide your final response in clear, concise English with citations when available."
)

research_agent = create_react_agent(llm, research_tools, prompt=RESEARCH_PROMPT)
