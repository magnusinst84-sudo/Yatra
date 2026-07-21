import os
from motor.motor_asyncio import AsyncIOMotorClient

client = None
db = None

async def init_db():
    global client, db
    
    mongo_uri = os.environ.get("MONGODB_URI")
    if not mongo_uri:
        # Provide a helpful error message to the user if they haven't set it yet.
        raise RuntimeError(
            "MONGODB_URI is not set in the environment.\n"
            "Please create a MongoDB cluster (e.g., at MongoDB Atlas), get the connection string, "
            "and add it to your backend/.env file as MONGODB_URI=mongodb+srv://..."
        )

    # Initialize the async motor client
    client = AsyncIOMotorClient(mongo_uri)
    db = client.yatra

    # Create Indexes
    # 1. share_slug must be unique, but sparse (so walkthroughs without a slug don't collide on null)
    await db.walkthroughs.create_index("share_slug", unique=True, sparse=True)
    
    # 2. user_uid index for fast lookup of a user's saved walkthroughs
    await db.walkthroughs.create_index("user_uid")
    
    # 3. Compound unique index on (place, era, user_uid) to prevent race condition duplicates
    await db.walkthroughs.create_index([("place", 1), ("era", 1), ("user_uid", 1)], unique=True)

async def close_db():
    global client
    if client:
        client.close()

def get_db():
    return db
