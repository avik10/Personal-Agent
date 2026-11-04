"""Health, Habit, & Fitness Specialist Agent."""

from langchain_core.tools import StructuredTool
from langgraph.prebuilt import create_react_agent

from agents.base import llm
from tools.habit_tools import (
    get_habit_status,
    log_habit,
    log_water,
    log_workout,
)

habit_tools = [
    StructuredTool.from_function(log_habit),
    StructuredTool.from_function(log_water),
    StructuredTool.from_function(log_workout),
    StructuredTool.from_function(get_habit_status),
]

HABIT_PROMPT = (
    "You are the Health, Habit, & Fitness Specialist Agent. "
    "Your responsibility is to track daily habits, streaks, water intake, and workouts using your tools.\n"
    "CRITICAL RULES:\n"
    "1. When the user reports drinking water (e.g. 'drank 500ml water' or '2L water'), convert to ml if needed and call `log_water`.\n"
    "2. When the user reports an exercise or workout (e.g. 'gym for 40 mins', 'running for 30m'), call `log_workout`.\n"
    "3. When the user completes a habit (e.g. 'finished reading today'), call `log_habit`.\n"
    "4. Always confirm the action, report streaks, and provide encouraging, positive English responses."
)

habit_agent = create_react_agent(llm, habit_tools, prompt=HABIT_PROMPT)
