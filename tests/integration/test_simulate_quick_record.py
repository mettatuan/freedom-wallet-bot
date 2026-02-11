"""
Simulate bot processing "37k cafe" message
"""
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from bot.utils.database import get_db, User
from bot.services.sheets_api_client import SheetsAPIClient

async def test_quick_record():
    user_id = 6588506476
    
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()

    print("\n" + "="*80)
    print("🧪 SIMULATE QUICK RECORD: 37k cafe")
    print("="*80)
    
    if user:
        print(f"\n📝 User: {user.username}")
        print(f"   Spreadsheet ID: {user.spreadsheet_id}")
        print(f"   Web App URL: {user.web_app_url}")
        
        print(f"\n🔧 Creating SheetsAPIClient...")
        print("-" * 80)
        
        # This will trigger __init__ logging
        client = SheetsAPIClient(user.spreadsheet_id, user.web_app_url)
        
        print(f"\n📤 Calling add_transaction...")
        print("-" * 80)
        
        try:
            result = await client.add_transaction(
                amount=37000,
                category="Ăn uống",
                note="cafe",
                transaction_type="Chi",
                from_jar="NEC",
                from_account="Cash"
            )
            
            print(f"\n✅ Result:")
            print(f"   Success: {result.get('success')}")
            if result.get('success'):
                print(f"   Transaction ID: {result.get('transactionId')}")
                print(f"   Message: {result.get('message')}")
            else:
                print(f"   Error: {result.get('error')}")
                
        except Exception as e:
            print(f"\n💥 EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"\n❌ User not found!")
    
    print("\n" + "="*80 + "\n")
    db.close()

if __name__ == "__main__":
    asyncio.run(test_quick_record())
