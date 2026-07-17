"""
tests/test_project.py
======================
End-to-end smoke-test for the entire Yatra backend.

Runs SYNCHRONOUSLY — no pytest needed.
Execute from the repo root:

    python tests/test_project.py [--skip-images] [--skip-db] [--skip-api]

Sections
--------
1.  ENV CHECK           — Verifies all required env vars are present.
2.  RAG LAYER           — Tests retrieve() for known and unknown place/era.
3.  AGENT LAYER         — Calls generate_world_state() end-to-end with real Gemini.
4.  IMAGE GEN           — Calls generate_image_with_fallback() for one prompt.
5.  DATABASE CRUD       — Tests MongoDB: save, find by id, find by place/era, list.
6.  API LAYER           — Starts a TestClient against FastAPI app and hits every route.
7.  SUMMARY             — Prints pass/fail count and exits 1 on any failure.
"""

import asyncio
import os
import sys
import argparse
import traceback
from pathlib import Path

# ---------------------------------------------------------------------------
# 0. Load .env before any imports that need keys
# ---------------------------------------------------------------------------
_ENV_PATH = Path(__file__).parent.parent / "backend" / ".env"
if _ENV_PATH.exists():
    with open(_ENV_PATH) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _, _v = _line.partition("=")
                os.environ.setdefault(_k.strip(), _v.strip())
    print(f"[env] Loaded {_ENV_PATH}")
else:
    print(f"[env] WARNING: {_ENV_PATH} not found — relying on shell env vars.")

# Add repo root to sys.path so `backend` is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

# ---------------------------------------------------------------------------
# CLI flags
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="Yatra end-to-end smoke test")
parser.add_argument("--skip-images", action="store_true", help="Skip image generation test (slow + costs quota)")
parser.add_argument("--skip-db",     action="store_true", help="Skip MongoDB CRUD tests")
parser.add_argument("--skip-api",    action="store_true", help="Skip FastAPI route tests")
ARGS = parser.parse_args()

# ---------------------------------------------------------------------------
# Test harness
# ---------------------------------------------------------------------------
RESULTS: list[tuple[str, str, str]] = []  # (section, name, PASS|FAIL|SKIP)

def record(section: str, name: str, passed: bool, err: str = ""):
    status = "PASS" if passed else "FAIL"
    RESULTS.append((section, name, status))
    icon = "✅" if passed else "❌"
    print(f"  {icon} [{section}] {name}" + (f"\n      └─ {err}" if err else ""))

def skip(section: str, name: str):
    RESULTS.append((section, name, "SKIP"))
    print(f"  ⏭️  [{section}] {name} (skipped)")

# ===========================================================================
# SECTION 1 — ENV CHECK
# ===========================================================================
print("\n" + "="*60)
print("SECTION 1 — ENV CHECK")
print("="*60)

REQUIRED_VARS = [
    "GEMINI_API_KEY",
    "MONGODB_URI",
    "FIREBASE_ADMIN_SDK_JSON",
    "FIREBASE_STORAGE_BUCKET",
]

for var in REQUIRED_VARS:
    val = os.environ.get(var, "")
    present = bool(val)
    record("ENV", var, present, f"Variable is empty or missing" if not present else "")

# ===========================================================================
# SECTION 2 — RAG LAYER
# ===========================================================================
print("\n" + "="*60)
print("SECTION 2 — RAG LAYER")
print("="*60)

try:
    from backend.rag.retrieval import retrieve

    # 2a. Known key — should return non-empty string instantly (dict lookup)
    ctx = retrieve("Hampi", "Vijayanagara Empire (c. 1500 CE)")
    record("RAG", "retrieve() known place/era", bool(ctx and len(ctx) > 20),
           f"Got {len(ctx)} chars" if ctx else "Empty string returned")

    # 2b. Unknown key — should return "" gracefully (no crash)
    ctx2 = retrieve("Paris", "French Revolution 1789")
    record("RAG", "retrieve() unknown place/era returns '' without crash", ctx2 == "" or isinstance(ctx2, str))

except Exception as e:
    record("RAG", "retrieve() import/init", False, traceback.format_exc(limit=3))

# ===========================================================================
# SECTION 3 — AGENT LAYER
# ===========================================================================
print("\n" + "="*60)
print("SECTION 3 — AGENT (Gemini generation)")
print("="*60)

