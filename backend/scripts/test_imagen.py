import os
from google import genai
from google.genai import types

key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=key)
try:
    result = client.models.generate_images(
        model='imagen-4.0-fast-generate-001',
        prompt='A dog',
        config=types.GenerateImagesConfig(
            number_of_images=1,
            output_mime_type="image/png"
        )
    )
    print("Success:", len(result.generated_images))
except Exception as e:
    print("Error SDK:", e)
