"""
Quick test to verify if API URL is working
Run this before running full cache performance test
"""
import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

async def test_api_url():
    """Test if API URL responds correctly"""
    
    api_url = os.getenv("FREEDOM_WALLET_API_URL", "")
    api_key = os.getenv("FREEDOM_WALLET_API_KEY", "")
    
    print("=" * 60)
    print("🔍 API URL CONNECTIVITY TEST")
    print("=" * 60)
    print()
    
    if not api_url:
        print("❌ FREEDOM_WALLET_API_URL not found in .env")
        print("   Please add it to .env file")
        return False
    
    if not api_key:
        print("❌ FREEDOM_WALLET_API_KEY not found in .env")
        print("   Please add it to .env file")
        return False
    
    print(f"🔗 Testing URL:")
    print(f"   {api_url[:70]}...")
    print()
    print(f"🔑 Using API Key:")
    print(f"   {api_key}")
    print()
    
    # Test with ping action
    payload = {
        "action": "ping",
        "api_key": api_key,
        "spreadsheet_id": "test"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                api_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                status = response.status
                
                if status == 200:
                    result = await response.json()
                    
                    print(f"✅ HTTP Status: {status} OK")
                    print(f"✅ Response: {result}")
                    print()
                    
                    if result.get("success"):
                        print("=" * 60)
                        print("✅ ✅ ✅ API URL IS WORKING!")
                        print("=" * 60)
                        return True
                    else:
                        print("⚠️ API responded but returned error:")
                        print(f"   {result.get('error')}")
                        return False
                
                elif status == 404:
                    print(f"❌ HTTP Status: {status} Not Found")
                    print()
                    print("🔧 PROBLEM: Web App deployment không tồn tại")
                    print()
                    print("📋 SOLUTIONS:")
                    print("   1. Open Apps Script: https://script.google.com/home")
                    print("   2. Find 'Freedom Wallet' project")
                    print("   3. Deploy → Manage deployments")
                    print("   4. Copy Web app URL")
                    print("   5. Update .env: FREEDOM_WALLET_API_URL=<new_url>")
                    print()
                    print("📄 See fix_api_url.md for detailed guide")
                    return False
                
                elif status == 302 or status == 301:
                    print(f"⚠️ HTTP Status: {status} Redirect")
                    print()
                    print("🔧 PROBLEM: Authorization required")
                    print()
                    print("📋 FIX:")
                    print("   1. Apps Script → Deploy → Manage deployments")
                    print("   2. Edit deployment (pencil icon)")
                    print("   3. Who has access: Anyone")
                    print("   4. Update")
                    return False
                
                else:
                    error_text = await response.text()
                    print(f"❌ HTTP Status: {status}")
                    print(f"   Response: {error_text[:200]}")
                    return False
                    
    except aiohttp.ClientError as e:
        print(f"❌ Network error: {e}")
        print()
        print("🔧 Check:")
        print("   - Internet connection")
        print("   - URL is complete (ends with /exec)")
        print("   - No firewall blocking")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    print()
    success = asyncio.run(test_api_url())
    print()
    
    if success:
        print("🚀 Ready to run: python test_cache_performance.py")
    else:
        print("⚠️ Fix API URL first, then try again")
        print("📖 Read: fix_api_url.md for help")
    print()
