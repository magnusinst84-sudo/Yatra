import os
from google import genai

def get_gemini_client() -> genai.Client:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("Set GEMINI_API_KEY in your environment.")
    return genai.Client(api_key=key)