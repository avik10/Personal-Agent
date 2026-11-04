"""Personal AI Assistant - Agent CLI Runner.

Orchestrates 13 specialized agents concurrently:
- GoogleAgent: Real-time Google Workspace data (Gmail, Calendar, Drive, Docs, Tasks) via MCP.
- OutlookAgent: Real-time Microsoft Outlook data (Mailbox, Search, Send, Read/Unread) via Microsoft Graph MCP.
- WeatherAgent: Real-time weather and 5-day forecasts via OpenWeatherMap.
- TaskNotesAgent: Scoped note-taking, to-dos, and reminder management.
- UtilityAgent: Computations, unit conversions, time, system status, file inspection.
- ResearchAgent: Web searches, news headlines, and article summaries.
- FinanceAgent: Expense tracking, category breakdowns, and monthly budget limits.
- HabitHealthAgent: Habit streaks, daily water logging, and workouts.
- BriefingAgent: Morning executive briefings consolidating weather, todos, & health.
- DraftingAgent: Professional email drafting, message polishing, and meeting agendas.
- DevAssistantAgent: Code inspection, syntax checking, git advice, safe execution.
- MemoryRAGAgent: Personal knowledge base for facts, credentials, and cheat-sheets.
- GeneralAgent: Natural, fluent English conversational dialogue.
"""

import sys
from pathlib import Path

# Ensure agent directory is in sys.path
AGENT_DIR = Path(__file__).resolve().parent
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

from config.settings import MODEL_NAME, TEMPERATURE
from core import multi_agent_graph


def run_pipeline(user_input: str) -> str:
    """Run the multi-agent graph pipeline for a single user query."""
    print(f"\n[Supervisor] Analyzing query: '{user_input}'...")
    result = multi_agent_graph.invoke({
        "user_query": user_input,
        "active_agents": [],
        "agent_tasks": {},
        "agent_outputs": {},
        "final_response": "",
    })

    active = result.get("active_agents", [])
    print(f"[Supervisor] Activated Agents ({len(active)}): {', '.join(active)}")
    for agent_name, out in result.get("agent_outputs", {}).items():
        first_line = out.strip().split("\n")[0][:90]
        print(f"  • {agent_name}: {first_line}...")

    final_resp = result.get("final_response", "").strip()
    return final_resp


def interactive_cli():
    """Start interactive command-line interface."""
    print("═" * 74)
    print(" 🚀  LANGGRAPH MULTI-AGENT ORCHESTRATION SYSTEM (12 SPECIALISTS)")
    print("     Agents: Google (MCP) | Weather | TaskNotes | Utility | Research")
    print("             Finance | HabitHealth | Briefing | Drafting | DevAssistant | MemoryRAG")
    print(f"     Backend: {MODEL_NAME} via Ollama (temperature={TEMPERATURE})")
    print("═" * 74)
    print("Type 'exit' or 'quit' to end session.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        try:
            response = run_pipeline(user_input)
            print(f"\nAgent:\n{response}\n")
        except Exception as e:
            print(f"\n[Error] Orchestration failed: {e}\n")


def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:]).strip()
        if query:
            response = run_pipeline(query)
            print(f"\nAgent:\n{response}\n")
            return
    interactive_cli()


if __name__ == "__main__":
    main()
