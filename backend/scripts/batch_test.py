import asyncio
import os
import sys

# Ensure backend can be imported
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

from backend.agent.world_state import generate_world_state
from backend.services.image_gen import generate_image_with_fallback
from backend.database.mongo_client import init_db, close_db
from backend.database.crud import save_walkthrough, find_walkthrough_by_place_era

# 10+ pairs for validation testing and database seeding
TARGETS = [
    {"place": "Mohenjo-daro", "era": "Indus Valley Civilization, c. 2500 BCE"},
    {"place": "Taxila", "era": "Maurya Empire, c. 250 BCE"},
    {"place": "Ujjain", "era": "Gupta Empire, c. 400 CE"},
    {"place": "Hampi", "era": "Vijayanagara Empire, c. 1500 CE"},
    {"place": "Fatehpur Sikri", "era": "Mughal Empire, c. 1575 CE"},
    {"place": "Pune", "era": "Maratha Empire, c. 1750 CE"},
    {"place": "Kolkata", "era": "British East India Company, c. 1820 CE"},
    {"place": "Shimla", "era": "British Raj, c. 1900 CE"},
    {"place": "Madurai", "era": "Pandya Kingdom, c. 1300 CE"},
    {"place": "Thanjavur", "era": "Chola Empire, c. 1000 CE"},
    {"place": "Ellora", "era": "Rashtrakuta Dynasty, c. 800 CE"}
]

async def process_target(target):
    place = target["place"]
    era = target["era"]
    
    # 1. Check if it already exists
    existing = await find_walkthrough_by_place_era(place, era)
    if existing:
        print(f"[SKIP] {place} ({era}) is already cached in MongoDB.")
        return True
        
    print(f"\n[GENERATING] {place} ({era})...")
    
    try:
        # 2. Generate text (agent validation)
        # Note: In a real run, you'd pull rag_context from Chroma.
        # Passing empty string triggers the "uncertainty flag" inside the agent,
        # which is fine for raw validation testing if RAG isn't connected yet.
        world_state = await generate_world_state(
            place=place,
            era=era,
            rag_context="", 
            user_uid="system"
        )
        
        state_dict = world_state.model_dump()
        print(f"  -> Generated {len(state_dict['stops'])} stops.")

        # 3. Generate images
        for stop in state_dict["stops"]:
            print(f"  -> Generating image for: {stop['stop_name']}...")
            image_url = await generate_image_with_fallback(stop["image_prompt"])
            stop["image_url"] = image_url
            stop["generated"] = True
            
        # 4. Save to Database
        await save_walkthrough(state_dict)
        print(f"[SUCCESS] Saved {place} to MongoDB!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed on {place} ({era}): {e}")
        return False

async def main():
    print("Initializing Database...")
    await init_db()
    
    success_count = 0
    total = len(TARGETS)
    
    print(f"Starting batch validation for {total} targets...\n")
    for target in TARGETS:
        if await process_target(target):
            success_count += 1
            
    print(f"\n--- BATCH VALIDATION COMPLETE ---")
    print(f"Success Rate: {success_count}/{total} ({(success_count/total)*100:.1f}%)")
    
    if (success_count/total) >= 0.9:
        print("✅ Day 3 Metric (>90%) Achieved!")
    else:
        print("❌ Failed to reach >90% metric.")
        
    await close_db()

if __name__ == "__main__":
    asyncio.run(main())
