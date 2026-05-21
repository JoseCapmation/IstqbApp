"""Clean up examC_31 question text: remove the placeholder note."""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

path = Path("data/questions.json")
data = json.loads(path.read_text(encoding="utf-8"))

for chapter in data:
    for q in chapter.get("questions", []):
        if q.get("id") == "examC_31":
            old = q["question"]
            new = old.replace(
                " (see official Sample Exam C for the figure)", ""
            )
            q["question"] = new
            print("Old:", old[:120])
            print("New:", new[:120])

path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("Saved.")
