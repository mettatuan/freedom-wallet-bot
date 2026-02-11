"""Test new deployment with dd/MM/yyyy date format"""
import sys
sys.path.insert(0, 'D:\\Projects\\FreedomWalletBot')

import asyncio
from bot.services.sheets_api_client import SheetsAPIClient

async def test_new_deployment():
    """Test ping and getCategories with new URL"""
    # Load from environment
    from dotenv import load_dotenv
    load_dotenv()
    import os
    
    spreadsheet_id = os.getenv("TEST_SPREADSHEET_ID", "1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg")
    client = SheetsAPIClient(spreadsheet_id)
    
    print("🔍 Testing new deployment...")
    print(f"URL: {client.api_url}")
    print()
    
    # Test 1: Ping
    print("1️⃣ Test PING...")
    ping_result = await client.ping()
    if ping_result.get("success"):
        print(f"✅ PING: {ping_result.get('message')}")
        print(f"   Timestamp: {ping_result.get('timestamp')}")
    else:
        print(f"❌ PING FAILED: {ping_result.get('error')}")
    
    print()
    
    # Test 2: Get Categories
    print("2️⃣ Test GET CATEGORIES...")
    categories_result = await client.get_categories()
    if categories_result.get("success"):
        categories = categories_result.get('categories', [])
        print(f"✅ Categories: {len(categories)} loaded")
        if categories:
            print(f"   First: {categories[0]['name']} ({categories[0]['type']}) {categories[0].get('icon', '')}")
            # Check investment categories
            investment = [c for c in categories if c['type'] == 'Đầu tư']
            print(f"   Investment categories: {len(investment)}")
            if investment:
                print(f"   - {investment[0]['name']} {investment[0].get('icon', '')}")
    else:
        print(f"❌ GET CATEGORIES FAILED: {categories_result.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_new_deployment())
