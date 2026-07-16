"""
embed_and_store.py — Generates vector embeddings using google-genai
and stores them in a local Chroma DB collection for Yatra.
"""

import os
import json
import time
import re
from google import genai
from google.genai.errors import APIError
import chromadb
from dotenv import load_dotenv

# Load env variables from .env if present
load_dotenv()

def parse_header(snapshot_text: str) -> tuple[str, str]:
    """Extract (place, era) from the first line of the snapshot document."""
    lines = snapshot_text.strip().split('\n')
    if not lines:
        return "", ""
    header = lines[0]
    if ',' in header:
        parts = header.split(',', 1)
        return parts[0].strip(), parts[1].strip()
    return header.strip(), ""

def get_word_count(text: str) -> int:
    return len(text.split())

def get_embedding_with_backoff(client: genai.Client, text: str, retries: int = 5) -> list[float]:
    """Fetch embedding for *text* with exponential backoff on 429 rate limits."""
    wait_time = 1.0
    for attempt in range(retries + 1):
        try:
            response = client.models.embed_content(
                model='gemini-embedding-001',
                contents=text
            )
            # Access embedding values from modern google-genai response object
            if response.embeddings:
                return response.embeddings[0].values
            elif hasattr(response, 'embedding') and response.embedding:
                return response.embedding.values
            else:
                raise ValueError("No embeddings returned in the response object.")
        except Exception as e:
            err_msg = str(e).lower()
            # Catch 429 rate limits
            if '429' in err_msg or 'resource_exhausted' in err_msg or 'rate limit' in err_msg:
                if attempt == retries:
                    print(f"[ERROR] Max retries reached. Failing on rate limit error: {e}")
                    raise e
                print(f"[WARN] Rate limit hit. Retrying in {wait_time}s... (Attempt {attempt + 1}/{retries})")
                time.sleep(wait_time)
                wait_time *= 2.0
            else:
                print(f"[ERROR] API Call failed: {e}")
                raise e
    raise RuntimeError("Failed to obtain embedding after maximum retries.")

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(current_dir, 'chunks', 'snapshot_index.json')
    db_path = os.path.join(current_dir, 'chroma_db')

    if not os.path.isfile(index_path):
        print(f"[ERROR] Index file not found at {index_path}. Run chunk_text.py first.")
        return

    # Load chunks
    with open(index_path, 'r', encoding='utf-8') as f:
        index_data = json.load(f)

    if not index_data:
        print("[WARN] snapshot_index.json is empty. Nothing to embed.")
        return

    print(f"Loaded {len(index_data)} snapshots from index.")

    # Initialize Gemini client
    # The client automatically picks up GEMINI_API_KEY from environment variables
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[WARN] GEMINI_API_KEY environment variable not set. API calls might fail if not authenticated.")
    
    client = genai.Client()

    # Initialize Chroma client
    print(f"Connecting to Chroma PersistentClient at: {db_path}")
    chroma_client = chromadb.PersistentClient(path=db_path)
    collection = chroma_client.get_or_create_collection(name="yatra_snapshots")

    total_embedded = 0
    start_time = time.time()

    for idx, (key, snapshot_text) in enumerate(index_data.items(), 1):
        place, era = parse_header(snapshot_text)
        wc = get_word_count(snapshot_text)

        # Generate embedding
        embedding = get_embedding_with_backoff(client, snapshot_text)

        # Metadata format: lowercased/stripped values
        metadata = {
            "place": place.strip().lower(),
            "era": era.strip().lower(),
            "word_count": wc
        }

        # Store in Chroma
        collection.upsert(
            ids=[key],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[snapshot_text]
        )

        total_embedded += 1

        if idx % 10 == 0 or idx == len(index_data):
            print(f"  Processed {idx}/{len(index_data)} snapshots... (Place: {place})")

    duration = time.time() - start_time
    print(f"\n[SUCCESS] Successfully stored {total_embedded} snapshots in collection 'yatra_snapshots'.")
    print(f"Database location: {db_path}")
    print(f"Time taken: {duration:.2f} seconds.")

if __name__ == '__main__':
    main()
