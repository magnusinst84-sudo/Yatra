"""
backend/api/walkthrough.py
--------------------------
Full walkthrough API:

Teammate's RAG-wired routes:
  GET  /api/walkthrough/places   — List all supported place + era combos.
  POST /api/walkthrough          — RAG + agent generation (no DB, direct response).

B1 Persistence & Image-Gen routes:
  POST /api/walkthrough/start    — Cache-first: check DB, then generate + persist.
  GET  /api/walkthrough/mine     — Authenticated user's saved walkthroughs.
  POST /api/walkthrough/{id}/save   — Claim a walkthrough to user account.
  POST /api/walkthrough/{id}/share  — Generate a public share slug.
  GET  /api/walkthrough/shared/{slug} — Public retrieval by slug.
  GET  /api/walkthrough/{id}/stop/{n} — Polling endpoint for stop image status.
POST /api/walkthrough   — Generate a historical walkthrough for a place + era.
GET  /api/walkthrough/places — List all supported place + era combinations.

The RAG pipeline (retrieval.py) is called synchronously inside a thread pool
so it does not block the async event loop.
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.agent.world_state import generate_world_state
from backend.models import AgentError, ValidationError, WorldState
from backend.rag.retrieval import retrieve
from backend.rag.places import PLACES

from backend.services.image_gen import generate_image_with_fallback
from backend.database.crud import (
    find_walkthrough_by_place_era,
    save_walkthrough,
    get_walkthrough_by_id,
    get_walkthrough_by_slug,
    list_walkthroughs_for_user,
    generate_share_slug,
    update_share_slug,
)
from backend.auth.jwt import get_current_user

router = APIRouter(tags=["walkthrough"])


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------

class WalkthroughRequest(BaseModel):
    place: str
    era: str
    user_uid: str | None = None  # optional — not required for testing


class StartRequest(BaseModel):
    place: str
    era: str
    rag_context: str = ""  # Optional override; if empty, RAG is called automatically


class PlaceOption(BaseModel):
    place: str
    era: str


# ---------------------------------------------------------------------------
# Teammate routes (RAG-wired, direct response, no DB)
# Routes
# ---------------------------------------------------------------------------

@router.get("/walkthrough/places", response_model=list[PlaceOption])
async def list_places() -> list[PlaceOption]:
    """Return all supported place + era combinations."""
    return [PlaceOption(place=p["place"], era=p["era"]) for p in PLACES]


@router.post("/walkthrough", response_model=WorldState)
async def create_walkthrough(req: WalkthroughRequest) -> WorldState:
    """
    Full RAG + generation pipeline (no DB caching — direct generation):
    1. retrieve(place, era)  — dict lookup or Chroma vector search
    2. generate_world_state  — Gemini generates 3-5 stop walkthrough
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

    rag_context: str = await asyncio.to_thread(retrieve, req.place, req.era)

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


# ---------------------------------------------------------------------------
# B1 Persistence, Image-Gen, and Auth routes
# ---------------------------------------------------------------------------

@router.post("/walkthrough/start")
async def start_walkthrough(req: StartRequest):
    """
    Cache-first walkthrough start:
    1. Check MongoDB for a pre-generated walkthrough for this place/era.
    2. If found, return it instantly (fast path).
    3. Otherwise: call RAG, generate via Gemini, generate images via Imagen,
       persist everything, then return.
    """
    # 1. Cache check
    cached = await find_walkthrough_by_place_era(req.place, req.era)
    if cached:
        return cached

    # 2. RAG context (use override if provided, else call retrieve)
    if req.rag_context:
        rag_context = req.rag_context
    else:
        rag_context = await asyncio.to_thread(retrieve, req.place, req.era)

    # 3. Generate world state
    try:
        world_state = await generate_world_state(
            place=req.place,
            era=req.era,
            rag_context=rag_context,
            user_uid="system",
        )
    except (ValidationError, AgentError) as e:
        raise HTTPException(status_code=500, detail=f"Agent generation failed: {e}")

    state_dict = world_state.model_dump(mode="json")

    # 4. Save text-only state first so it's in DB even if image gen is slow
    await save_walkthrough(state_dict)

    # 5. Generate images for each stop and update DB
    for stop in state_dict["stops"]:
        image_url = await generate_image_with_fallback(stop["image_prompt"])
        stop["image_url"] = image_url
        stop["generated"] = True

    # 6. Upsert the full state (with image URLs) into DB
    from backend.database.mongo_client import get_db
    db = get_db()
    await db.walkthroughs.replace_one(
        {"walkthrough_id": state_dict["walkthrough_id"]},
        state_dict,
        upsert=True,
    )

    return state_dict


@router.get("/walkthrough/mine")
async def get_my_walkthroughs(user=Depends(get_current_user)):
    """Fetch all walkthroughs saved by the current authenticated user."""
    return await list_walkthroughs_for_user(user["uid"])


@router.post("/walkthrough/{walkthrough_id}/save")
async def save_user_walkthrough(walkthrough_id: str, user=Depends(get_current_user)):
    """Claim a system-generated walkthrough to the authenticated user's account."""
    db_instance = get_db_safe()
    result = await db_instance.walkthroughs.update_one(
        {"walkthrough_id": walkthrough_id},
        {"$set": {"user_uid": user["uid"]}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Walkthrough not found")
    return {"status": "saved", "walkthrough_id": walkthrough_id}


@router.post("/walkthrough/{walkthrough_id}/share")
async def share_walkthrough(walkthrough_id: str, user=Depends(get_current_user)):
    """Generate a shareable public slug for a walkthrough owned by the user."""
    wt = await get_walkthrough_by_id(walkthrough_id)
    if not wt:
        raise HTTPException(status_code=404, detail="Walkthrough not found")

    if wt.get("user_uid") != user["uid"]:
        raise HTTPException(status_code=403, detail="Not authorized to share this walkthrough")

    if not wt.get("share_slug"):
        slug = generate_share_slug()
        await update_share_slug(walkthrough_id, slug)
        wt["share_slug"] = slug

    return {"share_slug": wt["share_slug"]}


@router.get("/walkthrough/shared/{slug}")
async def get_shared_walkthrough(slug: str):
    """Retrieve a walkthrough by its public share slug (no auth required)."""
    wt = await get_walkthrough_by_slug(slug)
    if not wt:
        raise HTTPException(status_code=404, detail="Shared walkthrough not found")
    return wt


@router.get("/walkthrough/{walkthrough_id}/stop/{n}")
async def poll_stop_status(walkthrough_id: str, n: int):
    """Polling endpoint — check whether stop N has finished generating its image."""
    wt = await get_walkthrough_by_id(walkthrough_id)
    if not wt:
        raise HTTPException(status_code=404, detail="Walkthrough not found")

    if n < 0 or n >= len(wt["stops"]):
        raise HTTPException(status_code=400, detail="Invalid stop index")

    stop = wt["stops"][n]
    return {
        "generated": stop.get("generated", False),
        "image_url": stop.get("image_url"),
    }


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def get_db_safe():
    from backend.database.mongo_client import get_db
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    return db
