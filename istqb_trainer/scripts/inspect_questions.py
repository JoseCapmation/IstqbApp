import json, sys
sys.stdout.reconfigure(encoding="utf-8")
q = json.loads(open("data/questions.json", encoding="utf-8").read())

# Structure of first question
print("=== First question structure ===")
print(json.dumps(q[0]["questions"][0], indent=2, ensure_ascii=False))

# Ch4 questions
print("\n=== Ch4 questions ===")
for ch in q:
    if ch.get("chapter_id") == 4:
        for i, qs in enumerate(ch.get("questions", [])):
            print(f"idx={i}: {qs.get('question','')[:100]}")

# Ch5 questions
print("\n=== Ch5 questions ===")
for ch in q:
    if ch.get("chapter_id") == 5:
        for i, qs in enumerate(ch.get("questions", [])):
            print(f"idx={i}: {qs.get('question','')[:100]}")
