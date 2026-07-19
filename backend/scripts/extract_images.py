import asyncio
import os
import sys
import base64
import re

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

async def extract_images():
    await mongo_client.init_db()
    
    # Create an output directory for the images
    out_dir = os.path.join(os.path.dirname(__file__), "extracted_images")
    os.makedirs(out_dir, exist_ok=True)
    
    print("Fetching walkthroughs from MongoDB...")
    walkthroughs = await mongo_client.db.walkthroughs.find({}).to_list(length=None)
    
    print(f"Found {len(walkthroughs)} walkthroughs in DB.")
    
    count = 0
    for w in walkthroughs:
        place = w.get("place", "Unknown").replace(" ", "_").replace("/", "_")
        
        stops = w.get("stops", [])
        for i, stop in enumerate(stops):
            image_url = stop.get("image_url")
            
            # Clean stop name for filename
            stop_name = stop.get("stop_name", f"Stop_{i}")
            # Keep only alphanumeric chars or spaces, then replace spaces with underscores
            stop_name = re.sub(r'[^\w\s]', '', stop_name).strip().replace(' ', '_')
            
            if not image_url:
                continue
                
            # Check if it's our base64 data URL format
            match = re.match(r'data:image/(.*?);base64,(.*)', image_url)
            if match:
                ext = match.group(1)
                if ext == "jpeg":
                    ext = "jpg"
                
                b64_data = match.group(2)
                
                # Check if it is the transparent placeholder to skip it
                if "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=" in b64_data:
                    print(f"Skipping {place} - {stop_name} (Placeholder Image)")
                    continue
                
                try:
                    img_bytes = base64.b64decode(b64_data)
                    filename = f"{place}_{i+1}_{stop_name}.{ext}"
                    filepath = os.path.join(out_dir, filename)
                    
                    with open(filepath, "wb") as f:
                        f.write(img_bytes)
                    count += 1
                except Exception as e:
                    print(f"Failed to decode/save image for {place} stop {i+1}: {e}")
            else:
                print(f"Skipping {place} stop {i+1} (not a standard base64 data URL)")
                
    await mongo_client.close_db()
    print(f"\nSuccessfully extracted {count} images to: {out_dir}")

if __name__ == '__main__':
    asyncio.run(extract_images())