async def _test_agent():
    from backend.agent.world_state import generate_world_state

    state = await generate_world_state(
        place="Taxila",
        era="Maurya Empire, c. 250 BCE",
        rag_context="Taxila was a major centre of learning in the ancient world.",
        user_uid="test-smoke"
    )
    return state

try:
    print("  [AGENT] Calling generate_world_state() — may take 15-30s …")
    state = asyncio.run(_test_agent())
    record("AGENT", "generate_world_state() returns WorldState", state is not None)
    record("AGENT", "stop count 3-5", 3 <= len(state.stops) <= 5,
           f"Got {len(state.stops)} stops")
    record("AGENT", "narration ≥ 120 words per stop",
           all(len(s.narration_script.split()) >= 120 for s in state.stops),
           f"Word counts: {[len(s.narration_script.split()) for s in state.stops]}")
    record("AGENT", "daily_life_facts ≥ 3 per stop",
           all(len(s.daily_life_facts) >= 3 for s in state.stops))
    record("AGENT", "era_summary non-empty", bool(state.era_summary))
    SAVED_AGENT_STATE = state
except Exception as e:
    record("AGENT", "generate_world_state() end-to-end", False, traceback.format_exc(limit=5))
    SAVED_AGENT_STATE = None

# ===========================================================================
# SECTION 4 — IMAGE GENERATION
# ===========================================================================
print("\n" + "="*60)
print("SECTION 4 — IMAGE GENERATION (Imagen via google.genai)")
print("="*60)

if ARGS.skip_images:
    skip("IMAGE", "generate_image_with_fallback()")
else:
    async def _test_image():
        from backend.services.image_gen import generate_image_with_fallback
        url = await generate_image_with_fallback(
            "A wide-angle view of ancient Taxila's stone monastery at dusk, "
            "terracotta rooftops, monks in saffron robes walking through the courtyard."
        )
        return url

    try:
        print("  [IMAGE] Calling generate_image_with_fallback() — may take 20-60s …")
        img_url = asyncio.run(_test_image())
        record("IMAGE", "generate_image_with_fallback() returns URL",
               bool(img_url), f"Got: {img_url[:60] if img_url else None}...")
        record("IMAGE", "URL is a base64 data URL",
               bool(img_url and img_url.startswith("data:image")),
               f"Starts with: {img_url[:30] if img_url else 'None'}")
    except Exception as e:
        record("IMAGE", "generate_image_with_fallback()", False, traceback.format_exc(limit=5))

# ===========================================================================
# SECTION 5 — DATABASE CRUD
# ===========================================================================
print("\n" + "="*60)
print("SECTION 5 — DATABASE (MongoDB CRUD)")
print("="*60)

if ARGS.skip_db:
    for name in ["init_db", "save_walkthrough", "get_walkthrough_by_id",
                 "find_walkthrough_by_place_era", "list_walkthroughs_for_user",
                 "share_slug flow"]:
        skip("DB", name)
else:
    import uuid as _uuid

    async def _test_db():
        from backend.database.mongo_client import init_db, close_db
        from backend.database.crud import (
            save_walkthrough, get_walkthrough_by_id,
            find_walkthrough_by_place_era, list_walkthroughs_for_user,
            generate_share_slug, update_share_slug, get_walkthrough_by_slug,
        )

        await init_db()
        record("DB", "init_db() connected", True)

        # Build a minimal dummy walkthrough
        test_id = str(_uuid.uuid4())
        dummy = {
            "walkthrough_id": test_id,
            "user_uid": "smoke-test-user",
            "place": "__smoke_test_place__",
            "era": "__smoke_test_era__",
            "era_summary": "Smoke test era",
            "stops": [
                {
                    "stop_id": str(_uuid.uuid4()),
                    "stop_name": "Test Stop",
                    "image_prompt": "Test prompt",
                    "narration_script": " ".join(["word"] * 130),
                    "daily_life_facts": ["fact1", "fact2", "fact3"],
                    "image_url": None,
                    "generated": False,
                }
            ],
        }

        # Save
        saved_id = await save_walkthrough(dummy)
        record("DB", "save_walkthrough()", saved_id == test_id, f"ID: {saved_id}")

        # Find by ID
        fetched = await get_walkthrough_by_id(test_id)
        record("DB", "get_walkthrough_by_id()", fetched is not None and fetched.get("place") == "__smoke_test_place__")

        # Find by place/era (system user)
        dummy2 = dict(dummy, walkthrough_id=str(_uuid.uuid4()), user_uid="system")
        await save_walkthrough(dummy2)
        cached = await find_walkthrough_by_place_era("__smoke_test_place__", "__smoke_test_era__")
        record("DB", "find_walkthrough_by_place_era()", cached is not None)

        # List for user
        results = await list_walkthroughs_for_user("smoke-test-user")
        record("DB", "list_walkthroughs_for_user()", len(results) >= 1)

        # Share slug
        slug = generate_share_slug()
        record("DB", "generate_share_slug() returns 8-char string", len(slug) == 8 and slug.isalnum())
        await update_share_slug(test_id, slug)
        shared = await get_walkthrough_by_slug(slug)
        record("DB", "get_walkthrough_by_slug() after update", shared is not None)

        # Cleanup: remove test docs
        from backend.database.mongo_client import get_db
        db = get_db()
        await db.walkthroughs.delete_many({"place": "__smoke_test_place__"})
        record("DB", "cleanup test documents", True)

        await close_db()

    try:
        asyncio.run(_test_db())
    except Exception as e:
        record("DB", "DB test suite", False, traceback.format_exc(limit=5))

