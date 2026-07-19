# Known Gaps & Tech Debt

### 1. `Home.jsx` Search Inputs are Hardcoded
* **Mismatch:** The frontend search form currently uses a free-text input `<input type="text" value={searchPlace} />` and a hardcoded select box `<select value={selectedEra}>` (`Home.jsx` lines 196, 212).
* **Gap:** It does not call `GET /api/walkthrough/places` to populate dropdowns, meaning a user can type a place/era combination that the backend does not officially support in its RAG vector store, resulting in a 400 Bad Request.

### 2. Deprecated Imagen 4 Models
* **Mismatch:** `backend/services/image_gen.py` relies heavily on `imagen-4.0-fast-generate-001` as the primary image generators.
* **Gap:** These specific model tags are scheduled for deprecation by Google in late 2026. Long-term, this code should be migrated to `imagen-3.0-generate-001` or standard Gemini image generation paths.

### 3. Missing Frontend 404/Error Handling for Shared Links
* **Mismatch:** While `App.tsx` correctly attempts to fetch `/shared/[slug]`, if the fetch fails (e.g., bad slug), it merely logs to console (`console.error('Shared link failed:', err)`).
* **Gap:** The frontend lacks a user-facing "Walkthrough Not Found" UI state, so guests will simply see the unauthenticated Landing Page with no explanation as to why the link didn't work.

### 4. Database Image URL Storage vs CDN Storage
* **Mismatch:** The image fallback code (`image_gen.py`) returns Base64 data URIs for both Pollinations and the Placeholder, which are saved directly into the MongoDB document (`stop["image_url"]`).
* **Gap:** Storing giant Base64 strings directly in MongoDB documents can rapidly inflate database size and reduce query performance. The optimal architecture (currently stubbed/unimplemented) is to upload these to Firebase Storage and only save the resulting CDN URL string in MongoDB.
