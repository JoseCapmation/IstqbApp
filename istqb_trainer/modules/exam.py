"""Final mock exam: 40 questions, no feedback until the end, 65% to pass."""

from __future__ import annotations

import random
from typing import Any

from utils.helpers import print_header, read_choice_letter


def _all_questions_flat(questions_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for block in questions_data:
        for q in block.get("questions") or []:
            out.append(q)
    return out


def run_mock_exam(questions_data: list[dict[str, Any]], num_questions: int = 40) -> tuple[float, bool]:
    """
    Returns (score_percent, passed). Feedback only after the last question.
    If fewer than num_questions in bank, samples with replacement (message printed once).
    """
    bank = _all_questions_flat(questions_data)
    if not bank:
        print("No questions in the bank for the exam.")
        return 0.0, False

    print_header("Mock exam (40 questions, results at the end)")
    if len(bank) < num_questions:
        print(
            f"\nNote: The question bank has only {len(bank)} items. "
            f"Some questions may repeat to reach {num_questions}.\n"
        )
        sample = [random.choice(bank) for _ in range(num_questions)]
    else:
        sample = random.sample(bank, num_questions)

    answers: list[str] = []
    for idx, q in enumerate(sample, start=1):
        print(f"\nQuestion {idx}/{len(sample)}")
        print(q.get("question", "").strip())
        opts = q.get("options") or {}
        for letter in "ABCD":
            if letter in opts:
                print(f"  {letter}) {opts[letter]}")
        ans = read_choice_letter()
        if ans is None:
            print("Exam aborted.")
            return 0.0, False
        answers.append(ans)

    correct = 0
    for q, a in zip(sample, answers):
        if str(q.get("correct", "")).upper() == a:
            correct += 1

    score = (correct / len(sample)) * 100.0
    passed = score >= 65.0

    print("\n" + "=" * 40)
    print("Exam finished")
    print(f"Score: {correct}/{len(sample)} ({score:.1f}%)")
    print("Passing score: 65%.")
    if passed:
        print("Result: PASSED")
    else:
        print("Result: NOT PASSED")
    print("=" * 40)

    return score, passed
