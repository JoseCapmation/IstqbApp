"""Routes: /api/state and /api/progress/reset."""

from __future__ import annotations

from fastapi import APIRouter, Query
from pydantic import BaseModel

from backend.deps import get_pm_for_user, get_theory, get_user_lock

router = APIRouter()


class StateResponse(BaseModel):
    total_chapters: int
    current_chapter: int
    completed_chapters: list[int]
    scores_per_chapter: dict[str, float]
    last_exam: dict | None
    all_done: bool


@router.get("/api/state", response_model=StateResponse)
def get_state(user: str = Query(...)) -> StateResponse:
    pm = get_pm_for_user(user)
    theory = get_theory()
    total = len(theory)
    last_exam = pm.state.exam_attempts[-1] if pm.state.exam_attempts else None
    return StateResponse(
        total_chapters=total,
        current_chapter=pm.state.current_chapter,
        completed_chapters=pm.state.completed_chapters,
        scores_per_chapter=pm.state.scores_per_chapter,
        last_exam=last_exam,
        all_done=pm.all_chapters_done(total),
    )


@router.post("/api/progress/reset")
def reset_progress(user: str = Query(...)) -> dict:
    pm = get_pm_for_user(user)
    theory = get_theory()
    lock = get_user_lock(user)
    with lock:
        pm.reset_all_progress()
        pm.sync_current_chapter(len(theory))
        pm.save()
    return {"ok": True}
