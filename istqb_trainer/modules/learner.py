"""Learning phase: theory in chunks with resume, quit (Q), and restart chapter (S)."""

from __future__ import annotations

from typing import Any, Literal

from modules.progress_manager import ProgressManager
from utils.helpers import pause, print_header, read_learning_command

LearningPhaseResult = Literal["completed", "quit"]


def run_learning_phase(
    chapter: dict[str, Any],
    pm: ProgressManager,
    chapter_id: int,
) -> LearningPhaseResult:
    title = chapter.get("title", "Chapter")
    chunks = chapter.get("content_chunks") or []
    print_header(f"Learning: {title}")
    if not chunks:
        print("No theory content for this chapter.")
        pause()
        return "completed"

    total = len(chunks)
    next_idx = pm.get_theory_chunk(chapter_id)
    if next_idx > total:
        next_idx = 0

    # Read all parts previously; user quit before starting practice
    if next_idx >= total:
        print("\nYou already finished reading this chapter. Continuing to practice.")
        pm.clear_theory_checkpoint(chapter_id)
        return "completed"

    if 0 < next_idx < total:
        part_1based = next_idx + 1
        print(
            f"\nYou have a saved reading position (part {part_1based}/{total}).\n"
            "[R] Resume here   [B] Begin chapter again from part 1"
        )
        while True:
            choice = input("Choice: ").strip().upper()
            if choice in ("R", "RESUME", ""):
                break
            if choice in ("B", "BEGIN", "START", "O"):
                next_idx = 0
                pm.set_theory_chunk(chapter_id, 0)
                break
            print("Enter R to resume or B to start from the beginning.")

    i = next_idx
    while i < total:
        print(f"\n--- Part {i + 1}/{total} ---\n")
        print(chunks[i].strip())
        pm.set_theory_chunk(chapter_id, i + 1)

        if i < total - 1:
            cmd = read_learning_command()
            if cmd == "quit":
                pm.save()
                return "quit"
            if cmd == "restart":
                i = 0
                pm.set_theory_chunk(chapter_id, 0)
                continue
            i += 1
            continue

        cmd = read_learning_command(
            "\n[Enter] start practice  [Q] menu  [S] restart chapter: "
        )
        if cmd == "quit":
            pm.set_theory_chunk(chapter_id, total)
            pm.save()
            return "quit"
        if cmd == "restart":
            i = 0
            pm.set_theory_chunk(chapter_id, 0)
            continue
        pm.clear_theory_checkpoint(chapter_id)
        print("\nEnd of theory for this chapter.")
        return "completed"

    return "completed"
