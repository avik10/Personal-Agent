# Personal AI Agent - React Studio Frontend

A modern React frontend for the Personal AI Agent system inspired by the latest **Google Gemini** and **ChatGPT** user interfaces.

---

## 🎨 Design & Key Features

- **Gemini Aesthetic**: Space charcoal theme (`#0e0e11`), glowing purple/blue gradients, glassmorphism panels, and smooth typography with *Plus Jakarta Sans*.
- **Google Workspace Live Status**: Shows connection status and email badge (`avik.bhattacharjya28@gmail.com`) for Gmail, Google Calendar, Google Drive, Docs, and Tasks.
- **12 Specialized Agents Inspection**: Real-time display of which agents responded (e.g. `GoogleAgent (MCP)`, `WeatherAgent`), plus an expandable orchestration drawer revealing raw sub-agent outputs before synthesis.
- **Quick Action Pills**: One-click prompt chips for Gmail, Calendar, Drive, Weather, and Expenses.
- **Persistent Chat History**: Local storage integration saving conversation threads with instant creation and deletion.
- **Auto-expanding Floating Input**: Bottom capsule bar with keyboard shortcuts (`Enter` to send, `Shift+Enter` for multiline).

---

## 🚀 Running the UI

### Option 1: One-Click Launcher (Recommended)
From the project root:
```bash
./start_ui.sh
```

### Option 2: Running Separately

**1. Start Backend API:**
```bash
python3 api_server.py
# Runs on http://localhost:8000
```

**2. Start React Frontend:**
```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```
Open **http://localhost:5173** in your browser.
