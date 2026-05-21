"""Routes: /api/users — user registry (no passwords)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.deps import ROOT, get_user_root, _registry_lock

router = APIRouter()

USERS_FILE = ROOT / "data" / "users" / "users.json"
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_\-]{1,32}$")


def _read_registry() -> dict:
    if not USERS_FILE.exists():
        return {}
    return json.loads(USERS_FILE.read_text(encoding="utf-8"))


def _write_registry(data: dict) -> None:
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


class CreateUserBody(BaseModel):
    username: str


@router.get("/api/users")
def list_users() -> dict:
    registry = _read_registry()
    return {"users": list(registry.keys())}


@router.get("/api/users/{username}")
def check_user(username: str) -> dict:
    registry = _read_registry()
    return {"exists": username in registry}


@router.post("/api/users", status_code=201)
def create_user(body: CreateUserBody) -> dict:
    username = body.username.strip()

    if not USERNAME_RE.match(username):
        raise HTTPException(
            status_code=422,
            detail="Username must be 1–32 characters: letters, digits, underscores, hyphens only.",
        )

    with _registry_lock:
        registry = _read_registry()
        if username in registry:
            raise HTTPException(status_code=409, detail=f"User '{username}' already exists.")

        registry[username] = {"created": datetime.now(timezone.utc).isoformat()}
        _write_registry(registry)

    # Ensure the user's progress directory exists.
    # ProgressManager looks for <user_root>/data/progress.json, so we need
    # the data/ subdirectory to exist.
    user_root = get_user_root(username)
    (user_root / "data").mkdir(parents=True, exist_ok=True)

    return {"ok": True, "username": username}
