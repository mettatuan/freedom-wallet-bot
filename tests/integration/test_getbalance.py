"""
Test getBalance with real spreadsheet ID
"""
import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

async def test_getbalance():
    """Test getBalance action"""
    
    api_url = os.getenv("FREEDOM_WALLET_API_URL")
    api_key = os.getenv("FREEDOM_WALLET_API_KEY")
    spreadsheet_id = os.getenv("TEST_SPREADSHEET_ID", "1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg")
    
    print("=" * 60)
    print("🧪 TEST GETBALANCE ACTION")
    print("=" * 60)
    print()
    print(f"📊 Spreadsheet ID: {spreadsheet_id}")
    print()
    
    payload = {
        "action": "getBalance",
        "api_key": api_key,
        "spreadsheet_id": spreadsheet_id
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                api_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                status = response.status
                print(f"HTTP Status: {status}")
                
                if status == 200:
                    result = await response.json()
                    print(f"\n📥 Response:")
                    print(f"   Success: {result.get('success')}")
                    
                    if result.get('success'):
                        print(f"   Total Balance: {result.get('totalBalance', 0):,.0f}đ")
                        print(f"   Jars: {len(result.get('jars', []))} items")
                        print(f"   Accounts: {len(result.get('accounts', []))} items")
                        print("\n✅ ✅ ✅ GETBALANCE WORKS!")
                    else:
                        print(f"   Error: {result.get('error')}")
                        print("\n❌ Action failed")
                        
                        # Check common issues
                        error = result.get('error', '')
                        if 'not found' in error.lower():
                            print("\n🔧 PROBLEM: Spreadsheet không tồn tại hoặc không access được")
                            print("\n📋 CHECKS:")
                            print("   1. Spreadsheet ID đúng?")
                            print(f"      Current: {spreadsheet_id}")
                            print("   2. Sheet có public hoặc shared với Apps Script?")
                            print("   3. Sheet có đúng structure (Tài khoản, Hũ, Giao dịch)?")
                        elif 'permission' in error.lower():
                            print("\n🔧 PROBLEM: Apps Script không có quyền truy cập")
                            print("\n📋 FIX:")
                            print("   1. Open spreadsheet")
                            print("   2. Share → Anyone with link can VIEW")
                            print("   3. Or share directly with Apps Script service account")
                else:
                    text = await response.text()
                    print(f"\n❌ Error: {text[:300]}")
                    
    except Exception as e:
        print(f"\n❌ Exception: {e}")


if __name__ == "__main__":
    asyncio.run(test_getbalance())
