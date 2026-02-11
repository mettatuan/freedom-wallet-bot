"""
Test addTransaction API call
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from bot.utils.database import get_db, User
import requests
import json

user_id = 6588506476

db = next(get_db())
user = db.query(User).filter(User.id == user_id).first()

print("\n" + "="*80)
print("🧪 TEST addTransaction API")
print("="*80)

if user and user.web_app_url:
    print(f"\n📝 User: {user.username}")
    print(f"   API URL: {user.web_app_url}")
    
    # Test payload
    payload = {
        "action": "addTransaction",
        "spreadsheet_id": user.spreadsheet_id,
        "api_key": "fwb_bot_testing_2026",
        "data": {
            "date": "10/02/2026",
            "type": "Chi",
            "amount": 37000,
            "category": "Ăn uống",
            "categoryId": "CAT041",
            "note": "cafe",
            "jar": "NEC",
            "account": "Cash"
        }
    }
    
    print(f"\n📦 Payload:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    print(f"\n🔄 Calling API...")
    print("-" * 80)
    
    try:
        response = requests.post(
            user.web_app_url,
            json=payload,
            timeout=20
        )
        
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        print(f"\n📄 Response Body:")
        print(response.text[:1000])
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"\n✅ JSON Response:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except:
                print("\n⚠️ Not JSON response")
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            
    except Exception as e:
        print(f"\n💥 EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\n❌ User or web_app_url not found!")

print("\n" + "="*80 + "\n")
db.close()
