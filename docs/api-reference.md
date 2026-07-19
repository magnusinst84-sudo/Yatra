# API Reference

*Source: `backend/api/walkthrough.py` and `backend/main.py`*

All routes are mounted directly via `main.py` (`app.include_router(walkthrough_router)`).

### 1. `GET /api/walkthrough/places`
* **Auth Required:** No
* **Purpose:** Returns the statically defined list of 25 supported place/era combinations.

### 2. `POST /api/walkthrough`
* **Auth Required:** No
* **Purpose:** Direct RAG + AI generation (No caching/DB check).

### 3. `POST /api/walkthrough/start`
* **Auth Required:** No (Defaults to `user_uid="system"` if no token provided)
* **Payload Shape:** `{"place": "string", "era": "string", "rag_context": "string (optional)"}`
* **Purpose:** Checks cache -> Runs generation -> Generates Images -> Saves to global pool.

### 4. `GET /api/walkthrough/mine`
* **Auth Required:** **YES** (`Depends(get_current_user)`)
* **Purpose:** Returns thumbnail summaries of all walkthroughs claimed by the authenticated user's UID.

### 5. `POST /api/walkthrough/{walkthrough_id}/save`
* **Auth Required:** **YES** (`Depends(get_current_user)`)
* **Purpose:** Clones a system walkthrough to the authenticated user's account.

### 6. `POST /api/walkthrough/{walkthrough_id}/share`
* **Auth Required:** **YES** (`Depends(get_current_user)`)
* **Purpose:** Validates ownership, generates an 8-character slug, and updates the database.

### 7. `GET /api/walkthrough/shared/{slug}`
* **Auth Required:** No
* **Purpose:** Public retrieval endpoint for guests viewing shared links.

### 8. `GET /api/walkthrough/{walkthrough_id}`
* **Auth Required:** No
* **Purpose:** Public retrieval by exact ID (used by History tab to expand thumbnails).

### 9. `GET /api/walkthrough/{walkthrough_id}/stop/{n}`
* **Auth Required:** No
* **Purpose:** Polling endpoint to check if an image has finished generating for a specific stop.
