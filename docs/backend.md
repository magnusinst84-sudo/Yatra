# Backend Architecture & Audit

## Image Generation Fallback Chain
*Source: `backend/services/image_gen.py`, `generate_image_with_fallback()`*

The backend currently attempts to generate images in the following exact fallback order:
1. **Tier 1:** `imagen-4.0-fast-generate-001` (via `genai.Client.models.generate_images`)
2. **Tier 2:** `imagen-4.0-generate-001`
3. **Tier 3:** `imagen-4.0-ultra-generate-001`
4. **Tier 4 (HTTP Fallback):** `https://image.pollinations.ai/prompt/{prompt}` (via `httpx.AsyncClient.get`)
5. **Final Fallback:** 1x1 Transparent PNG placeholder (`data:image/png;base64,iVBORw0...`)

All successful tiers return a Base64-encoded Data URL string.

## Walkthrough Clone Logic (`/save` route)
*Source: `backend/api/walkthrough.py`, `save_user_walkthrough()` (Lines 210-229)*

**Confirmed:** The `/save` route explicitly performs clone/copy logic so the global system document remains untouched.

```python
@router.post("/walkthrough/{walkthrough_id}/save")
async def save_user_walkthrough(walkthrough_id: str, user=Depends(get_current_user)):
    # ...
    wt = await db_instance.walkthroughs.find_one({"walkthrough_id": walkthrough_id})
    # Clone the document for the user so the original stays in the global cache pool
    wt.pop("_id", None)
    new_walkthrough_id = str(uuid.uuid4())
    wt["walkthrough_id"] = new_walkthrough_id
    wt["user_uid"] = user["uid"]
    # Clear any share_slug so the clone doesn't inherit a public link
    wt.pop("share_slug", None) 
    
    await db_instance.walkthroughs.insert_one(wt)
    # ...
```
