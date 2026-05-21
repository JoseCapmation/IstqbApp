"""FastAPI application for ISTQB Trainer Web UI."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.routes import auth, chapters, exam, quiz, state

_DIAGRAMS_DIR = Path(__file__).resolve().parent.parent / "data" / "diagrams"

app = FastAPI(title="ISTQB Trainer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(state.router)


_MIME = {".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg"}

@app.get("/api/diagrams/{filename}")
def get_diagram(filename: str) -> FileResponse:
    """Serve diagram files (SVG/PNG/JPG) stored in data/diagrams/."""
    safe_name = Path(filename).name  # strip any path traversal
    path = _DIAGRAMS_DIR / safe_name
    mime = _MIME.get(path.suffix.lower())
    if not path.exists() or not mime:
        raise HTTPException(status_code=404, detail="Diagram not found")
    return FileResponse(str(path), media_type=mime)
app.include_router(chapters.router)
app.include_router(quiz.router)
app.include_router(exam.router)

# Serve the built React frontend if it exists (production mode).
_FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if _FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=str(_FRONTEND_DIST), html=True), name="frontend")
