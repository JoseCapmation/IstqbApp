"""Practice quiz: 3–5 MCQs, immediate feedback, 70% to pass."""

from __future__ import annotations

import random
from typing import Any

from modules.ai_generator import generate_extra_questions
from utils.helpers import print_header, read_choice_letter


def _get_chapter_questions(questions_data: list[dict[str, Any]], chapter_id: int) -> list[dict[str, Any]]:
    for block in questions_data:
        if block.get("chapter_id") == chapter_id:
            return list(block.get("questions") or [])
    return []


def _prepare_pool(
    chapter: dict[str, Any],
    questions_data: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    cid = int(chapter["id"])
    pool = _get_chapter_questions(questions_data, cid)
    random.shuffle(pool)

    need_more = max(0, 5 - len(pool))
    if need_more > 0:
        excerpt = "\n\n".join(chapter.get("content_chunks") or [])[:8000]
        extra = generate_extra_questions(
            chapter.get("title", "Chapter"),
            excerpt,
            need_more,
            cid,
            start_index=len(pool) + 1,
        )
        pool.extend(extra)

    if len(pool) < 3:
        # Still thin: duplicate shuffled copies as last resort (same chapter bank)
        dup = list(pool)
        random.shuffle(dup)
        while len(pool) < 3 and dup:
            pool.append(dup.pop() if dup else pool[0])

    return pool


def run_practice_quiz(
    chapter: dict[str, Any],
    questions_data: list[dict[str, Any]],
) -> tuple[float, bool]:
    """
    Run practice for current chapter. Returns (score_percent, passed).
    passed is True if score >= 70.
    """
    pool = _prepare_pool(chapter, questions_data)
    if not pool:
        print("No questions available for this chapter.")
        return 0.0, False

    n = min(random.randint(3, 5), len(pool))
    selected = random.sample(pool, n) if len(pool) >= n else pool

    print_header(f"Practice: {chapter.get('title', 'Chapter')}")
    print(f"\nAnswer {len(selected)} questions. You need at least 70% to continue.\n")

    correct = 0
    for idx, q in enumerate(selected, start=1):
        print(f"\nQuestion {idx}/{len(selected)}")
        print(q.get("question", "").strip())
        opts = q.get("options") or {}
        for letter in "ABCD":
            if letter in opts:
                print(f"  {letter}) {opts[letter]}")
        ans = read_choice_letter()
        if ans is None:
            print("Exiting practice early counts as a failed attempt.")
            return 0.0, False
        right = str(q.get("correct", "A")).upper()
        if ans == right:
            correct += 1
            print("Correct.")
        else:
            print(f"Incorrect. Correct answer: {right}.")
        expl = q.get("explanation")
        if expl:
            print(f"Explanation: {expl}")

    score = (correct / len(selected)) * 100.0
    passed = score >= 70.0
    print(f"\n--- Practice score: {correct}/{len(selected)} ({score:.1f}%) ---")
    if passed:
        print("You passed this practice. You can proceed to the next chapter.")
    else:
        print("You need at least 70%. Try again when you're ready.")
    return score, passed


def practice_loop(
    chapter: dict[str, Any],
    questions_data: list[dict[str, Any]],
) -> float:
    """Repeat until pass or user quits from read_choice (returns last score)."""
    while True:
        score, passed = run_practice_quiz(chapter, questions_data)
        if passed:
            return score
        again = input("\nRetry practice? [Y/n]: ").strip().lower()
        if again in ("n", "no"):
            return score
