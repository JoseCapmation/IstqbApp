"""Routes: /api/chapters/{id}/quiz and /api/chapters/{id}/quiz/submit."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.deps import get_pm_for_user, get_questions, get_theory, get_user_lock
from backend.services.quiz_service import (
    prepare_quiz_pool,
    score_answers,
    select_quiz_questions,
    strip_answers,
)

router = APIRouter()

# Map (username, chapter_id) -> selected questions for the active quiz session.
_active_quizzes: dict[tuple[str, int], list[dict]] = {}


class QuizResponse(BaseModel):
    chapter_id: int
    questions: list[dict]
    total: int


class SubmitBody(BaseModel):
    answers: dict[str, str]


class QuizResult(BaseModel):
    score: float
    passed: bool
    correct_count: int
    total: int
    per_question: list[dict]
    chapter_completed: bool


def _find_chapter(chapter_id: int) -> dict:
    theory = get_theory()
    ch = next((c for c in theory if c.get("id") == chapter_id), None)
    if ch is None:
        raise HTTPException(status_code=404, detail=f"Chapter {chapter_id} not found")
    return ch


@router.get("/api/chapters/{chapter_id}/quiz", response_model=QuizResponse)
def get_quiz(chapter_id: int, user: str = Query(...)) -> QuizResponse:
    ch = _find_chapter(chapter_id)
    questions_data = get_questions()
    pool = prepare_quiz_pool(ch, questions_data)
    if not pool:
        raise HTTPException(status_code=404, detail="No questions available for this chapter")
    selected = select_quiz_questions(pool)
    _active_quizzes[(user, chapter_id)] = selected
    return QuizResponse(
        chapter_id=chapter_id,
        questions=strip_answers(selected),
        total=len(selected),
    )


@router.post("/api/chapters/{chapter_id}/quiz/submit", response_model=QuizResult)
def submit_quiz(chapter_id: int, body: SubmitBody, user: str = Query(...)) -> QuizResult:
    _find_chapter(chapter_id)
    questions = _active_quizzes.get((user, chapter_id))
    if questions is None:
        raise HTTPException(
            status_code=400,
            detail="No active quiz for this chapter — call GET /quiz first",
        )

    result = score_answers(questions, body.answers)
    chapter_completed = False

    if result["passed"]:
        pm = get_pm_for_user(user)
        theory = get_theory()
        lock = get_user_lock(user)
        with lock:
            pm.complete_chapter(chapter_id, result["score"], len(theory))
            pm.save()
        chapter_completed = True
        _active_quizzes.pop((user, chapter_id), None)

    return QuizResult(
        score=result["score"],
        passed=result["passed"],
        correct_count=result["correct_count"],
        total=result["total"],
        per_question=result["per_question"],
        chapter_completed=chapter_completed,
    )
