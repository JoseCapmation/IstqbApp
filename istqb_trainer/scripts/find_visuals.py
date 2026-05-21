"""Find questions and theory chunks that reference missing visuals."""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

QUESTIONS_FILE = "data/questions.json"
THEORY_FILE = "data/theory.json"

keywords = ["graph", "figure", "diagram", "table", "chart", "flow", "below", "shown", "above", "following"]

q_data = json.loads(open(QUESTIONS_FILE, encoding="utf-8").read())
t_data = json.loads(open(THEORY_FILE, encoding="utf-8").read())

print("=" * 60)
print("QUESTIONS referencing visuals")
print("=" * 60)
total_q = 0
for chapter in q_data:
    cid = chapter.get("chapter_id")
    for qs in chapter.get("questions", []):
        text = qs.get("question", "")
        if any(k in text.lower() for k in keywords):
            total_q += 1
            print(f"\nCh{cid} Q{total_q}:")
            print(f"  {text[:200]}")

print(f"\nTotal questions with visual references: {total_q}")

print()
print("=" * 60)
print("THEORY CHUNKS referencing visuals")
print("=" * 60)
total_t = 0
for ch in t_data:
    cid = ch.get("id")
    for idx, chunk in enumerate(ch.get("content_chunks", [])):
        if any(k in chunk.lower() for k in keywords):
            total_t += 1
            print(f"\nCh{cid} chunk[{idx}]: {chunk[:180]}")

print(f"\nTotal theory chunks with visual references: {total_t}")
