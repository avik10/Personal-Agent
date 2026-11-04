"""System Utility & Computation Specialist Agent."""

from langchain_core.tools import StructuredTool
from langgraph.prebuilt import create_react_agent

from agents.base import llm
from tools.utility_tools import (
    calculate,
    convert_units,
    days_until,
    fetch_url_text,
    get_current_time,
    get_system_status,
    list_files,
    read_file_content,
)

utility_tools = [
    StructuredTool.from_function(calculate),
    StructuredTool.from_function(convert_units),
    StructuredTool.from_function(get_current_time),
    StructuredTool.from_function(days_until),
    StructuredTool.from_function(get_system_status),
    StructuredTool.from_function(list_files),
    StructuredTool.from_function(read_file_content),
    StructuredTool.from_function(fetch_url_text),
]

UTILITY_PROMPT = (
    "You are the System Utility & Computation Specialist Agent. "
    "Your responsibility is to perform math calculations, unit conversions, date/time lookups, "
    "and file reading operations using your tools. "
    "Always provide your final response in clear, concise English."
)

utility_agent = create_react_agent(llm, utility_tools, prompt=UTILITY_PROMPT)
