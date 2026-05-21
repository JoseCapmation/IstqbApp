"""Extract images from the ISTQB Guru questions PDF."""
import sys
from pathlib import Path
from pypdf import PdfReader
from PIL import Image
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

PDF = Path("samplePdfs/500-ISTQB-Sample-Papers_Questions_istqb.guru.pdf")
OUT = Path("scripts/guru_images")
OUT.mkdir(exist_ok=True)

reader = PdfReader(str(PDF))
print(f"PDF has {len(reader.pages)} pages")

for page_num, page in enumerate(reader.pages, start=1):
    # Only process pages around guru_1 (p~1-5), guru_13 (p~13-17), guru_39 (p~39-43)
    # We'll extract everything first then filter
    if "/Resources" not in page:
        continue
    resources = page["/Resources"]
    if "/XObject" not in resources:
        continue
    xobjects = resources["/XObject"].get_object()
    for name, obj in xobjects.items():
        obj = obj.get_object()
        if obj.get("/Subtype") != "/Image":
            continue
        w = obj.get("/Width", 0)
        h = obj.get("/Height", 0)
        # Skip tiny images (logos etc.)
        if w * h < 50000:
            continue
        data = obj.get_data()
        arr = np.frombuffer(data, dtype=np.uint8)
        # Try to decode
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            out = OUT / f"page{page_num:03d}_{name.lstrip('/')}_{w}x{h}.png"
            out.write_bytes(data)
            print(f"  Page {page_num}: PNG {out.name}")
        elif data[:3] == b"\xff\xd8\xff":
            out = OUT / f"page{page_num:03d}_{name.lstrip('/')}_{w}x{h}.jpg"
            out.write_bytes(data)
            print(f"  Page {page_num}: JPG {out.name}")
        elif len(data) == w * h:
            img = Image.frombytes("L", (w, h), data)
            img = img.point(lambda x: 255 - x)  # invert
            out = OUT / f"page{page_num:03d}_{name.lstrip('/')}_{w}x{h}_gray_inv.png"
            img.save(str(out))
            print(f"  Page {page_num}: raw-gray-inv {out.name}")
        elif len(data) == w * h * 3:
            img = Image.frombytes("RGB", (w, h), data)
            out = OUT / f"page{page_num:03d}_{name.lstrip('/')}_{w}x{h}_rgb.png"
            img.save(str(out))
            print(f"  Page {page_num}: raw-RGB {out.name}")

print(f"\nDone — images in {OUT}")
