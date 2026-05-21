"""Try different interpretations of the raw PDF image data."""
import sys
from pathlib import Path
from PIL import Image, ImageOps
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

img_dir = Path("scripts/pdf_images")
out_dir = Path("scripts/pdf_images_png")
out_dir.mkdir(exist_ok=True)

def try_variants(fname, w, h, label):
    path = img_dir / fname
    data = path.read_bytes()
    arr = np.frombuffer(data, dtype=np.uint8)

    variants = []
    # Try grayscale (w*h bytes)
    if len(data) == w * h:
        img = Image.frombytes("L", (w, h), data)
        variants.append(("gray", img))
        variants.append(("gray_inv", ImageOps.invert(img)))

    # Try RGB
    if len(data) == w * h * 3:
        img = Image.frombytes("RGB", (w, h), data)
        variants.append(("rgb", img))
        # Try BGR
        arr3 = arr.reshape(h, w, 3)
        bgr = arr3[:, :, ::-1]
        variants.append(("bgr", Image.fromarray(bgr)))
        # Try inverted
        variants.append(("rgb_inv", ImageOps.invert(img)))

    for vname, img in variants:
        out = out_dir / f"{label}_{vname}.png"
        img.save(str(out))
        print(f"  Saved {out.name}")

# Q23 state transition - try the smaller 1106x546 (alpha/mask?) + larger
try_variants("page14_R198_1106x546.bin", 1106, 546, "q23")
try_variants("page14_R199_1106x546.bin", 1106, 546, "q23b")

# Q24 control flow graph
try_variants("page15_R207_349x490.bin", 349, 490, "q24")
try_variants("page15_R208_349x490.bin", 349, 490, "q24b")

# Q32 tc schedule
try_variants("page19_R243_807x239.bin", 807, 239, "q32")
try_variants("page19_R244_807x239.bin", 807, 239, "q32b")
