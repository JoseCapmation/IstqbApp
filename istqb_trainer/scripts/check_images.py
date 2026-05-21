"""Check what format the extracted bin images are and rename them."""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

img_dir = Path("scripts/pdf_images")

pages_of_interest = {14, 15, 19}  # Q23, Q24, Q32

for f in sorted(img_dir.glob("*.bin")):
    page_num = int(f.name[4:6])
    if page_num not in pages_of_interest:
        continue
    data = f.read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        fmt = "png"
    elif data[:3] == b"\xff\xd8\xff":
        fmt = "jpg"
    elif data[:4] == b"RIFF":
        fmt = "webp"
    else:
        fmt = f"unknown({data[:4].hex()})"
    print(f"  {f.name}: {fmt}  ({len(data)} bytes)")
