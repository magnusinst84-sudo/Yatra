import os
import sys
import json
import asyncio
import httpx
from fastapi import FastAPI
from backend.main import app
from backend.auth.jwt import get_current_user
from backend.database.mongo_client import init_db, close_db
from backend.database.crud import get_db

async def run_tests():
    print("Starting E2E Tests for Sections 8 and 9")
    
    # Initialize DB (same loop as test)
    await init_db()

    # --- SECTION 8: SHAREABLE LINKS ---
    print("\n--- SECTION 8: SHAREABLE LINKS ---")
    
    def override_user1(): return {"uid": "e2e_user_1", "email": "1@test.com"}
    app.dependency_overrides[get_current_user] = override_user1
    
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client_auth:
        print("1. Generating walkthrough (POST /api/walkthrough/start)...")
        resp1 = await client_auth.post("/api/walkthrough/start", json={"place": "Taxila", "era": "Maurya Empire, c. 250 BCE"})
        if resp1.status_code != 200:
            print(f"Error starting walkthrough: {resp1.status_code} {resp1.text}")
            sys.exit(1)
        wt_data = resp1.json()
        wt_id = wt_data["walkthrough_id"]
        print(f"   Generated ID: {wt_id}")
        
        print("2. Claiming and sharing...")
        await client_auth.post(f"/api/walkthrough/{wt_id}/save")
        resp_share = await client_auth.post(f"/api/walkthrough/{wt_id}/share")
        share_data = resp_share.json()
        slug = share_data.get("share_slug")
        print(f"   Share Slug: {slug}")
    
    print("3. Public lookup with NO auth...")
    app.dependency_overrides.clear()
    
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client_public:
        resp_public = await client_public.get(f"/api/walkthrough/shared/{slug}")
        print(f"   Status Code: {resp_public.status_code}")
        
        print("4. Comparing payloads...")
        pub_data = resp_public.json()
        is_same_stops = len(wt_data["stops"]) == len(pub_data["stops"])
        is_same_narration = wt_data["stops"][0]["narration_script"] == pub_data["stops"][0]["narration_script"]
        print(f"   Same stop count: {is_same_stops}")
        print(f"   Same narration: {is_same_narration}")
        print(f"   Response size: {len(json.dumps(pub_data))} bytes")
        if pub_data.get("stops") and pub_data["stops"][0].get("image_url"):
            print(f"   Image URL length: {len(pub_data['stops'][0]['image_url'])} chars")
        else:
            print("   No image URL found in public payload.")
        
        print("5. Invalid slug test...")
        resp_invalid = await client_public.get("/api/walkthrough/shared/invalidSlug123")
        print(f"   Invalid slug status code: {resp_invalid.status_code}")


    # --- SECTION 9: MY WALKTHROUGHS ---
    print("\n--- SECTION 9: MY WALKTHROUGHS ---")
    print("1. Endpoint wired: GET /api/walkthrough/mine")
    
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client_public:
        resp_no_auth = await client_public.get("/api/walkthrough/mine")
        print(f"2. Call without token status: {resp_no_auth.status_code}")
    
    print("3. Creating 2 walkthroughs for user_2...")
    def override_user2(): return {"uid": "e2e_user_2", "email": "2@test.com"}
    app.dependency_overrides[get_current_user] = override_user2
    
    await get_db().walkthroughs.insert_many([
        {"walkthrough_id": "wt_user2_1", "user_uid": "e2e_user_2", "place": "Place A", "era": "Era A", "created_at": 1, "stops": []},
        {"walkthrough_id": "wt_user2_2", "user_uid": "e2e_user_2", "place": "Place B", "era": "Era B", "created_at": 2, "stops": [{"image_url": "dummy", "narration_script": "very long text"}]}
    ])
    
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client_user2:
        resp_mine = await client_user2.get("/api/walkthrough/mine")
        mine_data = resp_mine.json()
        print(f"   User 2 returned items count: {len(mine_data)}")
        if len(mine_data) >= 2:
            print(f"   Newest first check: {mine_data[0]['walkthrough_id'] == 'wt_user2_2'}")
            print(f"   Shape keys (item 0): {list(mine_data[0].keys())}")
    
    print("4. User 3 isolation check...")
    def override_user3(): return {"uid": "e2e_user_3", "email": "3@test.com"}
    app.dependency_overrides[get_current_user] = override_user3
    
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client_user3:
        resp_mine_3 = await client_user3.get("/api/walkthrough/mine")
        mine_data_3 = resp_mine_3.json()
        print(f"   User 3 returned items count: {len(mine_data_3)}")
    
    # Cleanup DB overrides
    await get_db().walkthroughs.delete_many({"user_uid": {"$in": ["e2e_user_1", "e2e_user_2", "e2e_user_3"]}})
    await close_db()
    
    print("\n--- E2E TESTS FINISHED ---")

if __name__ == "__main__":
    asyncio.run(run_tests())
