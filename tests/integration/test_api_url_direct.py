"""
Check API URL và test trực tiếp
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from bot.utils.database import get_db, User
import requests

user_id = 6588506476

db = next(get_db())
user = db.query(User).filter(User.id == user_id).first()

print("\n" + "="*80)
print("🔍 API URL CHECK")
print("="*80)

if user:
    print(f"\n📝 User: {user.username}")
    print(f"   Spreadsheet ID: {user.spreadsheet_id}")
    print(f"   Web App URL: {user.web_app_url}")
    
    if user.web_app_url:
        print(f"\n🧪 Testing API with ping...")
        print("-" * 80)
        
        try:
            response = requests.post(
                user.web_app_url,
                json={
                    "action": "ping",
                    "spreadsheet_id": user.spreadsheet_id,
                    "api_key": "fwb_bot_testing_2026"
                },
                timeout=10
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            if response.status_code == 200:
                print("\n✅ API URL WORKS!")
            else:
                print(f"\n❌ API ERROR: {response.status_code}")
                
        except Exception as e:
            print(f"\n💥 EXCEPTION: {e}")
    else:
        print("\n❌ No web_app_url set!")
else:
    print(f"\n❌ User not found!")

print("\n" + "="*80 + "\n")
db.close()
