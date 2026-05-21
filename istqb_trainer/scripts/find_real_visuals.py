"""Find questions that truly require a diagram/table/graph to answer."""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

QUESTIONS_FILE = "data/questions.json"
q_data = json.loads(open(QUESTIONS_FILE, encoding="utf-8").read())

# These phrases indicate a visual that MUST be seen to answer the question
real_visual_phrases = [
    "control flow graph",
    "state transition diagram",
    "state transition table",
    "decision table",
    "the following figure",
    "the above diagram",
    "the following diagram",
    "shown in the diagram",
    "shown above",
    "exhibit",
    "following table",
    "following decision table",
    "the following state",
]

hits = []
for chapter in q_data:
    cid = chapter.get("chapter_id")
    for qs in chapter.get("questions", []):
        text = qs.get("question", "").lower()
        for phrase in real_visual_phrases:
            if phrase in text:
                hits.append({
                    "chapter": cid,
                    "question": qs.get("question", ""),
                    "options": qs.get("options", {}),
                    "answer": qs.get("answer", ""),
                    "phrase": phrase,
                })
                break

print(f"Questions truly needing a visual: {len(hits)}\n")
for i, h in enumerate(hits, 1):
    print(f"{'='*70}")
    print(f"#{i} Ch{h['chapter']} | trigger: '{h['phrase']}'")
    print(f"Q: {h['question']}")
    print(f"Options: {h['options']}")
    print(f"Answer: {h['answer']}")
