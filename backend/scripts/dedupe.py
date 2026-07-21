import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

DRY_RUN = False

async def main():
    load_dotenv('backend/.env')
    mongo_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_uri)
    db = client.yatra
    
    pipeline = [
        {"$sort": {"created_at": 1}},
        {"$group": {
            "_id": {"place": "$place", "era": "$era", "user_uid": "$user_uid"},
            "docs": {"$push": {"id": "$_id", "stops": "$stops", "created_at": "$created_at"}},
            "count": {"$sum": 1}
        }},
        {"$match": {"count": {"$gt": 1}}}
    ]
    
    total_deleted = 0
    
    cursor = db.walkthroughs.aggregate(pipeline)
    async for doc in cursor:
        docs = doc['docs']
        # prefer a fully-generated doc (must have stops); fall back to most recent if none complete
        complete = [d for d in docs if d.get("stops") and all(s.get("generated") for s in d["stops"])]
        keeper = complete[-1] if complete else docs[-1]
        dups_to_remove = [d["id"] for d in docs if d["id"] != keeper["id"]]
        
        total_deleted += len(dups_to_remove)
        print(f"Group: {doc['_id']}")
        print(f"  -> Keeping ID: {keeper['id']}")
        print(f"  -> Removing IDs: {dups_to_remove}")
        
        if not DRY_RUN:
            await db.walkthroughs.delete_many({"_id": {"$in": dups_to_remove}})
            
    print(f"\nTotal documents that {'would be' if DRY_RUN else 'were'} deleted: {total_deleted}")
    print(f"Deduplication phase {'simulated (DRY RUN)' if DRY_RUN else 'completed'}.")
    
    # Try to enforce index now only if not DRY_RUN
    if not DRY_RUN:
        try:
            await db.walkthroughs.create_index([('place', 1), ('era', 1), ('user_uid', 1)], unique=True)
            print('Unique index creation successful.')
        except Exception as e:
            print(f'Index creation failed: {e}')
            
        indexes = await db.walkthroughs.index_information()
        print('Current Indexes:')
        for name, info in indexes.items():
            print(f'{name}: {info}')
    else:
        print("\nSkipping index creation during DRY_RUN.")

if __name__ == "__main__":
    asyncio.run(main())
