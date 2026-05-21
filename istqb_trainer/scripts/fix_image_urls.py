"""Update image_url fields to use /api/diagrams/ instead of /diagrams/."""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

path = "data/questions.json"
q_data = json.loads(open(path, encoding="utf-8").read())

changed = 0
for chapter in q_data:
    for qs in chapter.get("questions", []):
        url = qs.get("image_url", "")
        if url and url.startswith("/diagrams/"):
            qs["image_url"] = url.replace("/diagrams/", "/api/diagrams/", 1)
            changed += 1
            print(f"  {qs['id']}: {qs['image_url']}")

with open(path, "w", encoding="utf-8") as f:
    json.dump(q_data, f, indent=2, ensure_ascii=False)

print(f"\nUpdated {changed} questions.")
