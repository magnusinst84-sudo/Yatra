import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def _load_dotenv():
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())
_load_dotenv()

import backend.database.mongo_client as mongo_client

async def wipe():
    await mongo_client.init_db()
    await mongo_client.db.walkthroughs.delete_many({})
    await mongo_client.close_db()
    print('DB Wiped')

if __name__ == '__main__':
    asyncio.run(wipe())
