"""Task & Notes Specialist Agent with Google Workspace Cloud & Local Storage."""

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
from mcp_google.services.tasks import (
    tasks_create_task,
    tasks_list_tasks,
    tasks_complete_task,
    tasks_delete_task,
)
from mcp_google.services.keep import (
    keep_create_note,
    keep_list_notes,
    keep_delete_note,
)

task_notes_tools = [
    # Google Workspace Cloud Notes & Tasks (Google Keep / Google Tasks)
    StructuredTool.from_function(
        keep_create_note,
        name="google_create_note_or_task",
        description="Create a note or task in Google Keep/Tasks cloud storage. Saves title and optional notes body.",
    ),
    StructuredTool.from_function(
        keep_list_notes,
        name="google_list_notes_or_tasks",
        description="List all notes and tasks from Google Keep and Google Tasks cloud. Shows active and completed items.",
    ),
    StructuredTool.from_function(
        tasks_complete_task,
        name="google_complete_task",
        description="Mark a task as completed in Google Tasks.",
    ),
    StructuredTool.from_function(
        keep_delete_note,
        name="google_delete_note_or_task",
        description="Delete a note or task from Google Keep or Google Tasks.",
    ),
    # Local Storage fallback
    StructuredTool.from_function(
        save_note,
        name="local_save_note",
        description="Save a note to local disk storage.",
    ),
    StructuredTool.from_function(
        read_notes,
        name="local_read_notes",
        description="Read notes from local disk storage.",
    ),
    StructuredTool.from_function(
        update_note,
        name="local_update_note",
        description="Update a note in local disk storage.",
    ),
    StructuredTool.from_function(
        add_todo,
        name="local_add_todo",
        description="Add a todo item to local disk storage.",
    ),
    StructuredTool.from_function(
        list_todos,
        name="local_list_todos",
        description="List todo items from local disk storage.",
    ),
    StructuredTool.from_function(
        complete_todo,
        name="local_complete_todo",
        description="Mark a todo item as completed in local storage.",
    ),
    StructuredTool.from_function(
        delete_todo,
        name="local_delete_todo",
        description="Delete a todo item from local storage.",
    ),
]

TASK_NOTES_PROMPT = (
    "You are the Task & Notes Specialist Agent.\n"
    "You support both Google Workspace Cloud Notes (Google Keep / Tasks) and local storage.\n\n"
    "ROUTING & PREFERENCE RULES:\n"
    "1. When the user asks to save, view, complete, or manage notes or tasks:\n"
    "   - By default, PREFER saving to Google Cloud using `google_create_note_or_task` or `google_list_notes_or_tasks` "
    "so the user can access their notes across Google Keep, Google Calendar, and mobile devices.\n"
    "   - If the Google tool indicates authentication is needed or if the user explicitly specifies 'local', "
    "use the local storage tools (`local_save_note`, `local_add_todo`, etc.).\n\n"
    "CRITICAL NOTE EXTRACTION RULES:\n"
    "1. When the user asks to save or record a note or task:\n"
    "   - Extract and save ONLY the specific content the user explicitly asked to note down "
    "(e.g., 'remind me to buy groceries tomorrow' -> title='Buy groceries', due_date='tomorrow').\n"
    "   - NEVER include unrelated context, weather forecasts, or conversational filler inside the note.\n"
    "2. Always provide your final response in clear, concise English confirming the exact action taken."
)

task_notes_agent = create_react_agent(llm, task_notes_tools, prompt=TASK_NOTES_PROMPT)
