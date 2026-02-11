"""
Test API trực tiếp với requests.post để debug
"""
import requests
import json

url = "https://script.google.com/macros/s/AKfycbxuVMMtTGXIrWphC3qzTTm5uudBLWunQzWONDEFX8RAoi3AiL0fXUbPz9MpEv_IWOpZ/exec"

payload = {
    "action": "ping",
    "spreadsheet_id": "1Vlq3MAplg_FtpaOqqcvgz1UNMfemHiQcKFcdfE4nOtI",
    "api_key": "fwb_bot_testing_2026"
}

print("📡 Testing direct POST request...")
print(f"🔗 URL: {url}")
print(f"📦 Payload: {json.dumps(payload, indent=2)}")
print("\n" + "="*70)

try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"✅ Status Code: {response.status_code}")
    print(f"📄 Response:")
    
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")
