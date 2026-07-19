"""
test_agent_state.py
-------------------
Quick smoke-test for backend.agent.world_state.generate_world_state().

Usage
-----
1.  Set your key in one of these ways:
      $env:GEMINI_API_KEY = "your-key-here"          # PowerShell
      set GEMINI_API_KEY=your-key-here                # CMD

2.  Run from the repo root (so `backend` is importable):
      python test_agent_state.py

The script prints the full WorldState JSON on success, or a clear error
message on failure.  No pytest / no external test framework needed.
"""

import asyncio
import json
import os
import sys


# ---------------------------------------------------------------------------
# 1. Load .env if present (optional convenience — not required)
# ---------------------------------------------------------------------------
def _load_dotenv():
    env_path = os.path.join(os.path.dirname(__file__), "backend", ".env")
    if not os.path.exists(env_path):
        env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())
        print(f"[info] Loaded env vars from {env_path}")


_load_dotenv()

# ---------------------------------------------------------------------------
# 2. Guard: key must be set before importing the agent (it reads it at init)
# ---------------------------------------------------------------------------
if not os.environ.get("GEMINI_API_KEY"):
    print(
        "\n[ERROR] GEMINI_API_KEY is not set.\n"
        "  PowerShell:  $env:GEMINI_API_KEY = 'your-key-here'\n"
        "  CMD:         set GEMINI_API_KEY=your-key-here\n"
        "  Or create backend/.env with  GEMINI_API_KEY=your-key-here\n"
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# 3. Import the agent (after env is ready)
# ---------------------------------------------------------------------------
from backend.agent.world_state import generate_world_state  # noqa: E402

# ---------------------------------------------------------------------------
# 4. Test parameters — feel free to edit
# ---------------------------------------------------------------------------
TEST_PLACE = "Mohenjo-daro"
TEST_ERA   = "Indus Valley Civilization, c. 2500 BCE"
TEST_RAG   = (
    "Mohenjo-daro was one of the largest urban centers of the Indus Valley "
    "Civilization. The city featured a carefully planned grid layout with "
    "baked-brick houses, covered drainage systems, public wells, granaries, "
    "and the Great Bath. Craft production, long-distance trade, standardized "
    "weights and measures, and sophisticated urban planning reflected the "
    "advanced civic organization of this Bronze Age civilization."
)


# ---------------------------------------------------------------------------
# 5. Run
# ---------------------------------------------------------------------------
async def main():
    print(f"\n[test] Calling generate_world_state(place={TEST_PLACE!r}, era={TEST_ERA!r})")
    print("[test] This may take 10-30 seconds …\n")

    try:
        state = await generate_world_state(
            place=TEST_PLACE,
            era=TEST_ERA,
            rag_context=TEST_RAG,
            user_uid="test-user-001",
        )
    except Exception as exc:
        print(f"[FAIL] {type(exc).__name__}: {exc}")
        sys.exit(1)

    print("=" * 60)
    print("WorldState returned successfully!")
    print("=" * 60)
    print(f"  walkthrough_id : {state.walkthrough_id}")
    print(f"  place          : {state.place}")
    print(f"  era            : {state.era}")
    print(f"  era_summary    : {state.era_summary[:80]}...")
    print(f"  stops count    : {len(state.stops)}")
    print()

    for i, stop in enumerate(state.stops, 1):
        print(f"  Stop {i}: {stop.stop_name}")
        print(f"    narration words : {len(stop.narration_script.split())}")
        print(f"    facts count     : {len(stop.daily_life_facts)}")
        print(f"    image_prompt    : {stop.image_prompt[:60]}...")
        print()

    print("=" * 60)
    print("Full JSON dump:")
    print("=" * 60)
    print(json.dumps(state.model_dump(mode="json"), indent=2, ensure_ascii=False))
    print("\n[PASS] Agent state test completed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
