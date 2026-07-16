import os

from openai import OpenAI


def get_client() -> OpenAI:
    key = os.environ.get("OPENAI_API_KEY")

    if not key:
        raise RuntimeError("Set OPENAI_API_KEY in your environment.")

    return OpenAI(api_key=key)