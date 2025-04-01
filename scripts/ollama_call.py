import requests
import json
import urllib3
from datetime import datetime
import os

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === CONFIG ===
API_URL = "https://app-api-pk.cloud.aau.dk/api/generate"
MODEL_NAME = "gemma3:1b"  # ("gemma3:1b" ; "gemma3:4b" ; "gemma3:12b" ; "gemma3:27b")
ARTICLES = "data/translated_articles.json"
PROMPT = "prompts/create_report.txt"
USAGE_LOG_FOLDER = "usage"
REPORT_FOLDER = "reports"


# === Load Articles ===
with open(ARTICLES, "r", encoding="utf-8") as f:
    articles = json.load(f)

# Combine all article texts into one
article_texts = "\n\n".join(article["translated_text"] for article in articles if article.get("translated_text"))


with open(PROMPT, "r", encoding="utf-8") as f:
    instructions = f.read().strip()

# === Construct the full prompt ===
full_prompt = instructions + "\n\n" + article_texts

# === Prepare Request ===
headers = {
    "Content-Type": "application/json"
}
payload = {
    "model": MODEL_NAME,
    "prompt": full_prompt,
    "stream": False,
    "options": {
        "seed": 101,
        "temperature": 0.7
    }
}
json_data = json.dumps(payload)

# === Log nvidia-smi ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
os.makedirs(USAGE_LOG_FOLDER, exist_ok=True)
try:
    import subprocess
    smi_output = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=timestamp,power.draw,memory.used,utilization.gpu", "--format=csv,nounits,noheader"],
        universal_newlines=True
    )
    usage = {
        "timestamp": timestamp,
        "model": MODEL_NAME,
        "prompt_file": PROMPT,
        "nvidia_smi": smi_output.strip()
    }
    usage_file = os.path.join(USAGE_LOG_FOLDER, f"usage_{MODEL_NAME.replace(':', '_')}_{timestamp}.json")
    with open(usage_file, "w", encoding="utf-8") as f:
        json.dump(usage, f, indent=4)
except Exception as e:
    print("⚠️ Failed to log nvidia-smi:", str(e))

# === Make API Call ===
response = requests.post(API_URL, headers=headers, data=json_data, verify=False)

if response.status_code == 200:
    result = response.json()
    report_text = result.get("response", "").strip()

    # Save report to /reports/
    os.makedirs(REPORT_FOLDER, exist_ok=True)
    report_file = os.path.join(REPORT_FOLDER, f"report_{MODEL_NAME.replace(':', '_')}_{timestamp}.md")
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_text)
    
    print(f"✅ Report saved to {report_file}")
    print("\n📝 Preview:\n")
    print(report_text[:500] + "...\n")

else:
    print(f"❌ Error: {response.status_code} - {response.text}")