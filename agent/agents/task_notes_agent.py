"""Task & Notes Specialist Agent."""

from langchain_core.tools import StructuredTool
from langgraph.prebuilt import create_react_agent

from agents.base import llm
from tools.utility_tools import (
    add_todo,
    complete_todo,
    delete_todo,
    list_todos,
    read_notes,
    save_note,
    update_note,
    update_todo,
)

task_notes_tools = [
    StructuredTool.from_function(save_note),
    StructuredTool.from_function(read_notes),
    StructuredTool.from_function(update_note),
    StructuredTool.from_function(add_todo),
    StructuredTool.from_function(list_todos),
    StructuredTool.from_function(update_todo),
    StructuredTool.from_function(complete_todo),
    StructuredTool.from_function(delete_todo),
]

TASK_NOTES_PROMPT = (
    "You are the Task & Notes Specialist Agent. "
    "Your responsibility is to manage notes, to-dos, and scheduled items using your tools.\n\n"
    "CRITICAL NOTE EXTRACTION RULES:\n"
    "1. When the user asks to save, make, or record a note:\n"
    "   - Extract and save ONLY the specific text or task the user explicitly asked to note down "
    "(e.g., 'have to buy bread tomorrow' -> note='Buy bread tomorrow').\n"
    "   - NEVER include weather reports, calculation results, or unrelated context in the note!\n"
    "   - Only the exact note item itself must be saved.\n"
    "2. Always provide your final response in clear, concise English confirming only the note/task action taken."
)

task_notes_agent = create_react_agent(llm, task_notes_tools, prompt=TASK_NOTES_PROMPT)
