import asyncio
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import time

async def main():
    load_dotenv('backend/.env')
    mongo_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_uri)
    db = client.yatra

    # Use a unique place to guarantee cache miss every time we run the script
    place = f"Race_Test_{int(time.time())}"
    era = "Test Era"

    payload = {
        "place": place,
        "era": era,
        "rag_context": "Dummy context to bypass real RAG."
    }
    url = "http://localhost:8000/api/walkthrough/start"

    async with aiohttp.ClientSession() as session:
        print(f"Firing two concurrent requests for {place}...")
        tasks = [
            session.post(url, json=payload),
            session.post(url, json=payload)
        ]
        
        responses = await asyncio.gather(*tasks)
        
        for i, res in enumerate(responses):
            data = await res.json()
            print(f"--- Request {i+1} ---")
            print(f"Status: {res.status}")
            if res.status == 200:
                print(f"Walkthrough ID: {data.get('walkthrough_id')}")
                print(f"Is generated complete?: {data.get('status') == 'complete' or all(s.get('generated') for s in data.get('stops', []))}")
            else:
                print(f"Error: {data}")

if __name__ == "__main__":
    asyncio.run(main())
