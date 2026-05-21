"""Singleton dependencies shared across all route handlers."""

from __future__ import annotations

import threading
from pathlib import Path

from modules.pdf_parser import load_theory_questions
from modules.progress_manager import ProgressManager

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Shared theory / questions — same for every user
# ---------------------------------------------------------------------------

_theory: list[dict] = []
_questions: list[dict] = []
_shared_lock = threading.Lock()
_data_loaded = False


def _ensure_content_loaded() -> None:
    global _theory, _questions, _data_loaded
    if _data_loaded:
        return
    with _shared_lock:
        if _data_loaded:
            return
        t, q = load_theory_questions(ROOT)
        _theory = t
        _questions = q
        _data_loaded = True


def get_theory() -> list[dict]:
    _ensure_content_loaded()
    return _theory


def get_questions() -> list[dict]:
    _ensure_content_loaded()
    return _questions


# ---------------------------------------------------------------------------
# Per-user ProgressManager cache
# ---------------------------------------------------------------------------

_user_pms: dict[str, ProgressManager] = {}
_user_locks: dict[str, threading.Lock] = {}
_registry_lock = threading.Lock()


def get_user_root(username: str) -> Path:
    """Return the base_dir for a given user's ProgressManager.

    ProgressManager appends "data/progress.json" to whatever base_dir it
    receives, so the actual progress file ends up at:
        data/users/{username}/data/progress.json
    """
    return ROOT / "data" / "users" / username


def get_user_lock(username: str) -> threading.Lock:
    with _registry_lock:
        if username not in _user_locks:
            _user_locks[username] = threading.Lock()
        return _user_locks[username]


def get_pm_for_user(username: str) -> ProgressManager:
    """Return (and lazily initialise) a ProgressManager for *username*."""
    _ensure_content_loaded()

    if username in _user_pms:
        return _user_pms[username]

    lock = get_user_lock(username)
    with lock:
        if username in _user_pms:
            return _user_pms[username]

        user_root = get_user_root(username)
        (user_root / "data").mkdir(parents=True, exist_ok=True)

        pm = ProgressManager(user_root)
        pm.load()
        total = len(_theory)
        pm.sync_current_chapter(total)
        pm.save()

        _user_pms[username] = pm
        return pm


# ---------------------------------------------------------------------------
# Backwards-compatible helpers (used by the old global-pm routes during
# the migration; after the ?user= param is wired everywhere these can be
# removed, but they are kept to avoid import errors)
# ---------------------------------------------------------------------------

def get_lock() -> threading.Lock:
    """Return the shared content lock (kept for backwards compat)."""
    return _shared_lock


