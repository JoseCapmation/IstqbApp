"""Terminal helpers for ISTQB Trainer."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal


def clear_screen() -> None:
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def term_width(default: int = 80) -> int:
    try:
        return os.get_terminal_size().columns
    except OSError:
        return default


def wrap_hint(text: str, prefix: str = "") -> str:
    w = max(40, term_width() - len(prefix))
    if len(text) <= w:
        return prefix + text
    return prefix + text[: w - 3] + "..."


def read_choice_letter(prompt: str = "Your answer (A-D, or Q to quit): ") -> str | None:
    """Return 'A'-'D' or None if quit."""
    while True:
        raw = input(prompt).strip().upper()
        if raw in ("Q", "QUIT", "EXIT"):
            return None
        if len(raw) == 1 and raw in "ABCD":
            return raw
        print("Please enter A, B, C, or D (or Q to quit).")


LearningCommand = Literal["next", "quit", "restart"]


def read_learning_command(
    message: str = "\n[Enter] next part  [Q] menu  [S] restart chapter: ",
) -> LearningCommand:
    """Enter = next chunk; Q = return to menu; S = restart this chapter from the first part."""
    while True:
        raw = input(message).strip().upper()
        if raw in ("", "N", "NEXT"):
            return "next"
        if raw in ("Q", "QUIT", "EXIT"):
            return "quit"
        if raw in ("S", "START", "RESTART"):
            return "restart"
        print("Press Enter for the next part, Q to return to the menu, or S to restart this chapter.")


def pause(message: str = "\nPress Enter to continue...") -> None:
    input(message)


def print_header(title: str) -> None:
    line = "=" * min(len(title) + 8, term_width())
    print(line)
    print(f"  {title}")
    print(line)


def base_dir() -> Path:
    return Path(__file__).resolve().parent.parent
