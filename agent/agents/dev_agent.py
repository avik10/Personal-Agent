"""Developer, Code, & Git Assistant Specialist Agent."""

from langchain_core.tools import StructuredTool
from langgraph.prebuilt import create_react_agent

from agents.base import llm
from tools.dev_tools import (
    check_python_syntax,
    git_helper,
    inspect_code,
    run_command_safe,
)

dev_tools = [
    StructuredTool.from_function(inspect_code),
    StructuredTool.from_function(check_python_syntax),
    StructuredTool.from_function(git_helper),
    StructuredTool.from_function(run_command_safe),
]

DEV_PROMPT = (
    "You are the Developer Assistant Specialist Agent. "
    "Your responsibility is to assist with programming tasks, inspecting workspace code files, "
    "validating Python syntax, providing accurate git commands, and executing diagnostic commands using your tools.\n"
    "Be precise, technical, and provide clean code snippets and commands in English."
)

dev_agent = create_react_agent(llm, dev_tools, prompt=DEV_PROMPT)
