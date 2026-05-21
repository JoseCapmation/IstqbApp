"""Crop the bar chart out of the rendered Q31 PDF page and save as PNG."""
import sys
from pathlib import Path
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

# The rendered page is at 150 DPI — page dimensions are ~8.27 x 11.69 in
# At 150 DPI: 1241 x 1754 px approx
img = Image.open("scripts/pdf_images_png/q31_bar_chart.png")
w, h = img.size
print(f"Full page size: {w} x {h}")

# The chart (title + bars + legend) spans approximately:
# top ~40%, bottom ~72%, left 10%, right 90% of the page
top    = int(h * 0.37)
bottom = int(h * 0.555)
left   = int(w * 0.08)
right  = int(w * 0.96)

chart = img.crop((left, top, right, bottom))
print(f"Cropped chart: {chart.size}")

out = Path("data/diagrams/iteration-effort-chart.png")
chart.save(str(out))
print(f"Saved: {out}")
