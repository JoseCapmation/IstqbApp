"""Load and save user progress in data/progress.json."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ProgressState:
    current_chapter: int = 1
    completed_chapters: list[int] = field(default_factory=list)
    scores_per_chapter: dict[str, float] = field(default_factory=dict)
    exam_attempts: list[dict[str, Any]] = field(default_factory=list)
    # Next chunk index to show per chapter (0-based); keys are chapter ids as strings.
    theory_chunk_index: dict[str, int] = field(default_factory=dict)

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "current_chapter": self.current_chapter,
            "completed_chapters": self.completed_chapters,
            "scores_per_chapter": self.scores_per_chapter,
            "exam_attempts": self.exam_attempts,
            "theory_chunk_index": dict(self.theory_chunk_index),
        }

    @classmethod
    def from_json_dict(cls, d: dict[str, Any]) -> ProgressState:
        raw_tc = d.get("theory_chunk_index") or {}
        theory_chunk_index = {str(k): int(v) for k, v in raw_tc.items()}
        return cls(
            current_chapter=int(d.get("current_chapter", 1)),
            completed_chapters=list(d.get("completed_chapters", [])),
            scores_per_chapter={str(k): float(v) for k, v in (d.get("scores_per_chapter") or {}).items()},
            exam_attempts=list(d.get("exam_attempts", [])),
            theory_chunk_index=theory_chunk_index,
        )


def _progress_path(base_dir: Path) -> Path:
    return base_dir / "data" / "progress.json"


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


class ProgressManager:
    def __init__(self, base_dir: Path | None = None):
        self.base_dir = base_dir or Path(__file__).resolve().parent.parent
        self.path = _progress_path(self.base_dir)
        self.state = ProgressState()

    def load(self) -> ProgressState:
        if not self.path.exists():
            self.state = ProgressState()
            self.save()
            return self.state
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        self.state = ProgressState.from_json_dict(raw)
        return self.state

    def save(self) -> None:
        text = json.dumps(self.state.to_json_dict(), indent=2, ensure_ascii=False)
        _atomic_write(self.path, text)

    def total_chapters(self, theory: list[dict[str, Any]]) -> int:
        return len(theory)

    def is_chapter_unlocked(self, chapter_id: int) -> bool:
        if chapter_id <= 1:
            return True
        return (chapter_id - 1) in self.state.completed_chapters

    def active_chapter_id(self, total: int) -> int | None:
        """First chapter not in completed_chapters, or None if all done."""
        for cid in range(1, total + 1):
            if cid not in self.state.completed_chapters:
                return cid
        return None

    def complete_chapter(self, chapter_id: int, score_percent: float, total_chapters: int) -> None:
        if chapter_id not in self.state.completed_chapters:
            self.state.completed_chapters.append(chapter_id)
        self.state.completed_chapters.sort()
        self.state.scores_per_chapter[str(chapter_id)] = round(score_percent, 1)
        self.sync_current_chapter(total_chapters)

    def sync_current_chapter(self, total_chapters: int) -> None:
        """Set current_chapter to the active incomplete chapter."""
        ac = self.active_chapter_id(total_chapters)
        if ac is not None:
            self.state.current_chapter = ac
        elif total_chapters > 0:
            self.state.current_chapter = total_chapters

    def all_chapters_done(self, total: int) -> bool:
        if total == 0:
            return False
        return set(self.state.completed_chapters) >= set(range(1, total + 1))

    def record_exam(self, score_percent: float, passed: bool) -> None:
        attempt = {
            "date": datetime.now(timezone.utc).isoformat(),
            "score": round(score_percent, 1),
            "passed": passed,
        }
        self.state.exam_attempts.append(attempt)

    def get_theory_chunk(self, chapter_id: int) -> int:
        return int(self.state.theory_chunk_index.get(str(chapter_id), 0))

    def set_theory_chunk(self, chapter_id: int, index: int) -> None:
        self.state.theory_chunk_index[str(chapter_id)] = max(0, int(index))

    def clear_theory_checkpoint(self, chapter_id: int) -> None:
        self.state.theory_chunk_index.pop(str(chapter_id), None)

    def clear_theory_progress(self) -> None:
        self.state.theory_chunk_index.clear()

    def reset_all_progress(self) -> None:
        self.state.completed_chapters.clear()
        self.state.scores_per_chapter.clear()
        self.state.exam_attempts.clear()
        self.state.theory_chunk_index.clear()
        self.state.current_chapter = 1
