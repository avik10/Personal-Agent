#!/usr/bin/env bash

# ==============================================================================
# Personal AI Agent Studio - Unified Single-Command Runner
# Starts Backend (FastAPI), Multi-Agent Engine (LangGraph & MCP), and Frontend (React)
# ==============================================================================
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "================================================================="
echo "   🚀 LAUNCHING PERSONAL AI AGENT STUDIO (ALL-IN-ONE)"
echo "   • Backend & API:     http://localhost:8000"
echo "   • React Studio UI:   http://localhost:8000"
echo "   • Google Workspace:  Gmail, Calendar & Drive MCPs"
echo "   • Multi-Agent Core:  12 Specialized Agents (LangGraph)"
echo "================================================================="

# 1. Check local Ollama LLM
echo "[1/4] Checking Ollama local LLM service..."
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "  ✓ Ollama is online and ready."
else
    echo "  ⚠️ Ollama is not detected on http://localhost:11434."
    echo "     Attempting to launch Ollama in background..."
    ollama serve >/dev/null 2>&1 &
    sleep 2
fi

# 2. Check and build frontend if needed
echo "[2/4] Verifying React frontend production build..."
if [ ! -d "frontend/dist" ] || [ ! -f "frontend/dist/index.html" ]; then
    echo "  Building frontend bundle with Vite..."
    (cd frontend && npm run build)
else
    echo "  ✓ Frontend bundle is ready in frontend/dist."
fi

# 3. Clean any existing process on port 8000
echo "[3/4] Ensuring port 8000 is clear..."
lsof -ti :8000 | xargs kill -9 2>/dev/null || true

# 4. Start the backend server (FastAPI serves API + React SPA)
echo "[4/4] Starting server on http://localhost:8000..."

# Open browser automatically on macOS
(sleep 2 && open http://localhost:8000 2>/dev/null || true) &

# Execute server
exec python3 backend/run.py
