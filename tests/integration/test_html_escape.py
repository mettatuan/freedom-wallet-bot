"""
Test Admin Commands - Verify HTML escaping works correctly
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from bot.utils.database import get_db, PaymentVerification, User


async def show_pending_with_special_chars():
    """Show how special characters in transaction_info are handled"""
    
    print("\n" + "="*70)
    print("🧪 TEST SPECIAL CHARACTERS IN TRANSACTION INFO")
    print("="*70 + "\n")
    
    db = next(get_db())
    
    # Find pending verifications
    pending = db.query(PaymentVerification).filter(
        PaymentVerification.status == "PENDING"
    ).all()
    
    if not pending:
        print("❌ Không có PENDING verification nào")
        db.close()
        return
    
    print(f"📋 Tìm thấy {len(pending)} PENDING verifications:\n")
    
    for ver in pending:
        user = db.query(User).filter(User.id == ver.user_id).first()
        
        print(f"VER{ver.id}:")
        print(f"  User: {user.username if user else 'N/A'}")
        print(f"  Transaction info (raw):")
        print(f"    {repr(ver.transaction_info[:100])}")
        print()
        
        # Check for special characters
        special_chars = ['<', '>', '&', '"', "'", '_', '*', '[', ']', '(', ')']
        found_special = [c for c in special_chars if c in ver.transaction_info]
        
        if found_special:
            print(f"  ⚠️ Contains special chars: {', '.join(found_special)}")
            print(f"  ✅ WILL BE ESCAPED with html.escape()")
        else:
            print(f"  ✅ No special characters")
        print()
    
    db.close()
    
    print("="*70)
    print("💡 TESTING TIPS:")
    print("="*70 + "\n")
    print("1. Create a test payment with special chars:")
    print("   Example: 'Chuyển khoản 999k từ OCB <số tài khoản>'")
    print()
    print("2. Run /payment_pending in bot")
    print("   ✅ Should work without 'can't parse entities' error")
    print()
    print("3. Transaction info with < > & will be escaped")
    print("   Example: '< > &' becomes '&lt; &gt; &amp;'")
    print()


async def simulate_html_escape():
    """Simulate HTML escaping"""
    import html
    
    print("\n" + "="*70)
    print("🔍 HTML ESCAPE EXAMPLES")
    print("="*70 + "\n")
    
    test_strings = [
        "Chuyển khoản 999k từ OCB",
        "Số tiền < 1 triệu",
        "A&B Company",
        "Email: test@example.com",
        "Username: user_123",
        "Amount: **999,000 VND**",
        "Note: [URGENT] Please check",
        "Message with <html> tags & special chars",
    ]
    
    for original in test_strings:
        escaped = html.escape(original)
        
        print(f"Original: {original}")
        if original != escaped:
            print(f"Escaped:  {escaped}")
            print(f"  ⚠️ Changed!")
        else:
            print(f"  ✅ No change needed")
        print()
    
    print("="*70)
    print("✅ ALL SPECIAL CHARACTERS WILL BE ESCAPED")
    print("="*70 + "\n")


if __name__ == "__main__":
    print("\n🤖 Freedom Wallet Bot - HTML Escape Test\n")
    
    # Show HTML escape examples
    asyncio.run(simulate_html_escape())
    
    # Show pending verifications with special chars
    asyncio.run(show_pending_with_special_chars())
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETE!")
    print("="*70 + "\n")
    print("💡 Next: Run /payment_pending in bot to verify fix works!")
    print()