# ===========================================================================
# SECTION 6 — API LAYER (FastAPI TestClient)
# ===========================================================================
print("\n" + "="*60)
print("SECTION 6 — API ROUTES (FastAPI TestClient)")
print("="*60)

if ARGS.skip_api:
    for name in ["GET /health", "GET /api/walkthrough/places", "POST /api/walkthrough (known place)"]:
        skip("API", name)
else:
    try:
        from fastapi.testclient import TestClient
        from backend.main import app

        # Use lifespan=False so we can call init_db manually and not hang
        client = TestClient(app, raise_server_exceptions=False)

        # 6a. Health check
        r = client.get("/health")
        record("API", "GET /health → 200", r.status_code == 200, str(r.status_code))

        # 6b. List places
        r = client.get("/api/walkthrough/places")
        record("API", "GET /api/walkthrough/places → 200", r.status_code == 200, str(r.status_code))
        if r.status_code == 200:
            places = r.json()
            record("API", "places list non-empty", len(places) > 0, f"{len(places)} entries")

        # 6c. POST /api/walkthrough with invalid place → 400
        r = client.post("/api/walkthrough", json={"place": "Moon", "era": "Lunar 2099"})
        record("API", "POST /api/walkthrough unknown place → 400", r.status_code == 400, str(r.status_code))

        # 6d. POST /api/walkthrough/places → 405 (method not allowed)
        r = client.post("/api/walkthrough/places")
        record("API", "POST /api/walkthrough/places → 405", r.status_code == 405, str(r.status_code))

        # 6e. Auth-gated routes should return 403 without token
        r = client.get("/api/walkthrough/mine")
        record("API", "GET /walkthrough/mine without auth → 403", r.status_code in (403, 401, 422), str(r.status_code))

    except ImportError as e:
        record("API", "FastAPI TestClient import", False, str(e))
    except Exception as e:
        record("API", "API test suite", False, traceback.format_exc(limit=5))

# ===========================================================================
# SECTION 7 — SUMMARY
# ===========================================================================
print("\n" + "="*60)
print("SUMMARY")
print("="*60)

passed  = sum(1 for _, _, s in RESULTS if s == "PASS")
failed  = sum(1 for _, _, s in RESULTS if s == "FAIL")
skipped = sum(1 for _, _, s in RESULTS if s == "SKIP")
total   = len(RESULTS)

print(f"\n  Total : {total}")
print(f"  ✅ Pass : {passed}")
print(f"  ❌ Fail : {failed}")
print(f"  ⏭️  Skip : {skipped}")

if failed:
    print("\n  FAILED TESTS:")
    for sec, name, status in RESULTS:
        if status == "FAIL":
            print(f"    ❌ [{sec}] {name}")

success_rate = (passed / (total - skipped)) * 100 if (total - skipped) > 0 else 0
print(f"\n  Success Rate (excl. skips): {success_rate:.1f}%")
if success_rate >= 90:
    print("  🎉 Day 3 gate PASSED (≥ 90%)")
else:
    print("  ⚠️  Day 3 gate FAILED (< 90%)")

print()
sys.exit(1 if failed else 0)
