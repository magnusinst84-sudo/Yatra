import os
import sys
import asyncio
import base64
from dotenv import load_dotenv

# Load env before importing our services
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from backend.services.image_gen import generate_image_with_fallback

async def main():
    print("Sending request to Pollinations.ai (may take 5-10 seconds)...")
    prompt = "A high quality, cinematic view of the ancient city of Taxila during the Maurya Empire, bustling market, terracotta architecture, monks walking, ultra realistic."
    
    img_url = await generate_image_with_fallback(prompt)
    
    if not img_url:
        print("Error: No image URL returned.")
        return

    if img_url.startswith("data:image"):
        # Split off the data URL prefix
        header, encoded = img_url.split(",", 1)
        image_data = base64.b64decode(encoded)
        
        # Save to the root folder
        output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "review_image.jpg"))
        with open(output_path, "wb") as f:
            f.write(image_data)
            
        print("\n✅ SUCCESS!")
        print(f"Image saved to: {output_path}")
        print("Just double-click 'review_image.jpg' in your file explorer (or in VS Code) to see it!")
    else:
        print("Returned string is not a base64 data URL.")
        print(img_url[:100])

if __name__ == "__main__":
    asyncio.run(main())
