"""Convert raw pixel data extracted from PDF to PNG files."""
import sys
from pathlib import Path
from PIL import Image
import io

sys.stdout.reconfigure(encoding="utf-8")

img_dir = Path("scripts/pdf_images")
out_dir = Path("scripts/pdf_images_png")
out_dir.mkdir(exist_ok=True)

# Files of interest (largest image per page = the actual diagram)
targets = [
    # (filename, width, height, label)
    ("page14_R199_1106x546.bin", 1106, 546, "q23_state_transition"),
    ("page15_R208_349x490.bin",  349,  490, "q24_control_flow_graph"),
    ("page19_R244_807x239.bin",  807,  239, "q32_tc_schedule"),
]

for fname, w, h, label in targets:
    path = img_dir / fname
    data = path.read_bytes()
    expected_rgb = w * h * 3
    expected_rgba = w * h * 4
    if len(data) == expected_rgb:
        mode = "RGB"
    elif len(data) == expected_rgba:
        mode = "RGBA"
    else:
        print(f"  SKIP {fname}: size {len(data)} doesn't match RGB({expected_rgb}) or RGBA({expected_rgba})")
        continue

    img = Image.frombytes(mode, (w, h), data)
    out = out_dir / f"{label}.png"
    img.save(str(out))
    print(f"  Saved {out.name}  ({w}x{h} {mode})")
