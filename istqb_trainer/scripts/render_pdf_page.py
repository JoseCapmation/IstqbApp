"""Render a specific PDF page to PNG using pdfplumber (which uses pdfminer under the hood)
   and pillow for cropping."""
import sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

import pdfplumber
from PIL import Image
import io

PDF  = Path("samplePdfs/ISTQB_CTFL_v4.0_Sample-Exam-C-Questions_v1.6.pdf")
OUT  = Path("scripts/pdf_images_png")
OUT.mkdir(exist_ok=True)

# Q31 is on page 18 of 21 (document) = PDF page index 17 (0-based, after cover/copyright/etc)
# The PDF has pages: cover(0), copyright(1), revision(2), toc(3), intro(4), Q1-Q4(5), ...
# Q31 is on document page 18 which = PDF index 17

TARGET_PAGES = {17: "q31_bar_chart", 18: "q32_tc_schedule_page"}

with pdfplumber.open(str(PDF)) as pdf:
    print(f"PDF has {len(pdf.pages)} pages")
    for page_idx, label in TARGET_PAGES.items():
        page = pdf.pages[page_idx]
        # render at 150 DPI
        img = page.to_image(resolution=150)
        out_path = OUT / f"{label}.png"
        img.save(str(out_path))
        print(f"  Saved page {page_idx} -> {out_path.name}")

print("Done")
