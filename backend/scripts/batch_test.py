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
    {"place": "Ellora", "era": "Rashtrakuta Dynasty, c. 800 CE"},
    {"place": "Ayodhya", "era": "Ancient Kosala Kingdom, c. 500 BCE"},
    {"place": "Jaipur", "era": "Kachwaha Rajput Kingdom, c. 1750 CE"},
    {"place": "Pune (Later)", "era": "Maratha Confederacy, c. 1770 CE"},
    {"place": "Varanasi", "era": "Ancient Mahajanapada Period, c. 500 BCE"},
    {"place": "Vijayanagar", "era": "Vijayanagara Empire, c. 1500 CE"},
    {"place": "Saragarhi", "era": "Battle of Saragarhi, 1897 CE"},
    {"place": "Raigad", "era": "Maratha Empire, c. 1674 CE"},
    {"place": "Chittorgarh", "era": "Kingdom of Mewar, c. 1568 CE"},
    {"place": "Sinhagad", "era": "Maratha Empire, c. 1670 CE"},
    {"place": "Anandpur Sahib", "era": "Khalsa, c. 1699 CE"}
]

async def process_target(target):
    place = target["place"]
    era = target["era"]
    
    result = {
        "walkthrough_success": False,
        "image_attempts": 0,
        "image_successes": 0,
        "skipped": False
    }
    
    # 1. Check if it already exists
    existing = await find_walkthrough_by_place_era(place, era)
    if existing:
        print(f"[SKIP] {place} ({era}) is already cached in MongoDB.")
        result["skipped"] = True
        return result
        
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
            result["image_attempts"] += 1
            image_url = await generate_image_with_fallback(stop["image_prompt"])
            
            # Check if it is the placeholder
            is_placeholder = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=" in image_url if image_url else True
            if not is_placeholder:
                result["image_successes"] += 1
                
            stop["image_url"] = image_url
            stop["generated"] = True
            
            # Add a short delay to avoid rate limits on free image services
            await asyncio.sleep(2.5)
            
        # 4. Save to Database
        await save_walkthrough(state_dict)
        print(f"[SUCCESS] Saved {place} to MongoDB!")
        result["walkthrough_success"] = True
        return result
        
    except Exception as e:
        print(f"[ERROR] Failed on {place} ({era}): {e}")
        return result

async def main():
    print("Initializing Database...")
    await init_db()
    
    walkthrough_success_count = 0
    total_targets = len(TARGETS)
    
    total_image_attempts = 0
    total_image_successes = 0
    
    print(f"Starting batch validation for {total_targets} targets...\n")
    for target in TARGETS:
        res = await process_target(target)
        if res["skipped"] or res["walkthrough_success"]:
            walkthrough_success_count += 1
            
        total_image_attempts += res["image_attempts"]
        total_image_successes += res["image_successes"]
            
    print(f"\n--- BATCH VALIDATION COMPLETE ---")
    print(f"Walkthrough Gen Success Rate: {walkthrough_success_count}/{total_targets} ({(walkthrough_success_count/total_targets)*100:.1f}%)")
    
    if total_image_attempts > 0:
        print(f"Image Gen Success Rate: {total_image_successes}/{total_image_attempts} ({(total_image_successes/total_image_attempts)*100:.1f}%)")
    else:
        print("Image Gen Success Rate: N/A (0 attempts)")
    
    if (walkthrough_success_count/total_targets) >= 0.9:
        print("[SUCCESS] Day 3 Metric (>90%) Achieved (Walkthroughs)!")
    else:
        print("[FAILED] Failed to reach >90% metric on Walkthroughs.")
        
    await close_db()

if __name__ == "__main__":
    asyncio.run(main())
