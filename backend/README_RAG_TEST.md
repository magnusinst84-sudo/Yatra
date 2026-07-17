# RAG + Generation — Quick Test Guide

Use this to verify the full RAG → Gemini generation pipeline end-to-end after pulling.

## Prerequisites

- Python 3.11+
- `GEMINI_API_KEY` set in `backend/.env`

## Setup (one-time)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run the server

Run from the **repo root** (`Yatra/`):

```bash
PYTHONPATH=. backend/venv/bin/uvicorn backend.main:app --reload --port 8000
```

Server starts at `http://localhost:8000`.

---

## Test the endpoints

### 1. Health check
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok"}
```

### 2. See all valid place + era options
```bash
curl http://localhost:8000/api/walkthrough/places
```

### 3. Generate a walkthrough (RAG + Gemini)
```bash
curl -X POST http://localhost:8000/api/walkthrough \
  -H "Content-Type: application/json" \
  -d '{"place": "Hampi", "era": "Vijayanagara Empire (c. 1500 CE)"}'
```

**Expected response shape:**
```json
{
  "walkthrough_id": "...",
  "place": "Hampi",
  "era": "Vijayanagara Empire (c. 1500 CE)",
  "era_summary": "...",
  "stops": [
    {
      "stop_id": "...",
      "stop_name": "...",
      "narration_script": "...",
      "image_prompt": "...",
      "daily_life_facts": ["...", "...", "..."],
      "image_url": null,
      "generated": false
    }
  ]
}
```

### 4. Test with a few more places
```bash
# Mughal Agra
curl -X POST http://localhost:8000/api/walkthrough \
  -H "Content-Type: application/json" \
  -d '{"place": "Agra", "era": "Mughal Empire (c. 1650 CE)"}'

# Indus Valley
curl -X POST http://localhost:8000/api/walkthrough \
  -H "Content-Type: application/json" \
  -d '{"place": "Mohenjo-daro", "era": "Indus Valley Civilization (c. 2500 BCE)"}'
```

### 5. Test invalid input (should return 400)
```bash
curl -X POST http://localhost:8000/api/walkthrough \
  -H "Content-Type: application/json" \
  -d '{"place": "Mumbai", "era": "Modern"}'
# Expected: 400 with "Unknown place+era" message
```

---

## What the pipeline does

```
POST /api/walkthrough
        │
        ▼
 retrieval.retrieve(place, era)
        │
        ├── Fast path: dict lookup in snapshot_index.json  (~0ms)
        └── Slow path: Gemini embedding + Chroma vector search (~1-2s)
        │
        ▼
 agent.generate_world_state(place, era, rag_context)
        │
        └── Calls Gemini (gemini-3.1-flash-lite → fallback chain)
            Returns structured WorldState with 3-5 stops
```

---

## Interactive API docs

FastAPI auto-generates docs at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
