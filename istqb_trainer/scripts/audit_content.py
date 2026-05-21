"""
Read-only content audit for ISTQB Trainer data files.

Prints a Markdown report to stdout highlighting:
- Questions with inline enumeration markers (the frontend formatter handles
  these at render time, but listing them here lets you spot candidates for
  permanent JSON cleanup).
- Questions / options missing terminal punctuation.
- Theory chunks that are unusually long or have suspicious character sequences.

Run from the `istqb_trainer/` directory:
    py scripts/audit_content.py
    py scripts/audit_content.py > audit_report.md
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_PATH = ROOT / "data" / "questions.json"
THEORY_PATH = ROOT / "data" / "theory.json"

TERMINAL_PUNCT = set(".?!:")

# Enumeration patterns that the display formatter detects and breaks up.
ENUM_PATTERNS = [
    re.compile(r" \d+\. "),                          # numeric:  " 1. "
    re.compile(r"[a-z\d\]:)] [A-Z]\. "),             # uppercase letter: " A. "
    re.compile(r" (?:viii|vii|vi|iv|ix|iii|ii|i|x)\. "),  # roman: " ii. "
]

STEM_RE = re.compile(
    r"(?:Which of the following|Which one of the following|Which BEST"
    r"|What is the BEST|What BEST|Which of these|Identify the|Select the)"
)


def has_enum_marker(text: str) -> bool:
    return any(p.search(text) for p in ENUM_PATTERNS)


def missing_terminal(text: str, min_length: int = 30) -> bool:
    t = text.strip()
    return len(t) >= min_length and t[-1] not in TERMINAL_PUNCT


def suspicious_chars(text: str) -> list[str]:
    issues = []
    if "  " in text:
        issues.append("double space")
    # Windows-1252 / Latin-1 surrogates sometimes appear as replacement chars
    if "\ufffd" in text:
        issues.append("replacement char (U+FFFD)")
    # Detect common Windows-1252 mojibake sequences
    if re.search(r"[â€œâ€™â€"â€"]", text):
        issues.append("possible mojibake")
    return issues


def audit_questions() -> None:
    if not QUESTIONS_PATH.exists():
        print(f"> `{QUESTIONS_PATH}` not found — skipping questions audit.\n")
        return

    data = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    all_q = [q for block in data for q in block.get("questions", [])]

    enum_hits: list[tuple[str, str]] = []
    missing_punct_q: list[tuple[str, str]] = []
    missing_punct_opt: list[tuple[str, str, str]] = []

    for q in all_q:
        qid = q.get("id", "?")
        text = q.get("question", "")

        if has_enum_marker(text) and "\n" not in text:
            enum_hits.append((qid, text[:120] + ("…" if len(text) > 120 else "")))

        if missing_terminal(text):
            missing_punct_q.append((qid, text[-60:]))

        for letter, opt_text in (q.get("options") or {}).items():
            if missing_terminal(opt_text):
                missing_punct_opt.append((qid, letter, opt_text[-60:]))

    print(f"## Questions audit  ({len(all_q)} total)\n")

    print(f"### Inline enumeration markers (no newlines) — {len(enum_hits)} questions\n")
    print("These are handled by the display formatter at render time.\n")
    if enum_hits:
        for qid, preview in enum_hits:
            print(f"- **{qid}**: `{preview}`")
    else:
        print("_None found._")
    print()

    print(f"### Question stems missing terminal punctuation — {len(missing_punct_q)}\n")
    if missing_punct_q:
        for qid, tail in missing_punct_q:
            print(f"- **{qid}**: `…{tail}`")
    else:
        print("_None found._")
    print()

    print(f"### Options missing terminal punctuation — {len(missing_punct_opt)}\n")
    print("(Options under 30 chars are excluded — short fragments are normal.)\n")
    if missing_punct_opt:
        for qid, letter, tail in missing_punct_opt:
            print(f"- **{qid}** option {letter}: `…{tail}`")
    else:
        print("_None found._")
    print()


def audit_theory() -> None:
    if not THEORY_PATH.exists():
        print(f"> `{THEORY_PATH}` not found — skipping theory audit.\n")
        return

    data = json.loads(THEORY_PATH.read_text(encoding="utf-8"))
    chunks_all = [
        (ch.get("id"), ch.get("title", ""), i, chunk)
        for ch in data
        for i, chunk in enumerate(ch.get("content_chunks") or [])
    ]

    long_chunks: list[tuple] = []
    suspect_chars: list[tuple] = []
    no_para_breaks: list[tuple] = []

    for ch_id, title, idx, chunk in chunks_all:
        if len(chunk) > 1500:
            long_chunks.append((ch_id, title, idx, len(chunk)))

        issues = suspicious_chars(chunk)
        if issues:
            suspect_chars.append((ch_id, title, idx, issues))

        # Flag chunks longer than 600 chars that have no paragraph break at all
        if len(chunk) > 600 and "\n\n" not in chunk and "\n" not in chunk:
            no_para_breaks.append((ch_id, title, idx, len(chunk)))

    total = len(chunks_all)
    print(f"## Theory audit  ({total} chunks across {len(data)} chapters)\n")

    print(f"### Unusually long chunks (> 1500 chars) — {len(long_chunks)}\n")
    if long_chunks:
        for ch_id, title, idx, length in long_chunks:
            print(f"- Chapter {ch_id} "{title}", chunk {idx}: {length} chars")
    else:
        print("_None found._")
    print()

    print(f"### Chunks > 600 chars with no paragraph breaks — {len(no_para_breaks)}\n")
    if no_para_breaks:
        for ch_id, title, idx, length in no_para_breaks:
            print(f"- Chapter {ch_id} "{title}", chunk {idx}: {length} chars, no `\\n`")
    else:
        print("_None found._")
    print()

    print(f"### Chunks with suspicious character sequences — {len(suspect_chars)}\n")
    if suspect_chars:
        for ch_id, title, idx, issues in suspect_chars:
            print(f"- Chapter {ch_id} "{title}", chunk {idx}: {', '.join(issues)}")
    else:
        print("_None found._")
    print()


def main() -> None:
    print("# ISTQB Content Audit Report\n")
    print(f"Data directory: `{ROOT / 'data'}`\n")
    print("---\n")
    audit_questions()
    print("---\n")
    audit_theory()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    main()
