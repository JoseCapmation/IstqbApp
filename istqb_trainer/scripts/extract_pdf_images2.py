"""Extract images from ISTQB PDF using pdfplumber/pypdf."""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from pypdf import PdfReader

PDF = Path("samplePdfs/ISTQB_CTFL_v4.0_Sample-Exam-C-Questions_v1.6.pdf")
OUT = Path("scripts/pdf_images")
OUT.mkdir(exist_ok=True)

reader = PdfReader(str(PDF))
print(f"PDF has {len(reader.pages)} pages")

for page_num, page in enumerate(reader.pages, start=1):
    if "/Resources" not in page:
        continue
    resources = page["/Resources"]
    if "/XObject" not in resources:
        continue
    xobjects = resources["/XObject"].get_object()
    for name, obj in xobjects.items():
        obj = obj.get_object()
        if obj.get("/Subtype") == "/Image":
            w = obj.get("/Width", 0)
            h = obj.get("/Height", 0)
            data = obj.get_data()
            # Detect format
            if data[:3] == b"\xff\xd8\xff":
                ext = "jpg"
            elif data[:8] == b"\x89PNG\r\n\x1a\n":
                ext = "png"
            else:
                ext = "bin"
            out_file = OUT / f"page{page_num:02d}_{name.lstrip('/')}_{w}x{h}.{ext}"
            out_file.write_bytes(data)
            print(f"  Page {page_num}: {out_file.name}")

print(f"\nDone — images in {OUT}")
