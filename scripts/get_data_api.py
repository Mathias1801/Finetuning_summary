import requests
from datetime import date
import os
import json

# Server info
API_URL = "http://130.225.39.127:8000/get_articles/"

# Get today's date in YYYY-MM-DD format
today = date.today().isoformat()

# Send GET request with date parameter
response = requests.get(API_URL, params={"date": today})

# Prepare data folder
output_dir = "data"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "raw_articles.json")

# Check response
if response.status_code == 200:
    articles = response.json()
    
    # Filter articles to include only those with a non-null title
    filtered_articles = [article for article in articles if article['title'] is not None]

    # Save filtered articles to file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(filtered_articles, f, ensure_ascii=False, indent=4)
    
    print(f"✅ {len(filtered_articles)} articles saved to {output_file}")
else:
    print(f"❌ Error: {response.status_code} - {response.text}")
