import os
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

api_key = os.environ.get("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)
if response.status_code == 200:
    models = response.json().get('models', [])
    for m in models:
        print(f"{m['name']} - {m.get('supportedGenerationMethods', [])}")
else:
    print(f"Failed: {response.status_code}")
    print(response.text)
