import requests
import json
import urllib3
from datetime import datetime
import os

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === CONFIG ===
API_URL = "https://app-api-pk.cloud.aau.dk/api/generate"
MODEL_NAME = "gemma3_t:latest"   # I created custom model by modifying modelfile of gemma3_12b
ARTICLES = "data/raw_articles.json"
PROMPT_FILE = "prompts/translate.txt"
USAGE_LOG_FOLDER = "usage"
OUTPUT_JSON = "data/translated_articles.json"


# Load articles
with open(ARTICLES, "r", encoding="utf-8") as f:
    articles = json.load(f)

# Prepare headers for the HTTP request
headers = {
    "Content-Type": "application/json"
}

# Process each article
translated_articles = []
for article in articles:
    full_prompt = f"{article['title']}\n\n{article['text']}"
    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "seed": 101,
            "temperature": 0.5
        }
    }
    json_data = json.dumps(payload)

    # Send request to the API
    response = requests.post(API_URL, headers=headers, data=json_data, verify=False)
    if response.status_code == 200:
        response_data = response.json()
        translated_articles.append({
            "translated_title": response_data.get("response").split('\n')[0],  # Assumes first line is the translated title
            "translated_text": "\n".join(response_data.get("response").split('\n')[1:])  # Assumes rest is the translated text
        })
    else:
        print(f"Error translating article {article['title']}: {response.status_code} - {response.text}")

# Save translated articles to a JSON file
os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(translated_articles, f, indent=4)

print(f"✅ All translated articles saved to {OUTPUT_JSON}")
