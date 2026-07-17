"""
backend/api/walkthrough.py
--------------------------
POST /api/walkthrough   — Generate a historical walkthrough for a place + era.
GET  /api/walkthrough/places — List all supported place + era combinations.

The RAG pipeline (retrieval.py) is called synchronously inside a thread pool
so it does not block the async event loop.
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.agent.world_state import generate_world_state
from backend.models import AgentError, ValidationError, WorldState
from backend.rag.retrieval import retrieve
from backend.rag.places import PLACES

router = APIRouter(tags=["walkthrough"])


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------

class WalkthroughRequest(BaseModel):
    place: str
    era: str
    user_uid: str | None = None  # optional — not required for testing


class PlaceOption(BaseModel):
    place: str
    era: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/walkthrough/places", response_model=list[PlaceOption])
async def list_places() -> list[PlaceOption]:
    """Return all supported place + era combinations."""
    return [PlaceOption(place=p["place"], era=p["era"]) for p in PLACES]


@router.post("/walkthrough", response_model=WorldState)
async def create_walkthrough(req: WalkthroughRequest) -> WorldState:
    """
    Full RAG + generation pipeline:
    1. retrieve(place, era)  — dict lookup or Chroma vector search
    2. generate_world_state  — Gemini generates 3-5 stop walkthrough
    """
    # Validate place+era against the known list
    known = {(p["place"], p["era"]) for p in PLACES}
    if (req.place, req.era) not in known:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unknown place+era: '{req.place}' / '{req.era}'. "
                "Call GET /api/walkthrough/places to see valid options."
            ),
        )

    # RAG retrieval (sync I/O — run in thread pool)
    rag_context: str = await asyncio.to_thread(retrieve, req.place, req.era)

    # Generation
    try:
        world_state = await generate_world_state(
            place=req.place,
            era=req.era,
            rag_context=rag_context,
            user_uid=req.user_uid,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except AgentError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return world_state
