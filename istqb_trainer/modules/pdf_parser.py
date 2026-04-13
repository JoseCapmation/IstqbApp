"""
Extract theory and MCQs from PDFs in samplePdfs (or PDF_DIR).
Writes data/theory.json and data/questions.json; uses fallback data on failure.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import pdfplumber

# --- Heuristics ----------------------------------------------------------------

CHAPTER_PATTERNS = [
    re.compile(
        r"^\s*(chapter|section)\s+([\d\.]+)\s*[:\-\.]?\s*(.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    re.compile(
        r"^\s*(\d+(?:\.\d+)*)\s+([A-Z][^\n]{3,120})\s*$",
        re.MULTILINE,
    ),
]

OPTION_LINE = re.compile(
    r"^\s*([A-Da-d])[\.\)]\s+(.+)$",
    re.MULTILINE,
)
ANSWER_LINE = re.compile(
    r"(?:^|\s)(?:answer|correct|solution)\s*[:.]?\s*([A-Da-d])\b",
    re.IGNORECASE | re.MULTILINE,
)


def _default_pdf_dir(base: Path) -> Path:
    env = os.environ.get("PDF_DIR", "").strip()
    if env:
        p = Path(env)
        if not p.is_absolute():
            p = (base / p).resolve()
        return p
    return base / "samplePdfs"


def _extract_pdf_text(pdf_path: Path) -> str:
    parts: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            if t.strip():
                parts.append(t)
    return "\n\n".join(parts)


def _split_paragraphs(text: str) -> list[str]:
    blocks = re.split(r"\n\s*\n+", text)
    return [b.strip() for b in blocks if b.strip()]


def _find_chapter_starts(text: str) -> list[tuple[int, str]]:
    """Return list of (char_index, title) for detected headings."""
    hits: list[tuple[int, str]] = []
    for pat in CHAPTER_PATTERNS:
        for m in pat.finditer(text):
            title = m.group(0).strip()[:200]
            hits.append((m.start(), title))
    hits.sort(key=lambda x: x[0])
    # Dedupe nearby duplicate indices
    deduped: list[tuple[int, str]] = []
    for idx, title in hits:
        if deduped and abs(idx - deduped[-1][0]) < 5:
            continue
        deduped.append((idx, title))
    return deduped


def _split_into_chapters(full_text: str) -> list[tuple[str, str]]:
    """Return list of (title, body)."""
    starts = _find_chapter_starts(full_text)
    if not starts:
        paras = _split_paragraphs(full_text)
        if not paras:
            return []
        # Single blob: treat as one chapter
        return [("Document", full_text.strip())]
    chapters: list[tuple[str, str]] = []
    for i, (pos, title) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(full_text)
        body = full_text[pos:end]
        # Remove title line from body duplicate if present
        body = body[len(title) :].strip() if body.startswith(title) else body.strip()
        chapters.append((title, body))
    return chapters


def _chunk_text(body: str, max_chars: int = 900) -> list[str]:
    """Split body into readable chunks without breaking mid-word when possible."""
    body = body.strip()
    if not body:
        return ["(No content extracted for this section.)"]
    if len(body) <= max_chars:
        return [body]
    chunks: list[str] = []
    start = 0
    while start < len(body):
        end = min(start + max_chars, len(body))
        if end < len(body):
            cut = body.rfind(" ", start, end)
            if cut > start + max_chars // 2:
                end = cut
        chunks.append(body[start:end].strip())
        start = end
    return chunks


def _parse_mcqs_from_block(block: str, chapter_id: int, start_q: int) -> tuple[list[dict[str, Any]], int]:
    """Very loose MCQ extraction from a text block."""
    questions: list[dict[str, Any]] = []
    qid = start_q
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if len(line) < 15:
            i += 1
            continue
        # Look ahead for 4 option lines
        opts: dict[str, str] = {}
        j = i + 1
        while j < len(lines) and len(opts) < 4:
            om = OPTION_LINE.match(lines[j].strip())
            if om:
                key = om.group(1).upper()
                opts[key] = om.group(2).strip()
            j += 1
        if len(opts) >= 4:
            qtext = line
            if qtext.endswith("?"):
                pass
            elif not any(c in qtext for c in "?:"):
                i += 1
                continue
            ans_m = ANSWER_LINE.search(block[max(0, i - 5) : i + 400])
            correct = ans_m.group(1).upper() if ans_m else "A"
            explanation = None
            questions.append(
                {
                    "id": f"c{chapter_id}_q{qid}",
                    "question": qtext,
                    "options": {
                        "A": opts.get("A", ""),
                        "B": opts.get("B", ""),
                        "C": opts.get("C", ""),
                        "D": opts.get("D", ""),
                    },
                    "correct": correct if correct in "ABCD" else "A",
                    "explanation": explanation,
                }
            )
            qid += 1
            i = j
            continue
        i += 1
    return questions, qid


def _questions_for_chapter(body: str, chapter_id: int) -> list[dict[str, Any]]:
    qs, _ = _parse_mcqs_from_block(body, chapter_id, 1)
    return qs


def get_fallback_theory_and_questions() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Built-in CTFL-style sample content when PDF parsing yields nothing."""
    theory: list[dict[str, Any]] = []
    questions_wrapped: list[dict[str, Any]] = []

    chapters_data = [
        {
            "title": "Fundamentals of Testing",
            "chunks": [
                "Testing shows the presence of defects, not their absence. The main objectives include finding defects, gaining confidence, and providing information for stakeholders.",
                "A test condition is an item or event that could be verified by one or more test cases. Test cases specify inputs, execution steps, and expected results.",
                "The seven testing principles include: testing shows presence of defects; exhaustive testing is impossible; early testing saves time and money; defect clustering; pesticides paradox; testing is context dependent; and absence-of-errors fallacy.",
            ],
            "qs": [
                {
                    "q": "Which testing principle states that if the same tests are repeated, they may no longer find new defects?",
                    "opts": ["Defect clustering", "Pesticides paradox", "Early testing", "Exhaustive testing"],
                    "correct": "B",
                    "explanation": "The pesticides paradox: tests need to be reviewed and revised to find different defects.",
                },
                {
                    "q": "What is the primary goal of testing?",
                    "opts": [
                        "To prove the software has no defects",
                        "To show the presence of defects and reduce risk",
                        "To write code",
                        "To replace reviews",
                    ],
                    "correct": "B",
                    "explanation": "Testing demonstrates defects exist and helps stakeholders make informed decisions.",
                },
                {
                    "q": "Exhaustive testing is generally impossible because:",
                    "opts": [
                        "Testers are too slow",
                        "There are too many combinations of inputs and paths",
                        "Management forbids it",
                        "Tools do not exist",
                    ],
                    "correct": "B",
                    "explanation": "The input and path space is usually infinite or too large to cover completely.",
                },
                {
                    "q": "Early testing helps mainly because:",
                    "opts": [
                        "Defects found late are cheaper",
                        "Defects found early are cheaper to fix",
                        "Developers prefer it",
                        "Users demand it",
                    ],
                    "correct": "B",
                    "explanation": "The cost of fixing defects increases over the lifecycle.",
                },
            ],
        },
        {
            "title": "Testing Throughout the SDLC",
            "chunks": [
                "Testing activities should start as early as possible in the software development lifecycle. Shift-left means involving testing earlier to prevent defects.",
                "Different test levels include component, integration, system, and acceptance testing. Each level has distinct objectives and test basis.",
                "Test types can be classified as functional vs non-functional, and white-box vs black-box, among others.",
            ],
            "qs": [
                {
                    "q": "Which test level focuses on interactions between components?",
                    "opts": ["Component testing", "Integration testing", "System testing", "Maintenance testing"],
                    "correct": "B",
                    "explanation": "Integration testing checks interfaces and interactions between integrated components.",
                },
                {
                    "q": "Shift-left testing primarily means:",
                    "opts": [
                        "Testing only at the end",
                        "Moving testing activities earlier in the lifecycle",
                        "Testing only on the left server",
                        "Avoiding automation",
                    ],
                    "correct": "B",
                    "explanation": "Shift-left emphasizes earlier test involvement and defect prevention.",
                },
                {
                    "q": "Acceptance testing is mainly used to:",
                    "opts": [
                        "Find all code bugs",
                        "Validate the system meets business needs",
                        "Replace unit tests",
                        "Measure CPU usage",
                    ],
                    "correct": "B",
                    "explanation": "Acceptance testing confirms the system fulfills agreed requirements for stakeholders.",
                },
            ],
        },
        {
            "title": "Static Testing",
            "chunks": [
                "Static testing examines work products without executing code. Reviews and static analysis are key techniques.",
                "Review types include informal review, walkthrough, technical review, inspection, and management review.",
                "Static analysis tools can detect defects such as unreachable code, security weaknesses, and maintainability issues.",
            ],
            "qs": [
                {
                    "q": "Static testing means:",
                    "opts": [
                        "Running performance tests",
                        "Examining artifacts without executing the software",
                        "Testing only mobile apps",
                        "Testing with static electricity",
                    ],
                    "correct": "B",
                    "explanation": "Static testing evaluates documentation and code without execution.",
                },
                {
                    "q": "Which review is typically the most formal and rigorous?",
                    "opts": ["Informal review", "Walkthrough", "Inspection", "Ad hoc review"],
                    "correct": "C",
                    "explanation": "Inspections follow a defined process with roles and documented outcomes.",
                },
                {
                    "q": "A benefit of early reviews is:",
                    "opts": [
                        "They remove the need for testing",
                        "They can find defects before dynamic test execution",
                        "They always find all defects",
                        "They replace automation",
                    ],
                    "correct": "B",
                    "explanation": "Reviews catch issues in requirements and design before they propagate.",
                },
            ],
        },
        {
            "title": "Test Techniques",
            "chunks": [
                "Black-box techniques include equivalence partitioning, boundary value analysis, decision table testing, state transition testing, and use case testing.",
                "White-box techniques include statement and branch coverage, and more advanced coverage types.",
                "Experience-based techniques include exploratory testing and error guessing.",
            ],
            "qs": [
                {
                    "q": "Boundary value analysis is typically used with:",
                    "opts": [
                        "Equivalence partitioning",
                        "Only performance tests",
                        "Only security scans",
                        "Compiler internals only",
                    ],
                    "correct": "A",
                    "explanation": "BVA focuses on boundaries of equivalence partitions.",
                },
                {
                    "q": "Decision table testing is useful when:",
                    "opts": [
                        "There are complex business rules with combinations of conditions",
                        "There is no documentation",
                        "Only one input exists",
                        "Only UI colors matter",
                    ],
                    "correct": "A",
                    "explanation": "Decision tables model combinations of conditions and actions.",
                },
                {
                    "q": "Exploratory testing is:",
                    "opts": [
                        "Fully scripted in advance",
                        "Simultaneous learning, test design, and execution",
                        "Only automated",
                        "Not a real technique",
                    ],
                    "correct": "B",
                    "explanation": "Exploratory testing combines learning about the product with testing.",
                },
            ],
        },
        {
            "title": "Test Management",
            "chunks": [
                "Test planning defines scope, approach, resources, and schedule. Test monitoring and control track progress against the plan.",
                "Test estimation can use metrics, expert judgment, or historical data. Risk-based testing prioritizes tests by risk.",
                "Configuration management ensures test assets align with the versions under test.",
            ],
            "qs": [
                {
                    "q": "Risk-based testing prioritizes:",
                    "opts": [
                        "Random areas",
                        "Areas with higher risk of failure or impact",
                        "Only UI text",
                        "Only documentation",
                    ],
                    "correct": "B",
                    "explanation": "Effort focuses where failure would hurt most or likelihood is high.",
                },
                {
                    "q": "Test monitoring primarily involves:",
                    "opts": [
                        "Writing production code",
                        "Gathering information and metrics to assess progress",
                        "Deleting test cases",
                        "Ignoring defects",
                    ],
                    "correct": "B",
                    "explanation": "Monitoring compares actual status with planned test objectives.",
                },
                {
                    "q": "Configuration management helps testing by:",
                    "opts": [
                        "Hiding versions",
                        "Ensuring consistency between testware and software versions",
                        "Removing traceability",
                        "Avoiding baselines",
                    ],
                    "correct": "B",
                    "explanation": "Test objects must match the version of the software under test.",
                },
            ],
        },
        {
            "title": "Tool Support for Testing",
            "chunks": [
                "Test tools support test design, execution, performance, and management. Tools can be commercial, open-source, or custom.",
                "Potential benefits include repeatability and coverage; risks include unrealistic expectations and maintenance costs.",
                "The generic tool architecture includes data, test harness, and interfaces to the system under test.",
            ],
            "qs": [
                {
                    "q": "A common risk of test automation is:",
                    "opts": [
                        "Improved repeatability",
                        "Unrealistic expectations and high maintenance cost",
                        "Faster feedback",
                        "Better regression coverage",
                    ],
                    "correct": "B",
                    "explanation": "Automation requires investment; expecting magic results is a classic pitfall.",
                },
                {
                    "q": "Data-driven testing means:",
                    "opts": [
                        "Tests ignore data",
                        "Test cases use external data sets to vary inputs",
                        "Only manual testing",
                        "Only load testing",
                    ],
                    "correct": "B",
                    "explanation": "Inputs and expected results are often stored in tables or files.",
                },
                {
                    "q": "Keyword-driven testing uses:",
                    "opts": [
                        "Random keystrokes",
                        "Keywords to represent actions and data in tests",
                        "Only compiler keywords",
                        "No documentation",
                    ],
                    "correct": "B",
                    "explanation": "Keywords abstract steps so non-programmers can read or maintain tests.",
                },
            ],
        },
    ]

    labels = ["A", "B", "C", "D"]
    for idx, ch in enumerate(chapters_data, start=1):
        theory.append(
            {
                "id": idx,
                "title": ch["title"],
                "content_chunks": ch["chunks"],
            }
        )
        qlist: list[dict[str, Any]] = []
        for qi, item in enumerate(ch["qs"], start=1):
            opts = {labels[j]: item["opts"][j] for j in range(4)}
            qlist.append(
                {
                    "id": f"c{idx}_q{qi}",
                    "question": item["q"],
                    "options": opts,
                    "correct": item["correct"],
                    "explanation": item["explanation"],
                }
            )
        questions_wrapped.append({"chapter_id": idx, "questions": qlist})

    return theory, questions_wrapped


