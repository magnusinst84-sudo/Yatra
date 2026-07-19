"""
backend/rag/retrieval.py
------------------------
Public interface: retrieve(place, era) -> str

Returns a compact 80-120 word historical snapshot for the given place/era
combination, suitable for injecting directly into the agent's prompt as
RAG context.

Primary source  : SNAPSHOT_LOOKUP — a plain dict built from
                  backend/rag/chunks/snapshot_index.json.
                  Dict lookup is instant and covers every known place/era
                  combination from the fixed PLACES list.

Fallback source : Chroma persistent vector store at backend/rag/chroma_db/,
                  collection "yatra_snapshots", embedded with gemini-embedding-001.
                  Used only when the exact dict key is not present (e.g. a
                  slightly different spelling from user input).

Returns "" on any unrecoverable failure so callers never see an exception.
"""

import json
import logging
import os
import re
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from google import genai

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Resolve paths relative to this file so the module works regardless of the
# working directory the FastAPI process is started from.
# ---------------------------------------------------------------------------
_HERE = Path(__file__).parent
_INDEX_PATH = _HERE / "chunks" / "snapshot_index.json"
_CHROMA_PATH = str(_HERE / "chroma_db")

# ---------------------------------------------------------------------------
# Module-level initialisation — runs once at import time, not per-call.
# ---------------------------------------------------------------------------

with open(_INDEX_PATH, "r", encoding="utf-8") as _f:
    SNAPSHOT_LOOKUP: dict[str, str] = json.load(_f)

_chroma_client = chromadb.PersistentClient(path=_CHROMA_PATH)
_collection = _chroma_client.get_or_create_collection(name="yatra_snapshots")

# google.genai.Client picks up GEMINI_API_KEY from the environment automatically.
_genai_client = genai.Client()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_key(place: str, era: str) -> str:
    """Replicate the exact key format used by chunk_text.py's make_index_key.

    We reproduce the logic here (rather than importing it) to keep retrieval.py
    self-contained and free of chunk_text's heavy NLP imports.
    """
    raw = f"{place}_{era}"
    raw = raw.lower()
    raw = re.sub(r'[^a-z0-9_\s-]', '', raw)
    raw = re.sub(r'[\s]+', '_', raw)
    raw = re.sub(r'_+', '_', raw)
    return raw.strip('_')


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def retrieve(place: str, era: str) -> str:
    """Return the RAG snapshot for *place* + *era*, or "" if unavailable.

    Fast path  — O(1) dict lookup, no network, no embedding.
    Slow path  — single Gemini embedding call + Chroma nearest-neighbour query.
                 Reached only for unrecognised place/era combinations.
    """
    key = _make_key(place, era)

    # Fast path: the vast majority of calls land here.
    if key in SNAPSHOT_LOOKUP:
        return SNAPSHOT_LOOKUP[key]

    # Slow path: fuzzy fallback via vector similarity.
    logger.warning("RAG dict miss for key=%r — falling back to Chroma", key)
    try:
        response = _genai_client.models.embed_content(
            model="gemini-embedding-001",
            contents=f"{place} {era}",
        )
        if not response.embeddings:
            return ""
        vector = response.embeddings[0].values

        results = _collection.query(
            query_embeddings=[vector],
            n_results=1,
        )
        distances = results.get("distances", [[]])[0]
        docs = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]
        
        # If the distance is too large, it's not a genuine match.
        if distances and distances[0] > 0.5:
            return ""
            
        return docs[0] if docs else ""

    except Exception as exc:  # noqa: BLE001
        logger.error("RAG retrieval failed for place=%r era=%r: %s", place, era, exc)
        return ""
