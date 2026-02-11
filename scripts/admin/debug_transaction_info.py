"""
Debug Transaction Info - Find problematic characters
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from bot.utils.database import get_db, PaymentVerification, User


def analyze_transaction_info():
    """Analyze all PENDING transaction_info for problematic characters"""
    
    print("\n" + "="*70)
    print("🔍 ANALYZING TRANSACTION INFO")
    print("="*70 + "\n")
    
    db = next(get_db())
    pending = db.query(PaymentVerification).filter(
        PaymentVerification.status == "PENDING"
    ).all()
    
    if not pending:
        print("❌ Không có PENDING verification nào")
        db.close()
        return
    
    for ver in pending:
        user = db.query(User).filter(User.id == ver.user_id).first()
        
        print(f"\n{'='*70}")
        print(f"VER{ver.id} - {user.username if user else 'N/A'}")
        print(f"{'='*70}\n")
        
        transaction_info = ver.transaction_info
        
        print(f"Length: {len(transaction_info)} characters")
        print(f"Length (bytes): {len(transaction_info.encode('utf-8'))} bytes\n")
        
        # Show first 200 chars with repr
        print("First 200 chars (repr):")
        print(repr(transaction_info[:200]))
        print()
        
        # Find problematic characters
        problematic = []
        for i, char in enumerate(transaction_info):
            if char in '<>&"\'':
                problematic.append((i, char, f"HTML special: {char}"))
            elif char in '_*[]()~`#+-=|{}':
                problematic.append((i, char, f"Markdown special: {char}"))
            elif char == '\n':
                problematic.append((i, char, "Newline"))
            elif char == '\r':
                problematic.append((i, char, "Carriage return"))
            elif char == '\t':
                problematic.append((i, char, "Tab"))
            elif ord(char) < 32 or ord(char) > 126:
                if char not in '\n\r\t' and ord(char) > 127:  # Allow UTF-8
                    pass
                elif ord(char) < 32:
                    problematic.append((i, repr(char), f"Control char: {ord(char)}"))
        
        if problematic:
            print(f"⚠️ Found {len(problematic)} problematic characters:\n")
            for pos, char, desc in problematic[:20]:  # Show first 20
                context_start = max(0, pos - 10)
                context_end = min(len(transaction_info), pos + 10)
                context = transaction_info[context_start:context_end]
                print(f"  Position {pos}: {desc}")
                print(f"    Context: {repr(context)}")
                print()
        else:
            print("✅ No problematic characters found")
        
        # Show what it looks like after processing
        print("\nAfter processing (first 100):")
        processed = transaction_info[:100].replace('\n', ' ').replace('\r', ' ')
        import html
        safe = html.escape(processed)
        print(f"  Original:  {repr(transaction_info[:100])}")
        print(f"  Processed: {repr(processed)}")
        print(f"  Escaped:   {repr(safe)}")
        print()
    
    db.close()
    
    print("="*70)
    print("✅ ANALYSIS COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    analyze_transaction_info()
