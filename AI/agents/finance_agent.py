"""Personal Finance & Expense Tracker Specialist Agent."""

from langchain_core.tools import StructuredTool
from langgraph.prebuilt import create_react_agent

from agents.base import llm
from tools.finance_tools import (
    get_expense_summary,
    list_expenses,
    log_expense,
    set_budget,
)

finance_tools = [
    StructuredTool.from_function(log_expense),
    StructuredTool.from_function(get_expense_summary),
    StructuredTool.from_function(list_expenses),
    StructuredTool.from_function(set_budget),
]

FINANCE_PROMPT = (
    "You are the Personal Finance & Expense Tracker Specialist Agent. "
    "Your responsibility is to log user expenses with correct amounts and categories, "
    "summarize spending breakdowns, and monitor monthly budgets using your tools.\n"
    "CRITICAL RULES:\n"
    "1. Whenever the user mentions spending, buying, paying, or costs (e.g. 'spent 500 on dinner', 'bought groceries for 450'), "
    "call `log_expense` with the exact numeric amount and category.\n"
    "2. Always state the recorded amounts and category totals clearly in English."
)

finance_agent = create_react_agent(llm, finance_tools, prompt=FINANCE_PROMPT)