def parse_pdfs_to_data(pdf_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Extract theory and questions from all PDFs in pdf_dir."""
    pdfs = sorted(pdf_dir.glob("*.pdf"))
    if not pdfs:
        return get_fallback_theory_and_questions()

    full_text_parts: list[str] = []
    for pdf in pdfs:
        try:
            full_text_parts.append(_extract_pdf_text(pdf))
        except Exception:
            continue

    full_text = "\n\n".join(full_text_parts).strip()
    if not full_text:
        return get_fallback_theory_and_questions()

    raw_chapters = _split_into_chapters(full_text)
    if not raw_chapters:
        return get_fallback_theory_and_questions()

    theory: list[dict[str, Any]] = []
    questions_wrapped: list[dict[str, Any]] = []

    for cid, (title, body) in enumerate(raw_chapters, start=1):
        chunks = _chunk_text(body)
        theory.append({"id": cid, "title": title[:200], "content_chunks": chunks})
        qs = _questions_for_chapter(body, cid)
        if len(qs) < 3:
            _, fb_q = get_fallback_theory_and_questions()
            if fb_q:
                fb_idx = (cid - 1) % len(fb_q)
                extra = fb_q[fb_idx]["questions"][:5]
                for eq in extra:
                    copy_q = dict(eq)
                    copy_q["id"] = f"c{cid}_q_pad_{len(qs) + 1}"
                    qs.append(copy_q)
        questions_wrapped.append({"chapter_id": cid, "questions": qs[:50]})

    if not theory:
        return get_fallback_theory_and_questions()

    return theory, questions_wrapped


def build_data_files(
    base_dir: Path | None = None,
    force_fallback: bool = False,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Write embedded fallback into data/theory.json and data/questions.json.
    Maintainers with PDFs should run: py scripts/build_data.py
    """
    base = base_dir or Path(__file__).resolve().parent.parent
    data_dir = base / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    if force_fallback:
        theory, questions = get_fallback_theory_and_questions()
    else:
        theory, questions = get_fallback_theory_and_questions()

    theory_path = data_dir / "theory.json"
    questions_path = data_dir / "questions.json"
    theory_path.write_text(json.dumps(theory, indent=2, ensure_ascii=False), encoding="utf-8")
    questions_path.write_text(json.dumps(questions, indent=2, ensure_ascii=False), encoding="utf-8")
    return theory, questions


def load_theory_questions(base_dir: Path | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Load from disk without rebuilding."""
    base = base_dir or Path(__file__).resolve().parent.parent
    data_dir = base / "data"
    t_path = data_dir / "theory.json"
    q_path = data_dir / "questions.json"
    theory = json.loads(t_path.read_text(encoding="utf-8"))
    questions = json.loads(q_path.read_text(encoding="utf-8"))
    return theory, questions
