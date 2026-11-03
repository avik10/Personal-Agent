"""FastAPI Backend Application Entrypoint."""

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .routes import status_router, google_router, chat_router

app = FastAPI(
    title="Personal AI Agent Backend",
    description="FastAPI service powering the 12-specialist multi-agent studio and Google Workspace MCP integration.",
    version="2.0.0",
)

# Configure CORS for local development and web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(status_router)
app.include_router(google_router)
app.include_router(chat_router)

# Locate frontend dist directory
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"

# Mount frontend compiled assets if available
if FRONTEND_DIST.exists() and (FRONTEND_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/")
    async def serve_spa_root():
        index_file = FRONTEND_DIST / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Frontend build index.html not found"}

    @app.get("/{full_path:path}")
    async def serve_spa_fallback(full_path: str):
        # Exclude API endpoints from SPA fallback
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        index_file = FRONTEND_DIST / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        raise HTTPException(status_code=404, detail="Frontend not found")
else:
    @app.get("/")
    def root():
        return {
            "message": "Personal AI Agent API is running.",
            "docs": "/docs",
            "status": "/api/status",
        }
