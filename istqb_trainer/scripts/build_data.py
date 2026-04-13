"""
Maintainer-only: regenerate data from samplePdfs (or PDF_DIR).

  py scripts/build_data.py
    Rebuilds questions from PDFs; keeps existing data/theory.json (curated study text) by default.

  py scripts/build_data.py --theory-from-pdf
    Also rebuilds theory from the syllabus PDF (overwrites curated theory).

  py scripts/build_data.py --dump-syllabus-text
    Writes data/_syllabus_extracted.txt only (no JSON write).

Requires PDFs under istqb_trainer/samplePdfs (or PDF_DIR in .env).
End users do not run this; they use prebuilt JSON shipped with the app.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from modules.content_build import build_from_pdf_dir, dump_syllabus_text, write_data_files
from modules.pdf_parser import _default_pdf_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build questions.json from PDFs; preserve curated theory.json unless --theory-from-pdf.",
    )
    parser.add_argument(
        "--theory-from-pdf",
        action="store_true",
        help="Rebuild theory.json from the syllabus PDF (default: keep existing data/theory.json).",
    )
    parser.add_argument(
        "--dump-syllabus-text",
        action="store_true",
        help="Write data/_syllabus_extracted.txt for QA (no JSON write).",
    )
    args = parser.parse_args()

    pdf_dir = _default_pdf_dir(ROOT)
    if not pdf_dir.is_dir():
        print(f"PDF folder not found: {pdf_dir}")
        sys.exit(1)

    if args.dump_syllabus_text:
        out = ROOT / "data" / "_syllabus_extracted.txt"
        out.parent.mkdir(parents=True, exist_ok=True)
        dump_syllabus_text(pdf_dir, out)
        print(f"Wrote {out}")
        return

    theory, questions = build_from_pdf_dir(
        pdf_dir,
        theory_from_pdf=args.theory_from_pdf,
        base_dir=ROOT,
    )
    write_data_files(ROOT, theory, questions)
    nq = sum(len(b.get("questions") or []) for b in questions)
    print(f"Wrote data/theory.json ({len(theory)} chapters) and data/questions.json ({nq} questions).")


if __name__ == "__main__":
    main()
