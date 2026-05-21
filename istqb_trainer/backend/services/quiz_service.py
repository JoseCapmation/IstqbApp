"""Pure quiz logic — no input() calls, no prints. Used by the API routes."""

from __future__ import annotations

import random
from typing import Any


def get_chapter_questions(questions_data: list[dict[str, Any]], chapter_id: int) -> list[dict[str, Any]]:
    for block in questions_data:
        if block.get("chapter_id") == chapter_id:
            return list(block.get("questions") or [])
    return []


def prepare_quiz_pool(
    chapter: dict[str, Any],
    questions_data: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return a shuffled pool for a chapter, padding to at least 3 if thin."""
    cid = int(chapter["id"])
    pool = get_chapter_questions(questions_data, cid)
    random.shuffle(pool)

    if len(pool) < 3:
        dup = list(pool)
        random.shuffle(dup)
        while len(pool) < 3 and dup:
            pool.append(dup.pop() if dup else pool[0])

    return pool


def select_quiz_questions(pool: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Pick 3–5 questions from the pool."""
    n = min(random.randint(3, 5), len(pool))
    return random.sample(pool, n) if len(pool) >= n else list(pool)


def strip_answers(questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return questions with 'correct' and 'explanation' removed (for client)."""
    result = []
    for q in questions:
        stripped = {k: v for k, v in q.items() if k not in ("correct", "explanation")}
        result.append(stripped)
    return result


def score_answers(
    questions: list[dict[str, Any]],
    answers: dict[str, str],
) -> dict[str, Any]:
    """
    Grade submitted answers.

    Parameters
    ----------
    questions : full question dicts (with 'correct' and 'explanation')
    answers   : { question_id: "A" | "B" | "C" | "D" }

    Returns
    -------
    {
        score: float (0-100),
        passed: bool,
        correct_count: int,
        total: int,
        per_question: [{ id, question, chosen, correct, explanation, is_correct }]
    }
    """
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
        "passed": score >= 70.0,
        "correct_count": correct_count,
        "total": total,
        "per_question": per_question,
    }
