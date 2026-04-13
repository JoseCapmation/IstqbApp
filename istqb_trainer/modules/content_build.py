"""
Maintainer-only: build theory.json and questions.json from classified PDFs.

By default, ``build_from_pdf_dir(..., theory_from_pdf=False, base_dir=...)`` reuses
existing ``data/theory.json`` so curated study text is not overwritten; pass
``theory_from_pdf=True`` to regenerate theory from the syllabus PDF.

Syllabus → six CTFL chapters; official sample exam + 500-paper banks with paired answers.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from modules.pdf_parser import _chunk_text, _extract_pdf_text, get_fallback_theory_and_questions

# --- Syllabus body (examinable chapters 1–6 only) --------------------------------

_SYLLABUS_START = re.compile(r"Chapter\s+1:\s*\n\s*1\.1\s", re.MULTILINE)
_SYLLABUS_END = re.compile(r"\n7\.\s+References\b", re.MULTILINE)

_FOOTER_LINES = re.compile(
    r"^v4\.0\.\d+\s+Page\s+\d+\s+of\s+\d+.*$",
    re.MULTILINE | re.IGNORECASE,
)
_HEADER_JUNK = re.compile(
    r"^©?\s*International Software Testing Qualifications Board.*$",
    re.MULTILINE | re.IGNORECASE,
)

CHAPTER_TITLES: dict[int, str] = {
    1: "Fundamentals of Testing",
    2: "Testing Throughout the Software Development Lifecycle",
    3: "Static Testing",
    4: "Test Analysis and Design",
    5: "Managing the Test Activities",
    6: "Test Tools and Automation",
}

# Extra theory chapter for istqb.guru bank (no syllabus text)
PRACTICE_BANK_CHAPTER_ID = 7
PRACTICE_BANK_TITLE = "Collated practice questions (sample papers)"
PRACTICE_BANK_CHUNKS = [
    "This section accompanies a large set of multiple-choice questions from public sample papers "
    "(istqb.guru and similar sources). They cover the full Foundation Level scope. "
    "Work through them after you have studied the six syllabus chapters, or use them to reinforce weak areas.",
]


def _clean_syllabus_body(text: str) -> str:
    text = _FOOTER_LINES.sub("", text)
    text = _HEADER_JUNK.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_syllabus_main_body(full_text: str) -> str:
    m0 = _SYLLABUS_START.search(full_text)
    if not m0:
        return ""
    start = m0.start()
    m1 = _SYLLABUS_END.search(full_text, start)
    end = m1.start() if m1 else len(full_text)
    return _clean_syllabus_body(full_text[start:end])


def syllabus_to_theory_chapters(syllabus_text: str) -> list[dict[str, Any]]:
    """Split examinable syllabus into six chapters with stable titles."""
    if not syllabus_text.strip():
        return []
    m1 = re.search(r"^Chapter\s+1:\s*", syllabus_text, re.MULTILINE)
    if not m1:
        return []
    starts: list[tuple[int, int]] = [(m1.start(), 1)]
    for n in range(2, 7):
        m = re.search(rf"^Learning Objectives for Chapter {n}:\s*$", syllabus_text, re.MULTILINE)
        if not m:
            return []
        starts.append((m.start(), n))
    starts.sort(key=lambda x: x[0])
    theory: list[dict[str, Any]] = []
    for i, (pos, ch_num) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(syllabus_text)
        body = _clean_syllabus_body(syllabus_text[pos:end])
        title = CHAPTER_TITLES.get(ch_num, f"Chapter {ch_num}")
        theory.append(
            {
                "id": ch_num,
                "title": title,
                "content_chunks": _chunk_text(body, max_chars=950),
            }
        )
    return theory


def theory_with_practice_bank(syllabus_theory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = list(syllabus_theory)
    if not any(c["id"] == PRACTICE_BANK_CHAPTER_ID for c in out):
        out.append(
            {
                "id": PRACTICE_BANK_CHAPTER_ID,
                "title": PRACTICE_BANK_TITLE,
                "content_chunks": list(PRACTICE_BANK_CHUNKS),
            }
        )
    return out


# --- PDF classification ---------------------------------------------------------

def _pair_question_answer(q_path: Path, answer_files: list[Path]) -> Path | None:
    name = q_path.name
    candidates = []
    if "Questions" in name:
        alt = name.replace("Questions", "Answers").replace("questions", "answers")
        candidates.append(q_path.with_name(alt))
    for a in answer_files:
        if a.stem.lower().replace("answers", "questions") == q_path.stem.lower().replace(
            "answers", "questions"
        ):
            candidates.append(a)
    for c in candidates:
        if c.exists():
            return c
    q_lower = q_path.name.lower()
    for a in answer_files:
        al = a.name.lower()
        if q_lower.split("questions")[0] and q_lower.split("questions")[0] in al.replace(
            "answers", ""
        ):
            return a
    return None


def classify_pdfs(pdf_dir: Path) -> tuple[list[Path], list[tuple[Path, Path]]]:
    """Return (syllabus_paths, [(questions_pdf, answers_pdf), ...])."""
    pdfs = sorted(pdf_dir.glob("*.pdf"))
    syllabus = [p for p in pdfs if "syllabus" in p.name.lower()]
    answer_files = [p for p in pdfs if "answer" in p.name.lower()]
    question_files = [
        p
        for p in pdfs
        if p not in syllabus
        and p not in answer_files
        and ("question" in p.name.lower() or "sample-exam" in p.name.lower() or "sample_papers" in p.name.lower())
    ]
    pairs: list[tuple[Path, Path]] = []
    for q in question_files:
        ap = _pair_question_answer(q, answer_files)
        if ap:
            pairs.append((q, ap))
        else:
            pairs.append((q, q))
    return syllabus, pairs


# --- Official sample exam -------------------------------------------------------

_Q_EXAM = re.compile(
    r"Question\s*#(\d+)\s*\([^)]+\)\s*\n(.*?)(?=Question\s*#\d+|\Z)",
    re.DOTALL | re.IGNORECASE,
)

_OPT_EXAM = re.compile(r"^([a-d])\)\s*(.+)$", re.MULTILINE | re.IGNORECASE)

_ANS_EXAM_BLOCK = re.compile(
    r"^(\d+)\s+([a-d])(?:,\s*([a-d]))?\s+",
    re.MULTILINE | re.IGNORECASE,
)

_LO_TAG = re.compile(r"\bFL-(\d+)\.\d+\.\d+\b")


def parse_official_exam_questions(text: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for m in _Q_EXAM.finditer(text):
        qn = int(m.group(1))
        block = m.group(2)
        if re.search(r"Select\s+TWO", block, re.I):
            continue
        if re.search(r"^e\)\s", block, re.MULTILINE | re.IGNORECASE):
            continue
        opts: dict[str, str] = {}
        for om in _OPT_EXAM.finditer(block):
            k = om.group(1).upper()
            opts[k] = om.group(2).strip()
        if set(opts.keys()) != {"A", "B", "C", "D"}:
            continue
        stem_end = block.find("a)")
        stem = block[:stem_end].strip() if stem_end > 0 else block.strip()
        stem = re.sub(r"\s+", " ", stem)
        out.append(
            {
                "num": qn,
                "question": stem[:2000],
                "options": opts,
                "correct": "A",
                "explanation": None,
                "lo_chapter": None,
            }
        )
    return out


def parse_official_exam_answers(text: str) -> dict[int, str]:
    """Map question number -> single correct letter A-D; skip multi-correct."""
    answers: dict[int, str] = {}
    for m in _ANS_EXAM_BLOCK.finditer(text):
        qn = int(m.group(1))
        a1 = m.group(2).lower()
        a2 = m.group(3)
        if a2:
            continue
        answers[qn] = a1.upper()
    return answers


def attach_lo_chapter_from_answers(answer_text: str, questions: list[dict[str, Any]]) -> None:
    """Set lo_chapter from first FL-X in answer block after each question header in answers PDF."""
    for q in questions:
        m = re.search(rf"(?m)^{q['num']}\s+[a-d]\b", answer_text, re.IGNORECASE)
        if not m:
            q["lo_chapter"] = 1
            continue
        window = answer_text[m.start() : m.start() + 2500]
        lm = _LO_TAG.search(window)
        if lm:
            ch = int(lm.group(1))
            q["lo_chapter"] = ch if 1 <= ch <= 6 else 1
        else:
            q["lo_chapter"] = 1


def build_official_exam_bank(q_text: str, a_text: str, id_prefix: str) -> list[dict[str, Any]]:
    qs = parse_official_exam_questions(q_text)
    ans = parse_official_exam_answers(a_text)
    attach_lo_chapter_from_answers(a_text, qs)
    bank: list[dict[str, Any]] = []
    for q in qs:
        if q["num"] not in ans:
            continue
        q["correct"] = ans[q["num"]]
        cid = q.pop("lo_chapter") or 1
        bank.append(
            {
                "id": f"{id_prefix}_{q['num']}",
                "question": q["question"],
                "options": q["options"],
                "correct": q["correct"],
                "explanation": q["explanation"],
                "_chapter_id": cid,
            }
        )
    return bank


# --- 500 papers (istqb.guru style) ---------------------------------------------

_Q_500 = re.compile(
    r"Q\.\s*(\d+)\s*:\s*(.*?)(?=Q\.\s*\d+\s*:|$)",
    re.DOTALL | re.IGNORECASE,
)

_OPT_500 = re.compile(r"^([A-D])\.\s*(.+)$", re.MULTILINE)


def parse_500_paper_questions(text: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for m in _Q_500.finditer(text):
        qn = int(m.group(1))
        block = m.group(2).strip()
        opts: dict[str, str] = {}
        for om in _OPT_500.finditer(block):
            opts[om.group(1)] = om.group(2).strip()
        if set(opts.keys()) != {"A", "B", "C", "D"}:
            continue
        first_opt = block.find("\nA.")
        stem = block[:first_opt].strip() if first_opt > 0 else block
        stem = re.sub(r"\s+", " ", stem)
        out.append({"num": qn, "question": stem[:2000], "options": dict(opts)})
    return out


_ANS_500_LINE = re.compile(r"^Q\.\s*(\d+)\s+([A-E])\s*$", re.MULTILINE | re.IGNORECASE)


def parse_500_paper_answers(text: str) -> dict[int, str]:
    d: dict[int, str] = {}
    for m in _ANS_500_LINE.finditer(text):
        qn = int(m.group(1))
        letter = m.group(2).upper()
        if letter in "ABCD":
            d[qn] = letter
    return d


def build_500_bank(q_text: str, a_text: str) -> list[dict[str, Any]]:
    qs = parse_500_paper_questions(q_text)
    ans = parse_500_paper_answers(a_text)
    bank: list[dict[str, Any]] = []
    for q in qs:
        if q["num"] not in ans:
            continue
        bank.append(
            {
                "id": f"guru_{q['num']}",
                "question": q["question"],
                "options": q["options"],
                "correct": ans[q["num"]],
                "explanation": None,
                "_chapter_id": PRACTICE_BANK_CHAPTER_ID,
            }
        )
    return bank


# --- Aggregate -----------------------------------------------------------------

def group_questions_by_chapter(
    flat: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_c: dict[int, list[dict[str, Any]]] = {}
    for q in flat:
        cid = int(q.pop("_chapter_id", 1))
        q_clean = {k: v for k, v in q.items() if not k.startswith("_")}
        by_c.setdefault(cid, []).append(q_clean)
    return [{"chapter_id": k, "questions": v} for k, v in sorted(by_c.items())]


def _load_theory_json(base_dir: Path) -> list[dict[str, Any]] | None:
    path = base_dir / "data" / "theory.json"
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return raw if isinstance(raw, list) else None


def build_from_pdf_dir(
    pdf_dir: Path,
    *,
    theory_from_pdf: bool = False,
    base_dir: Path | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    syllabus_paths, pairs = classify_pdfs(pdf_dir)

    theory: list[dict[str, Any]] = []
    if not theory_from_pdf and base_dir is not None:
        existing = _load_theory_json(base_dir)
        if existing:
            theory = existing

    if not theory:
        if syllabus_paths:
            full = _extract_pdf_text(syllabus_paths[0])
            body = extract_syllabus_main_body(full)
            theory = syllabus_to_theory_chapters(body)

        if len(theory) < 6:
            fb_t, _ = get_fallback_theory_and_questions()
            theory = fb_t

    theory = theory_with_practice_bank(theory)

    all_q: list[dict[str, Any]] = []

    for q_path, a_path in pairs:
        try:
            qt = _extract_pdf_text(q_path)
            at = _extract_pdf_text(a_path) if a_path != q_path else ""
        except Exception:
            continue
        name = q_path.name.lower()
        if "sample-exam" in name and "question" in name:
            chunk = build_official_exam_bank(qt, at, "examC")
            all_q.extend(chunk)
        elif "500" in name or "istqb.guru" in name or "sample_papers" in name:
            chunk = build_500_bank(qt, at)
            all_q.extend(chunk)

    if not all_q:
        _, fb_q = get_fallback_theory_and_questions()
        questions = fb_q
    else:
        questions = group_questions_by_chapter(all_q)

    return theory, questions


def write_data_files(
    base_dir: Path,
    theory: list[dict[str, Any]],
    questions: list[dict[str, Any]],
) -> None:
    data_dir = base_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "theory.json").write_text(
        json.dumps(theory, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (data_dir / "questions.json").write_text(
        json.dumps(questions, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def dump_syllabus_text(pdf_dir: Path, out_path: Path) -> None:
    """Maintainer helper: write raw extracted syllabus text for QA in the IDE."""
    syllabus_paths, _ = classify_pdfs(pdf_dir)
    if not syllabus_paths:
        out_path.write_text("(no syllabus PDF found)\n", encoding="utf-8")
        return
    full = _extract_pdf_text(syllabus_paths[0])
    body = extract_syllabus_main_body(full)
    out_path.write_text(body or full, encoding="utf-8")
