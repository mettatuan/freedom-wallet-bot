"""
Test Auto-Fix Handlers — Quick validation
"""
import asyncio
import sqlite3
import sys
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.core.auto_fix_handlers import (
    try_auto_fix,
    fix_database_locked,
    fix_ssl_certificate_error,
    fix_connection_reset,
)


async def test_db_locked():
    """Test DB lock auto-fix."""
    print("\n" + "="*60)
    print("TEST 1: Database Locked Error")
    print("="*60)
    
    error = sqlite3.OperationalError("database is locked")
    result = await try_auto_fix(error, {"test": "db_lock"})
    
    if result:
        print(f"✅ Auto-fix applied:")
        print(f"   Success: {result.success}")
        print(f"   Action: {result.action_taken}")
        print(f"   Should Retry: {result.should_retry}")
        print(f"   Retry Delay: {result.retry_delay}s")
    else:
        print("❌ No auto-fix handler found")


async def test_ssl_error():
    """Test SSL error auto-fix."""
    print("\n" + "="*60)
    print("TEST 2: SSL Certificate Error")
    print("="*60)
    
    error = Exception("SSL: CERTIFICATE_VERIFY_FAILED")
    result = await try_auto_fix(error, {"test": "ssl_error"})
    
    if result:
        print(f"✅ Auto-fix applied:")
        print(f"   Success: {result.success}")
        print(f"   Action: {result.action_taken}")
        print(f"   Should Retry: {result.should_retry}")
    else:
        print("❌ No auto-fix handler found")


async def test_connection_reset():
    """Test connection reset auto-fix."""
    print("\n" + "="*60)
    print("TEST 3: Connection Reset Error")
    print("="*60)
    
    error = ConnectionResetError("Connection reset by peer")
    result = await try_auto_fix(error, {"test": "conn_reset"})
    
    if result:
        print(f"✅ Auto-fix applied:")
        print(f"   Success: {result.success}")
        print(f"   Action: {result.action_taken}")
        print(f"   Should Retry: {result.should_retry}")
    else:
        print("❌ No auto-fix handler found")


async def test_unknown_error():
    """Test that unknown errors return None."""
    print("\n" + "="*60)
    print("TEST 4: Unknown Error (should return None)")
    print("="*60)
    
    error = ValueError("Some random error")
    result = await try_auto_fix(error, {"test": "unknown"})
    
    if result:
        print(f"❌ Unexpected: Auto-fix applied to unknown error")
        print(f"   Action: {result.action_taken}")
    else:
        print("✅ Correctly returned None for unknown error")


async def main():
    print("\n🔧 AUTO-FIX HANDLERS TEST SUITE")
    print("="*60)
    
    await test_db_locked()
    await test_ssl_error()
    await test_connection_reset()
    await test_unknown_error()
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
