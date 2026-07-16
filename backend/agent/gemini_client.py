import asyncio
import os
from google import genai
from google.genai import types
from google.genai.errors import APIError


MODEL_CHAIN = ["gemini-3.1-flash-lite", "gemini-3-flash-preview", "gemini-3.5-flash"]
QUOTA_STATUS_CODES = {429}

def get_gemini_client() -> genai.Client:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("Set GEMINI_API_KEY in your environment.")
    return genai.Client(api_key=key)


async def generate_with_fallback(
    prompt: str,
    system_instruction: str,
    response_mime_type: str = "application/json",
) -> str:
    """Generate through Gemini models only, not a cross-provider fallback.

    This chain remains entirely within Google's Gemini model family, the same
    provider as the primary model. It therefore does not trigger the TRD §9 /
    PRD §6 "no multi-provider fallback chain" clause.
    """
    client = get_gemini_client()
    last_exc: APIError | None = None

    for model in MODEL_CHAIN:
        try:
            response = await asyncio.to_thread(
                client.models.generate_content,
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type=response_mime_type,
                ),
            )
            return response.text
        except APIError as exc:
            status_code = exc.code
            if status_code not in QUOTA_STATUS_CODES and "quota" not in str(exc).lower():
                raise
            last_exc = exc

    assert last_exc is not None
    raise last_exc
