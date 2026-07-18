import uuid
import secrets
import string
from backend.database.mongo_client import get_db

def generate_share_slug(length=8):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

async def save_walkthrough(walkthrough_data: dict) -> str:
    """Save a walkthrough to MongoDB.

    Always inserts a shallow copy of the input dict so that motor's
    insert_one() — which mutates the dict in-place to add `_id` — does not
    pollute the caller's object.  The `_id` is also stripped from the copy
    afterwards so the dict remains clean for re-use.
    """
    db = get_db()

    doc = dict(walkthrough_data)          # copy — protects caller from _id mutation
    doc.pop("_id", None)                  # strip any stale ObjectId before inserting

    if "walkthrough_id" not in doc:
        doc["walkthrough_id"] = str(uuid.uuid4())
        walkthrough_data["walkthrough_id"] = doc["walkthrough_id"]

    await db.walkthroughs.insert_one(doc)
    doc.pop("_id", None)                  # clean up after motor adds it
    return doc["walkthrough_id"]

async def get_walkthrough_by_id(walkthrough_id: str) -> dict:
    """Get a walkthrough by its internal ID."""
    db = get_db()
    result = await db.walkthroughs.find_one({"walkthrough_id": walkthrough_id})
    if result:
        result.pop("_id", None)  # Remove internal Mongo ObjectId
    return result

async def get_walkthrough_by_slug(slug: str) -> dict:
    """Get a shared walkthrough by its slug."""
    db = get_db()
    result = await db.walkthroughs.find_one({"share_slug": slug})
    if result:
        result.pop("_id", None)
    return result

async def list_walkthroughs_for_user(user_uid: str) -> list:
    """List all walkthroughs saved by a specific user."""
    db = get_db()
    cursor = db.walkthroughs.find({"user_uid": user_uid}).sort("created_at", -1)
    results = []
    async for document in cursor:
        document.pop("_id", None)
        results.append(document)
    return results

async def update_share_slug(walkthrough_id: str, slug: str):
    """Update a walkthrough with a new share slug."""
    db = get_db()
    await db.walkthroughs.update_one(
        {"walkthrough_id": walkthrough_id},
        {"$set": {"share_slug": slug}}
    )

async def find_walkthrough_by_place_era(place: str, era: str) -> dict:
    """Find a pre-generated walkthrough by place and era."""
    db = get_db()
    # Assuming pre-generated walkthroughs are marked with user_uid="system"
    result = await db.walkthroughs.find_one({"place": place, "era": era, "user_uid": "system"})
    if result:
        result.pop("_id", None)
    return result
