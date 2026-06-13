"""Unified search API wrappers for Phase 1."""
from __future__ import annotations

from backend.app.services.retrieval.retrieval_manager import search_visual

try:  # pragma: no cover - depends on optional API runtime.
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel, Field
except ImportError:  # pragma: no cover
    APIRouter = None
    HTTPException = None
    BaseModel = object
    Field = None


if APIRouter is not None:
    router = APIRouter(prefix="/search", tags=["search"])

    class SearchBody(BaseModel):
        query: str
        mode: str = "visual"
        top_k: int = Field(default=20, ge=1, le=200)

    @router.post("")
    def search_endpoint(body: SearchBody) -> dict:
        if body.mode not in {"visual", "image", "baseline"}:
            raise HTTPException(
                status_code=400,
                detail="Phase 1 supports mode='visual' only.",
            )
        try:
            return {
                "success": True,
                "data": search_visual(body.query, body.top_k).to_dict(),
                "message": None,
            }
        except Exception as exc:  # noqa: BLE001 - convert service errors to API response.
            raise HTTPException(status_code=500, detail=str(exc)) from exc
else:
    router = None


def search(query: str, top_k: int = 20, mode: str = "visual") -> dict:
    if mode not in {"visual", "image", "baseline"}:
        raise ValueError("Phase 1 supports mode='visual' only.")
    return search_visual(query=query, top_k=top_k).to_dict()
