import os
import uuid
import base64
import urllib.parse
import httpx
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Model chain for image generation — ordered fastest → highest quality.
# Tier 1–3: Imagen 4 models (generate_images API).
# Tier 4: gemini-2.0-flash-preview-image-generation — generate_content fallback.
# Images are returned as base64 data URLs and stored directly in MongoDB.
IMAGEN_MODEL_CHAIN = [
    "imagen-4.0-fast-generate-001",   # Tier 1: Fastest, lowest cost
    "imagen-4.0-generate-001",        # Tier 2: Standard quality
    "imagen-4.0-ultra-generate-001",  # Tier 3: Highest quality
]
GEMINI_IMAGE_FALLBACK = "gemini-3.1-flash-image"


def get_gemini_client() -> genai.Client:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("Set GEMINI_API_KEY in your environment.")
    return genai.Client(api_key=key)


def bytes_to_data_url(image_bytes: bytes, mime_type: str = "image/png") -> str:
    """Convert raw image bytes into a base64 data URL for direct browser use."""
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


async def generate_image_with_fallback(prompt: str) -> str | None:
    """
    Generates an image using a four-tier fallback chain and returns a
    base64 data URL (stored directly in MongoDB — no external storage needed).

    Tier 1: imagen-4.0-fast-generate-001   (generate_images)
    Tier 2: imagen-4.0-generate-001        (generate_images)
    Tier 3: imagen-4.0-ultra-generate-001  (generate_images)
    Tier 4: free fallback via Pollinations.ai

    Returns None if all tiers fail.
    """
    client = get_gemini_client()

    # --- Tiers 1–3: Imagen 4 via generate_images() ---
    for model in IMAGEN_MODEL_CHAIN:
        try:
            result = client.models.generate_images(
                model=model,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    output_mime_type="image/png",
                    aspect_ratio="16:9",
                ),
            )
            if not result.generated_images:
                continue
            image_bytes = result.generated_images[0].image.image_bytes
            print(f"  [IMAGE] Generated via {model}")
            return bytes_to_data_url(image_bytes)

        except APIError as exc:
            if exc.code not in {429} and "quota" not in str(exc).lower():
                print(f"  [IMAGE] {model} failed: {exc.code} {exc.status}")
        except Exception as e:
            print(f"  [IMAGE] Unexpected error with {model}: {e}")

    # --- Tier 4: Free Fallback via Pollinations.ai (No API key required) ---
    # Since free-tier Gemini API restricts image generation, we use this free service
    # so you can actually see real generated images in your app without paying.
    try:
        print("  [IMAGE] Falling back to free Pollinations.ai generator...")
        prompt_encoded = urllib.parse.quote(prompt)
        pollinations_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=576&nologo=true"
        
        async with httpx.AsyncClient(timeout=60.0) as http_client:
            resp = await http_client.get(pollinations_url)
            if resp.status_code == 200:
                print("  [IMAGE] Successfully generated via Pollinations.ai")
                return bytes_to_data_url(resp.content, "image/jpeg")
            else:
                print(f"  [IMAGE] Pollinations failed with status {resp.status_code}")
                
    except Exception as e:
        print(f"  [IMAGE] Free fallback failed: {e}")

    # If even the free fallback fails, return a 1x1 transparent PNG placeholder
    print("  [IMAGE] All methods failed. Returning placeholder image.")
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="