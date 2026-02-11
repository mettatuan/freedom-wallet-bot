"""
Quick test to verify add transaction works after DateHelper fix
"""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from bot.services.sheets_api_client import SheetsAPIClient

async def test_add_transaction():
    """Test add transaction"""
    
    spreadsheet_id = os.getenv("TEST_SPREADSHEET_ID", "1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg")
    client = SheetsAPIClient(spreadsheet_id)
    
    print("=" * 60)
    print("🧪 TEST ADD TRANSACTION - After DateHelper Fix")
    print("=" * 60)
    print()
    print(f"📊 Spreadsheet: {spreadsheet_id}")
    print()
    
    # Test add transaction
    print("📝 Adding test transaction...")
    result = await client.add_transaction(
        amount=1000,
        category="Test",
        note="Test transaction after DateHelper fix",
        from_jar="NEC",
        from_account="Cash"
    )
    
    print()
    if result.get("success"):
        print("✅ ✅ ✅ SUCCESS!")
        print(f"   Transaction ID: {result.get('transactionId')}")
        print(f"   Message: {result.get('message')}")
        print()
        print("🎉 DateHelper.generateId() is working!")
        print("Bot có thể ghi giao dịch thành công.")
    else:
        print("❌ FAILED")
        print(f"   Error: {result.get('error')}")
        print()
        print("⚠️ Still having issues - check Apps Script logs")
    
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_add_transaction())
