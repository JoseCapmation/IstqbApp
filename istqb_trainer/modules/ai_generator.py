"""
Optional LLM-generated MCQs for practice when the bank is thin.
Supports OpenAI, Anthropic, Ollama, or none (disabled).
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx

VALID_KEYS = frozenset("ABCD")


def _provider() -> str:
    return (os.environ.get("AI_PROVIDER") or "none").strip().lower()


def _validate_question(obj: dict[str, Any]) -> dict[str, Any] | None:
    opts = obj.get("options") or {}
    if not all(k in opts for k in "ABCD"):
        return None
    c = str(obj.get("correct", "A")).upper()
    if c not in VALID_KEYS:
        return None
    q = str(obj.get("question", "")).strip()
    if len(q) < 10:
        return None
    return {
        "id": str(obj.get("id", "ai_q")),
        "question": q,
        "options": {k: str(opts[k]).strip() for k in "ABCD"},
        "correct": c,
        "explanation": obj.get("explanation"),
    }


def _parse_json_array(text: str) -> list[dict[str, Any]]:
    text = text.strip()
    m = re.search(r"\[[\s\S]*\]", text)
    if not m:
        return []
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [x for x in data if isinstance(x, dict)]


def _call_openai(prompt: str) -> str:
    from openai import OpenAI

    client = OpenAI()
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    r = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You output only valid JSON: an array of MCQ objects.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )
    return r.choices[0].message.content or ""


def _call_anthropic(prompt: str) -> str:
    import anthropic

    client = anthropic.Anthropic()
    model = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")
    msg = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    parts = msg.content
    if not parts:
        return ""
    block = parts[0]
    return getattr(block, "text", str(block))


def _call_ollama(prompt: str) -> str:
    base = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
    model = os.environ.get("OLLAMA_MODEL", "llama3.2")
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.4},
    }
    with httpx.Client(timeout=120.0) as client:
        r = client.post(f"{base}/api/generate", json=payload)
        r.raise_for_status()
        data = r.json()
    return data.get("response", "")


def generate_extra_questions(
    chapter_title: str,
    theory_excerpt: str,
    count: int,
    chapter_id: int,
    start_index: int,
) -> list[dict[str, Any]]:
    """
    Return up to `count` validated MCQ dicts, or empty list if disabled / error.
    """
    prov = _provider()
    if prov in ("", "none", "disabled"):
        return []

    need = max(1, min(count, 8))
    prompt = f"""Create exactly {need} ISTQB Foundation Level style multiple-choice questions about this chapter.

Chapter: {chapter_title}

Theory excerpt:
{theory_excerpt[:6000]}

Return ONLY a JSON array (no markdown) of objects with this shape:
[
  {{
    "question": "string",
    "options": {{"A":"...","B":"...","C":"...","D":"..."}},
    "correct": "A"|"B"|"C"|"D",
    "explanation": "short string why the answer is correct"
  }}
]
"""

    try:
        if prov == "openai":
            if not os.environ.get("OPENAI_API_KEY"):
                return []
            raw = _call_openai(prompt)
        elif prov == "anthropic":
            if not os.environ.get("ANTHROPIC_API_KEY"):
                return []
            raw = _call_anthropic(prompt)
        elif prov == "ollama":
            raw = _call_ollama(prompt)
        else:
            return []
    except Exception:
        return []

    items = _parse_json_array(raw)
    out: list[dict[str, Any]] = []
    for i, obj in enumerate(items):
        obj = dict(obj)
        obj["id"] = f"c{chapter_id}_ai_{start_index + i}"
        v = _validate_question(obj)
        if v:
            out.append(v)
        if len(out) >= need:
            break
    return out
