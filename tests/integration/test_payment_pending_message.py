"""
Test Message Length - Simulate actual /payment_pending message
"""
import sys
from pathlib import Path
import html

sys.path.insert(0, str(Path(__file__).parent))

from bot.utils.database import get_db, PaymentVerification, User
from datetime import datetime


def simulate_payment_pending_message():
    """Simulate the exact message that /payment_pending will send"""
    
    print("\n" + "="*70)
    print("📋 SIMULATING /payment_pending MESSAGE")
    print("="*70 + "\n")
    
    db = next(get_db())
    pending = db.query(PaymentVerification).filter(
        PaymentVerification.status == "PENDING"
    ).order_by(PaymentVerification.created_at.desc()).all()
    
    if not pending:
        print("❌ Không có PENDING verification nào")
        db.close()
        return
    
    # Build message exactly like in admin_payment.py
    message = "<b>🔍 YÊU CẦU XÁC NHẬN THANH TOÁN</b>\n\n"
    
    for verification in pending[:10]:  # Show max 10
        user = db.query(User).filter(User.id == verification.user_id).first()
        username = user.username if user else "Unknown"
        safe_username = html.escape(username)
        
        time_ago = (datetime.utcnow() - verification.created_at).total_seconds() / 60
        
        # Escape transaction info and replace newlines with spaces
        transaction_preview = verification.transaction_info[:100].replace('\n', ' ').replace('\r', ' ')
        safe_transaction_info = html.escape(transaction_preview)
        
        message += f"""━━━━━━━━━━━━━━━━━━━━━
<b>VER{verification.id}</b> - {safe_username} (ID: {verification.user_id})
💰 Số tiền: {verification.amount:,.0f} VNĐ
⏱️ {time_ago:.0f} phút trước
📝 {safe_transaction_info}...

Dùng: <code>/payment_approve VER{verification.id}</code> hoặc <code>/payment_reject VER{verification.id}</code>

"""
    
    if len(pending) > 10:
        message += f"\n... và {len(pending) - 10} yêu cầu khác"
    
    db.close()
    
    # Analyze message
    print(f"Total length: {len(message)} characters")
    print(f"Total length: {len(message.encode('utf-8'))} bytes\n")
    
    print("="*70)
    print("FULL MESSAGE:")
    print("="*70)
    print(message)
    print("="*70)
    
    # Check byte offset 704
    if len(message.encode('utf-8')) >= 704:
        print(f"\n⚠️ Byte 704 area:")
        message_bytes = message.encode('utf-8')
        start = max(0, 700)
        end = min(len(message_bytes), 710)
        chunk = message_bytes[start:end]
        print(f"  Bytes {start}-{end}: {repr(chunk)}")
        print(f"  Decoded: {chunk.decode('utf-8', errors='ignore')}")
    
    # Validate HTML
    print(f"\n✅ Message validation:")
    print(f"  - Contains <b>: {message.count('<b>')}")
    print(f"  - Contains </b>: {message.count('</b>')}")
    print(f"  - Contains <code>: {message.count('<code>')}")
    print(f"  - Contains </code>: {message.count('</code>')}")
    
    if message.count('<b>') != message.count('</b>'):
        print("  ⚠️ WARNING: Unbalanced <b> tags!")
    if message.count('<code>') != message.count('</code>'):
        print("  ⚠️ WARNING: Unbalanced <code> tags!")
    
    # Try to send (simulation)
    print(f"\n📤 Ready to send via Telegram API")
    print(f"  parse_mode: HTML")
    print(f"  Length OK: {len(message) < 4096}") # Telegram limit
    
    print("\n="*70)
    print("✅ SIMULATION COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    simulate_payment_pending_message()
