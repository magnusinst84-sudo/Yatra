from __future__ import annotations
import json
import uuid
from datetime import datetime, timezone
import asyncio

from google.genai import types
from google.genai.errors import APIError as GeminiAPIError

from backend.agent.gemini_client import get_gemini_client
from backend.agent.prompts import SYSTEM_PROMPT, USER_TEMPLATE
from backend.models import WorldState, Stop, AgentError, ValidationError

MODEL = "gemini-3.1-flash-lite"
MIN_NARRATION_WORDS = 120
MIN_STOPS = 3
MAX_STOPS = 5
MIN_FACTS = 3

# Kept off 0.0: a deterministic retry re-runs the same failure mode instead
# of giving you a genuinely different sample. All three attempts stay in a
# range that still produces coherent JSON but varies enough to escape a
# repeated undershoot.
RETRY_TEMPERATURES = [0.7, 0.85, 0.6]


async def generate_world_state(place: str, era: str, rag_context: str, user_uid: str | None = None) -> WorldState:
    last_exc: Exception | None = None
    for attempt, temperature in enumerate(RETRY_TEMPERATURES):
        try:
            raw = await _call_model(place, era, rag_context, temperature)
            return _parse_and_validate(raw, place, era, user_uid)
        except GeminiAPIError as e:
            last_exc = e
            if attempt == len(RETRY_TEMPERATURES) - 1:
                raise AgentError(f"Gemini API failure after {len(RETRY_TEMPERATURES)} attempts: {e}") from e
        except (json.JSONDecodeError, ValidationError) as e:
            last_exc = e
            if attempt == len(RETRY_TEMPERATURES) - 1:
                raise ValidationError(f"Validation failed after {len(RETRY_TEMPERATURES)} attempts: {e}") from e
    raise AgentError(f"exhausted retries: {last_exc}")


async def _call_model(place: str, era: str, rag_context: str, temperature: float) -> str:
    client = get_gemini_client()
    prompt = USER_TEMPLATE.format(
        place=place, era=era,
        rag_context=rag_context or "(no context — proceed with uncertainty flag)",
    )

    def _sync_call():
        return client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=temperature,
                response_mime_type="application/json",
            ),
        )

    # generate_content is a blocking network call. Running it directly inside
    # this coroutine would block the event loop and serialize every concurrent
    # generate_world_state() call (e.g. asyncio.gather over multiple eras).
    # to_thread moves the blocking call off the event loop so calls actually
    # run concurrently.
    response = await asyncio.to_thread(_sync_call)
    return response.text


def _parse_and_validate(raw, place, era, user_uid):
    data = json.loads(raw)
    if "stops" not in data or "era_summary" not in data:
        raise ValidationError("Missing required top-level keys")

    raw_stops = data["stops"]
    if not (MIN_STOPS <= len(raw_stops) <= MAX_STOPS):
        raise ValidationError(f"Expected {MIN_STOPS}-{MAX_STOPS} stops, got {len(raw_stops)}")

    stops = []
    prev_stop_name = None
    for i, s in enumerate(raw_stops):
        _validate_stop_content(s, i, prev_stop_name)
        prev_stop_name = s.get("stop_name")
        stops.append(Stop(
            stop_id=str(uuid.uuid4()), stop_name=s["stop_name"],
            image_prompt=s["image_prompt"], narration_script=s["narration_script"],
            daily_life_facts=s["daily_life_facts"], image_url=None, generated=False,
        ))

    return WorldState(
        walkthrough_id=str(uuid.uuid4()), user_uid=user_uid, place=place, era=era,
        era_summary=data["era_summary"], created_at=datetime.now(timezone.utc), stops=stops,
    )


# Fallback connector words, used only if the prior stop's name isn't
# referenced directly. Broadened from the original 6-phrase list, which
# rejected valid paraphrases (e.g. "departing", "having left", "onward from")
# while accepting phrases with no real link to the previous stop (e.g. "beyond
# the horizon" contained "beyond" and passed with zero actual continuity).
CONTINUITY_MARKERS = (
    "continuing", "from here", "leaving", "beyond", "as you move",
    "turning from", "departing", "having left", "onward from", "moving on",
    "walking from", "past the", "behind you", "further along", "next to",
)


def _validate_stop_content(s, index, prev_stop_name=None):
    required = {"stop_name", "narration_script", "image_prompt", "daily_life_facts"}
    missing = required - s.keys()
    if missing:
        raise ValidationError(f"Stop {index} missing keys: {missing}")

    word_count = len(s["narration_script"].split())
    if word_count < MIN_NARRATION_WORDS:
        raise ValidationError(f"Stop {index} narration too short: {word_count} words")

    if len(s["daily_life_facts"]) < MIN_FACTS:
        raise ValidationError(f"Stop {index} has too few daily_life_facts")

    if index > 0:
        prompt_lower = s["image_prompt"].lower()
        references_prev_name = bool(prev_stop_name) and prev_stop_name.lower() in prompt_lower
        references_connector = any(m in prompt_lower for m in CONTINUITY_MARKERS)
        if not (references_prev_name or references_connector):
            raise ValidationError(
                f"Stop {index} image_prompt lacks continuity reference "
                f"(no mention of prior stop '{prev_stop_name}' and no connector phrase)"
            )