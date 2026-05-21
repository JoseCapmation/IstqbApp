"""Add image_url to examC_31 in questions.json."""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

path = Path("data/questions.json")
data = json.loads(path.read_text(encoding="utf-8"))

patched = False
for chapter in data:
    for q in chapter.get("questions", []):
        if q.get("id") == "examC_31":
            q["image_url"] = "/api/diagrams/iteration-effort-chart.svg"
            patched = True
            print(f"Patched: {q['id']} -> {q['image_url']}")

if patched:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Saved questions.json")
else:
    print("ERROR: examC_31 not found")
