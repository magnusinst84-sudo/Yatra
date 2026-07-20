import os
import uuid
import base64
import urllib.parse
import httpx
from google import genai
from google.genai import types
from google.genai.errors import APIError
from motor.motor_asyncio import AsyncIOMotorClient

# Model chain for image generation — ordered fastest → highest quality.
IMAGEN_MODEL_CHAIN = [
    "imagen-4.0-fast-generate-001",   # Tier 1: Fastest, lowest cost
    "imagen-4.0-generate-001",        # Tier 2: Standard quality
    "imagen-4.0-ultra-generate-001",  # Tier 3: Highest quality
]

# MongoDB Configuration
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "chronos_db"  # Adjusted for your narrative application context
COLLECTION_NAME = "generated_images"

# Global Async MongoDB Client
db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client[DB_NAME]
images_collection = db[COLLECTION_NAME]


def get_gemini_client() -> genai.Client:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("Set GEMINI_API_KEY in your environment.")
    return genai.Client(api_key=key)


def bytes_to_data_url(image_bytes: bytes, mime_type: str = "image/png") -> str:
    """Convert raw image bytes into a base64 data URL for direct browser use."""
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


async def save_image_to_mongodb(prompt: str, data_url: str) -> str:
    """Writes the generated image metadata and data URL to MongoDB."""
    document = {
        "_id": str(uuid.uuid4()),
        "prompt": prompt,
        "image_data_url": data_url,
        "created_at": httpx.Client().get("https://httpbin.org/date").headers.get("date") 
                      if not os.environ.get("TESTING") else None 
    }
    # In a real environment, you'd ideally use datetime.utcnow() but keeping it simple for async insertion
    import datetime
    document["timestamp"] = datetime.datetime.utcnow()

    result = await images_collection.insert_one(document)
    print(f"  [MONGO] Successfully saved image document with ID: {result.inserted_id}")
    return result.inserted_id


async def generate_image_with_fallback(prompt: str) -> str | None:
    """
    Generates an image using a four-tier fallback chain and returns a
    base64 data URL.
    """
    client = get_gemini_client()

    # --- Tiers 1–3: Imagen 4 via client.aio (Async API) ---
    for model in IMAGEN_MODEL_CHAIN:
        try:
            # FIX: Using client.aio for true async execution inside an async function
            result = await client.aio.models.generate_images(
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
            
            # Extract raw bytes from the new Google GenAI SDK structure
            image_bytes = result.generated_images[0].image.image_bytes
            print(f"  [IMAGE] Generated via {model}")
            return bytes_to_data_url(image_bytes)

        except APIError as exc:
            # 429 indicates rate limit or quota exceeded
            if exc.code not in {429} and "quota" not in str(exc).lower():
                print(f"  [IMAGE] {model} failed: {exc.code} {exc.status}")
        except Exception as e:
            print(f"  [IMAGE] Unexpected error with {model}: {e}")

    # --- Tier 4: Free Fallback via Pollinations.ai ---
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

    # Fallback placeholder if everything else completely blows up
    print("  [IMAGE] All methods failed. Returning placeholder image.")
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="


async def generate_and_store_flow(prompt: str):
    """Orchestrates the generation and immediate writing to MongoDB."""
    print(f"Starting process for prompt: '{prompt}'")
    
    # 1. Generate the image URL string
    data_url = await generate_image_with_fallback(prompt)
    
    # 2. Save it straight to MongoDB
    if data_url:
        doc_id = await save_image_to_mongodb(prompt, data_url)
        return doc_id
    return None


# Example execution block
if __name__ == "__main__":
    import asyncio
    
    # Set your environment variables before running
    # os.environ["GEMINI_API_KEY"] = "your-api-key"
    # os.environ["MONGO_URI"] = "mongodb://localhost:27017"
    
    test_prompt = "A cinematic, moody portrait of a historical time traveler in neon-lit ancient Rome"
    
    asyncio.run(generate_and_store_flow(test_prompt))