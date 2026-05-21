"""Extract images from the ISTQB Sample Exam C PDF, one file per page."""
import fitz  # PyMuPDF
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

PDF = Path("samplePdfs/ISTQB_CTFL_v4.0_Sample-Exam-C-Questions_v1.6.pdf")
OUT = Path("scripts/pdf_images")
OUT.mkdir(exist_ok=True)

doc = fitz.open(str(PDF))

print(f"PDF has {len(doc)} pages")
for page_num, page in enumerate(doc, start=1):
    images = page.get_images(full=True)
    for img_idx, img_info in enumerate(images):
        xref = img_info[0]
        base_image = doc.extract_image(xref)
        ext = base_image["ext"]
        img_bytes = base_image["image"]
        w, h = base_image["width"], base_image["height"]
        filename = OUT / f"page{page_num:02d}_img{img_idx+1:02d}_{w}x{h}.{ext}"
        filename.write_bytes(img_bytes)
        print(f"  Page {page_num}: saved {filename.name} ({w}x{h})")

print(f"\nDone — images saved to {OUT}")
