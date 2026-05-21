"""Patch questions.json to add image_url for diagram questions."""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

DIAGRAM_MAP = {
    "examC_23": "/diagrams/state-transition-ctfl.svg",
    "examC_24": "/diagrams/cfg-branch.svg",
    "examC_32": "/diagrams/tc-schedule.svg",
    "guru_1":   "/diagrams/state-table-atm.svg",
    "guru_13":  "/diagrams/state-diagram-webshop.svg",
    "guru_39":  "/diagrams/code-paths.svg",
}

path = "data/questions.json"
q_data = json.loads(open(path, encoding="utf-8").read())

patched = 0
for chapter in q_data:
    for qs in chapter.get("questions", []):
        qid = qs.get("id", "")
        if qid in DIAGRAM_MAP:
            qs["image_url"] = DIAGRAM_MAP[qid]
            patched += 1
            print(f"  Patched {qid} → {DIAGRAM_MAP[qid]}")

with open(path, "w", encoding="utf-8") as f:
    json.dump(q_data, f, indent=2, ensure_ascii=False)

print(f"\nDone — {patched} questions patched.")
