"""Pure exam logic — no input() calls, no prints. Used by the API routes."""

from __future__ import annotations

import random
import uuid
from typing import Any

# In-memory store of active exam sessions: exam_id -> list of full question dicts.
# Single-user local app; a dict is sufficient.
_active_exams: dict[str, list[dict[str, Any]]] = {}


def all_questions_flat(questions_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for block in questions_data:
        for q in block.get("questions") or []:
            out.append(q)
    return out


def create_exam(questions_data: list[dict[str, Any]], num_questions: int = 40) -> dict[str, Any]:
    """
    Build a new exam session.

    Returns
    -------
    {
        exam_id: str,
        questions: [stripped question dicts],
        total: int,
        note: str | None   (if bank is too small)
    }
    """
    bank = all_questions_flat(questions_data)
    note: str | None = None

    if len(bank) < num_questions:
        note = (
            f"The question bank has only {len(bank)} items. "
            f"Some questions may repeat to reach {num_questions}."
        )
        sample = [random.choice(bank) for _ in range(num_questions)]
    else:
        sample = random.sample(bank, num_questions)

    exam_id = str(uuid.uuid4())
    _active_exams[exam_id] = sample  # store full (with answers) server-side

    stripped = [
        {k: v for k, v in q.items() if k not in ("correct", "explanation")}
        for q in sample
    ]

    return {"exam_id": exam_id, "questions": stripped, "total": len(sample), "note": note}


def submit_exam(exam_id: str, answers: dict[str, str]) -> dict[str, Any]:
    """
    Grade a submitted exam.

    Parameters
    ----------
    exam_id : returned from create_exam
    answers : { question_id: "A" | "B" | "C" | "D" }

    Returns
    -------
    {
        score: float,
        passed: bool,
        correct_count: int,
        total: int,
        per_question: [{ id, question, chosen, correct, explanation, is_correct }]
    }

    Raises
    ------
    KeyError if exam_id is unknown.
    """
    questions = _active_exams.pop(exam_id)  # consume — one submission per exam

    correct_count = 0
    per_question = []
    for q in questions:
        qid = q.get("id", "")
        chosen = str(answers.get(qid, "")).upper()
        correct = str(q.get("correct", "")).upper()
        is_correct = chosen == correct
        if is_correct:
            correct_count += 1
        per_question.append(
            {
                "id": qid,
                "question": q.get("question", ""),
                "options": q.get("options", {}),
                "image_url": q.get("image_url"),
                "chosen": chosen,
                "correct": correct,
                "explanation": q.get("explanation"),
                "is_correct": is_correct,
            }
        )

    total = len(questions)
    score = (correct_count / total * 100.0) if total else 0.0
    return {
        "score": round(score, 1),
        "passed": score >= 65.0,
        "correct_count": correct_count,
        "total": total,
        "per_question": per_question,
    }
