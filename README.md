# Personal AI Agent - 3-Tier Multi-Agent Studio

An enterprise-grade, local Multi-Agent Personal Assistant orchestrating 12 specialized agents concurrently using **LangGraph**, **Ollama** (`qwen3.5:8b`), and **Model Context Protocol (MCP)** for Google Workspace, segregated into 3 clean, maintainable directories.

---

## 🏛 3-Tier Directory Architecture

```
Personal Agent/
├── frontend/                          # ONLY React & Frontend code
│   ├── src/
│   │   ├── features/google/          # Google Workspace Bucket (Gmail, Calendar, Drive views & modal)
│   │   ├── components/               # Sidebar (Capabilities Guide), Header, ChatArea, InputBar
│   │   ├── App.jsx                   # Multi-view router (Chat Studio ⇄ Google Bucket)
│   │   ├── main.jsx                  # React DOM entry
│   │   └── index.css                 # Dark theme & styling
│   ├── dist/                         # Compiled production bundle
│   ├── package.json                  # Frontend dependencies
│   ├── vite.config.js                # Vite build config
│   └── index.html                    # Single page HTML entry
│
├── backend/                           # ONLY FastAPI Backend Server & Endpoints
│   ├── app/
│   │   ├── __init__.py               # Path configurations
│   │   ├── main.py                   # FastAPI application, CORS & static frontend SPA mounting
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py               # POST /api/chat (LangGraph multi-agent execution)
│   │   │   ├── google.py             # GET/POST /api/google/* (Gmail, Calendar, Drive)
│   │   │   └── status.py             # GET /api/status, GET /api/agents
│   │   └── schemas.py                # Pydantic models (ChatQueryRequest, SendEmail, CreateEvent)
│   ├── run.py                        # Backend launcher script (runs on http://localhost:8000)
│   └── requirements.txt              # FastAPI, uvicorn, pydantic dependencies
│
├── agent/                             # ONLY Agent & MCP Framework Code
│   ├── __init__.py                   # Package exports (multi_agent_graph, MultiAgentState)
│   ├── runner.py                     # Command-line agent interface (CLI execution)
│   ├── agents/                       # 12 Specialized ReAct Agents
│   │   ├── google_agent.py           # Google Workspace MCP Agent
│   │   ├── weather_agent.py          # Weather Specialist (OpenWeatherMap)
│   │   ├── task_notes_agent.py       # Tasks & Notes Specialist
│   │   ├── utility_agent.py          # Math & Utility Specialist
│   │   ├── research_agent.py         # Web Research Specialist
│   │   ├── finance_agent.py          # Finance & Expense Specialist
│   │   ├── habit_agent.py            # Habits & Health Specialist
│   │   ├── briefing_agent.py         # Morning Briefing Specialist
│   │   ├── drafting_agent.py         # Writing & Drafting Specialist
│   │   ├── dev_agent.py              # Developer Assistant Specialist
│   │   ├── knowledge_agent.py        # Knowledge & RAG Specialist
│   │   └── base.py                   # ChatOllama client
│   ├── core/                         # LangGraph Orchestration Engine
│   │   ├── state.py                  # MultiAgentState TypedDict
│   │   ├── router.py                 # Query decomposition & intent fan-out router
│   │   ├── synthesizer.py            # Cross-agent answer synthesis
│   │   └── graph.py                  # Compiled StateGraph (Supervisor -> Fan-out -> Synthesizer)
│   ├── tools/                        # 26 LangChain StructuredTools
│   │   ├── google_mcp_tools.py       # Google MCP Tool Bridge
│   │   ├── weather_tools.py          # OpenWeatherMap tools
│   │   └── ...                       # Finance, Habit, Dev, Knowledge, Utility tools
│   ├── mcp_google/                   # Google Workspace MCP Server Package
│   │   ├── auth.py                   # OAuth token management & thread-local isolation
│   │   ├── server.py                 # FastMCP server definition
│   │   ├── setup_auth.py             # Google OAuth desktop browser consent flow
│   │   └── services/                 # Gmail, Calendar, Drive, Docs, Tasks tools
│   ├── config/                       # Settings, prompts & environment paths
│   ├── instructions/                 # Agent operational rules & prompts
│   ├── storage/                      # Local JSON/log storage & Google credentials
│   └── requirements.txt              # Agent dependencies (langchain, langgraph, mcp, etc.)
│
├── main.py                            # Root CLI forwarder
├── start.sh                           # One-click startup script
└── README.md
```

---

## 🚀 Quick Start

### 1. Start the Complete Studio (Backend + Frontend)
```bash
./start.sh
# or
python3 backend/run.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser. The FastAPI server serves both the REST API and the compiled React SPA.

### 2. Run the Agent in Terminal (CLI Mode)
```bash
python3 agent/runner.py "What is the weather in Mumbai and check my calendar"
# or from root
python3 main.py "What is the weather in Mumbai and check my calendar"
```

### 3. Google Workspace Account Authorization (One-Time)
```bash
python3 -m agent.mcp_google setup_auth
```
Tokens are saved securely in `agent/storage/google_credentials/token.json` and auto-refreshed in the background.

---

## 🛠 Features

1. **Frontend (`frontend/`)**:
   - Clean, modern Gemini & ChatGPT aesthetic.
   - Dedicated **Chat Studio** with clean chatbox.
   - Non-clickable **Agent Capabilities Guide** in the left panel.
   - Dedicated **Google Workspace Bucket** page with **Gmail**, **Calendar**, and **Drive** views and in-page Google Account connection.
2. **Backend (`backend/`)**:
   - Modular FastAPI architecture with separated routes for chat, status, and Google Workspace.
   - Asynchronous thread pool execution of LangGraph workflows.
   - Serves static assets and SPA fallback from `frontend/dist`.
3. **Agent (`agent/`)**:
   - 12 specialist ReAct agents orchestrated by LangGraph supervisor.
   - Model Context Protocol (MCP) server for Google Workspace (Gmail, Calendar, Drive, Docs, Tasks).
   - Thread-local API clients preventing memory corruption and race conditions in concurrent multi-agent executions.
