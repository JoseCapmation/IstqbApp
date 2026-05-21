"""Find exact question IDs for the 6 questions that need diagrams."""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

q_data = json.loads(open("data/questions.json", encoding="utf-8").read())

needs_diagram = [
    "state transition diagram",
    "control flow graph",
    "the following figure",
    "state transition table",
    "the above diagram",
]

for chapter in q_data:
    cid = chapter.get("chapter_id")
    for qs in chapter.get("questions", []):
        text = qs.get("question", "").lower()
        for phrase in needs_diagram:
            if phrase in text:
                print(f'Ch{cid} | id={qs["id"]} | phrase="{phrase}"')
                print(f'  Q: {qs["question"][:150]}')
                print(f'  Opts: {qs["options"]}')
                print(f'  Answer: {qs.get("correct","")}')
                print()
                break
