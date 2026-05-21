"""Routes: /api/chapters and /api/chapters/{id}/*."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.deps import get_pm_for_user, get_theory, get_user_lock

router = APIRouter()


class ChapterSummary(BaseModel):
    id: int
    title: str
    locked: bool
    completed: bool
    score: float | None
    chunk_count: int
    chunk_index: int


class ChapterDetail(BaseModel):
    id: int
    title: str
    content_chunks: list[str]
    chunk_index: int
    chunk_count: int


class ChunkBody(BaseModel):
    index: int


def _find_chapter(chapter_id: int) -> dict:
    theory = get_theory()
    ch = next((c for c in theory if c.get("id") == chapter_id), None)
    if ch is None:
        raise HTTPException(status_code=404, detail=f"Chapter {chapter_id} not found")
    return ch


@router.get("/api/chapters", response_model=list[ChapterSummary])
def list_chapters(user: str = Query(...)) -> list[ChapterSummary]:
    pm = get_pm_for_user(user)
    theory = get_theory()
    result = []
    for ch in theory:
        cid = int(ch["id"])
        result.append(
            ChapterSummary(
                id=cid,
                title=ch.get("title", ""),
                locked=not pm.is_chapter_unlocked(cid),
                completed=cid in pm.state.completed_chapters,
                score=pm.state.scores_per_chapter.get(str(cid)),
                chunk_count=len(ch.get("content_chunks") or []),
                chunk_index=pm.get_theory_chunk(cid),
            )
        )
    return result


@router.get("/api/chapters/{chapter_id}", response_model=ChapterDetail)
def get_chapter(chapter_id: int, user: str = Query(...)) -> ChapterDetail:
    pm = get_pm_for_user(user)
    ch = _find_chapter(chapter_id)
    cid = int(ch["id"])
    chunks = ch.get("content_chunks") or []
    return ChapterDetail(
        id=cid,
        title=ch.get("title", ""),
        content_chunks=chunks,
        chunk_index=pm.get_theory_chunk(cid),
        chunk_count=len(chunks),
    )


@router.post("/api/chapters/{chapter_id}/chunk")
def save_chunk_index(chapter_id: int, body: ChunkBody, user: str = Query(...)) -> dict:
    pm = get_pm_for_user(user)
    lock = get_user_lock(user)
    _find_chapter(chapter_id)
    with lock:
        pm.set_theory_chunk(chapter_id, body.index)
        pm.save()
    return {"ok": True, "chunk_index": body.index}


@router.post("/api/chapters/{chapter_id}/restart")
def restart_chapter(chapter_id: int, user: str = Query(...)) -> dict:
    pm = get_pm_for_user(user)
    lock = get_user_lock(user)
    _find_chapter(chapter_id)
    with lock:
        pm.clear_theory_checkpoint(chapter_id)
        pm.save()
    return {"ok": True}
