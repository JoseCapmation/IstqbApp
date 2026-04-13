"""
ISTQB Trainer — CLI for ISTQB CTFL sequential learning.

Run from the `istqb_trainer` directory::

    python main.py

From the chapter menu you can use **P** to practice without reading, or **M** for a full mock exam anytime
(chapter progress is unchanged). The app loads ``data/theory.json`` and ``data/questions.json`` only.
End users do not need PDFs.

Maintainers: regenerate JSON from ``samplePdfs`` (or ``PDF_DIR``)::

    py scripts/build_data.py
    py scripts/build_data.py --theory-from-pdf   # also overwrite theory from syllabus PDF
    py scripts/build_data.py --dump-syllabus-text   # writes data/_syllabus_extracted.txt for QA

Optional developer flag::

    python main.py --rebuild   # same as build script if PDFs are present; else embedded fallback

Environment: see .env.example (PDF_DIR, AI_PROVIDER, API keys for optional extra questions).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from modules.content_build import build_from_pdf_dir, write_data_files
from modules.exam import run_mock_exam
from modules.learner import run_learning_phase
from modules.pdf_parser import _default_pdf_dir, build_data_files, load_theory_questions
from modules.progress_manager import ProgressManager
from modules.quiz import practice_loop
from utils.helpers import clear_screen, print_header


def ensure_data(rebuild: bool) -> tuple[list[dict], list[dict]]:
    theory_path = ROOT / "data" / "theory.json"
    questions_path = ROOT / "data" / "questions.json"
    pdf_dir = _default_pdf_dir(ROOT)
    pdf_files = list(pdf_dir.glob("*.pdf")) if pdf_dir.is_dir() else []

    if rebuild:
        if pdf_files:
            theory, questions = build_from_pdf_dir(
                pdf_dir,
                theory_from_pdf=False,
                base_dir=ROOT,
            )
            write_data_files(ROOT, theory, questions)
        else:
            build_data_files(ROOT, force_fallback=False)
            print(
                "Note: No PDFs found under samplePdfs (or PDF_DIR). "
                "Wrote embedded fallback. Use py scripts/build_data.py when PDFs are available."
            )
    elif not theory_path.exists() or not questions_path.exists():
        build_data_files(ROOT, force_fallback=False)

    theory, questions = load_theory_questions(ROOT)
    if not theory:
        build_data_files(ROOT, force_fallback=False)
        theory, questions = load_theory_questions(ROOT)
    return theory, questions


def main() -> None:
    parser = argparse.ArgumentParser(description="ISTQB Foundation Level Trainer (CLI)")
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Developer: rebuild JSON from PDFs if samplePdfs/PDF_DIR has .pdf files; else fallback.",
    )
    args = parser.parse_args()

    theory, questions = ensure_data(args.rebuild)

    pm = ProgressManager(ROOT)
    pm.load()
    total = len(theory)
    pm.sync_current_chapter(total)
    pm.save()

    while True:
        clear_screen()
        print_header("ISTQB Trainer — CTFL")
        print(f"\nChapters completed: {len(pm.state.completed_chapters)}/{total}")
        if pm.state.completed_chapters:
            print(f"Completed chapter IDs: {sorted(pm.state.completed_chapters)}")
        if pm.state.exam_attempts:
            last = pm.state.exam_attempts[-1]
            print(
                f"Last exam: {last.get('score')}% — "
                f"{'PASS' if last.get('passed') else 'FAIL'}"
            )

        if total == 0:
            print("\nNo chapters loaded. Restore data/theory.json or run py scripts/build_data.py.")
            break

        if pm.all_chapters_done(total):
            print(
                "\nAll chapters completed. You can take the final mock exam "
                "(40 questions, no feedback until the end, 65% to pass)."
            )
            choice = input(
                "\n[T] or [M] Mock exam   [R] Reset progress   [Q] Quit: "
            ).strip().lower()
            if choice in ("q", "quit"):
                pm.save()
                print("Goodbye.")
                break
            if choice in ("r", "reset"):
                print("\nThis clears chapter completion, scores, exam history, and reading checkpoints.")
                confirm = input("Type RESET or yes to confirm: ").strip()
                if confirm == "RESET" or confirm.lower() == "yes":
                    pm.reset_all_progress()
                    pm.sync_current_chapter(total)
                    pm.save()
                    print("All progress has been reset.")
                    input("Press Enter...")
                continue
            if choice in ("t", "m", "mock", "exam"):
                score, passed = run_mock_exam(questions, 40)
                pm.record_exam(score, passed)
                pm.save()
                input("\nPress Enter to return to the menu...")
            continue

        active = pm.active_chapter_id(total)
        if active is None:
            break
        ch = next((c for c in theory if c.get("id") == active), None)
        if ch is None:
            print("Chapter data does not match progress. Reset data/progress.json or rebuild.")
            break

        print(f"\nCurrent chapter: {active} — {ch.get('title')}")
        print("\n[C] Learn then practice (recommended path)")
        print("[P] Practice only — skip reading for this chapter")
        print("[M] Mock exam — 40 questions, does not unlock chapters (65% to pass)")
        print("[R] Reset all progress (requires confirmation)")
        print("[Q] Quit (progress is saved)")
        cmd = input("\nCommand: ").strip().lower()
        if cmd in ("q", "quit"):
            pm.save()
            print("Goodbye.")
            break
        if cmd in ("r", "reset"):
            print("\nThis clears chapter completion, scores, exam history, and reading checkpoints.")
            confirm = input("Type RESET or yes to confirm: ").strip()
            if confirm == "RESET" or confirm.lower() == "yes":
                pm.reset_all_progress()
                pm.sync_current_chapter(total)
                pm.save()
                print("All progress has been reset.")
                input("Press Enter...")
            continue
        if cmd in ("m", "mock", "exam"):
            score, passed = run_mock_exam(questions, 40)
            pm.record_exam(score, passed)
            pm.save()
            input("\nPress Enter to return to the menu...")
            continue
        if cmd in ("p", "practice"):
            score = practice_loop(ch, questions)
            if score >= 70.0:
                pm.complete_chapter(active, score, total)
                pm.save()
                input("\nProgress saved. Press Enter...")
            else:
                pm.save()
                input("\nPress Enter...")
            continue
        if cmd not in ("c", "continue", ""):
            continue

        learn_out = run_learning_phase(ch, pm, active)
        pm.save()
        if learn_out == "quit":
            input("\nProgress saved. Press Enter...")
            continue

        score = practice_loop(ch, questions)
        if score >= 70.0:
            pm.complete_chapter(active, score, total)
            pm.save()
            input("\nProgress saved. Press Enter...")
        else:
            pm.save()
            input("\nPress Enter...")


if __name__ == "__main__":
    main()
