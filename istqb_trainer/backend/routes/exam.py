"""Routes: /api/exam and /api/exam/submit."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.deps import get_pm_for_user, get_questions, get_user_lock
from backend.services.exam_service import create_exam, submit_exam

router = APIRouter()


class ExamResponse(BaseModel):
    exam_id: str
    questions: list[dict]
    total: int
    note: str | None = None


class SubmitBody(BaseModel):
    exam_id: str
    answers: dict[str, str]


class ExamResult(BaseModel):
    score: float
    passed: bool
    correct_count: int
    total: int
    per_question: list[dict]


@router.get("/api/exam", response_model=ExamResponse)
def get_exam(user: str = Query(...)) -> ExamResponse:  # noqa: ARG001
    questions_data = get_questions()
    result = create_exam(questions_data, num_questions=40)
    return ExamResponse(**result)


@router.post("/api/exam/submit", response_model=ExamResult)
def submit_exam_route(body: SubmitBody, user: str = Query(...)) -> ExamResult:
    try:
        result = submit_exam(body.exam_id, body.answers)
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid or expired exam_id")

    pm = get_pm_for_user(user)
    lock = get_user_lock(user)
    with lock:
        pm.record_exam(result["score"], result["passed"])
        pm.save()

    return ExamResult(**result)
