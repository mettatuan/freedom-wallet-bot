"""
Smart Cleanup - Preserve Multi-Year Payment History
- Giữ tất cả APPROVED từ các năm khác nhau (payment history)
- Xóa PENDING duplicates
- Xóa APPROVED duplicates trong cùng tháng (keep newest)
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from bot.utils.database import get_db, PaymentVerification, User
from loguru import logger


def get_period_key(dt):
    """Get year-month key for grouping"""
    if not dt:
        return "unknown"
    return f"{dt.year}-{dt.month:02d}"


async def smart_cleanup():
    """
    Smart cleanup preserving multi-year history:
    1. Group verifications by user + period (year-month)
    2. Within each period: Keep 1 APPROVED (newest), delete duplicates
    3. Across periods: Keep ALL APPROVED (payment history)
    4. Delete all PENDING duplicates (keep newest)
    """
    
    print("\n" + "="*70)
    print("🧹 SMART CLEANUP - PRESERVE MULTI-YEAR HISTORY")
    print("="*70 + "\n")
    
    db = next(get_db())
    
    # Get all verifications
    all_vers = db.query(PaymentVerification).order_by(
        PaymentVerification.user_id,
        PaymentVerification.created_at.desc()
    ).all()
    
    print(f"📦 Tổng cộng: {len(all_vers)} yêu cầu\n")
    
    # Group by user
    user_verifications = defaultdict(list)
    for ver in all_vers:
        user_verifications[ver.user_id].append(ver)
    
    print(f"👥 Số user: {len(user_verifications)}\n")
    print("="*70)
    
    to_delete = []
    
    for user_id, verifications in user_verifications.items():
        user = db.query(User).filter(User.id == user_id).first()
        username = user.username if user else "N/A"
        full_name = user.full_name if user else "N/A"
        
        print(f"\n👤 {full_name} (@{username}) - ID: {user_id}")
        print(f"   Tổng: {len(verifications)} yêu cầu")
        
        # Group verifications by period (year-month)
        period_groups = defaultdict(list)
        for ver in verifications:
            period = get_period_key(ver.created_at)
            period_groups[period].append(ver)
        
        print(f"   📅 Số periods: {len(period_groups)}")
        
        # Process each period
        for period, vers_in_period in period_groups.items():
            approved_in_period = [v for v in vers_in_period if v.status == "APPROVED"]
            pending_in_period = [v for v in vers_in_period if v.status == "PENDING"]
            rejected_in_period = [v for v in vers_in_period if v.status == "REJECTED"]
            
            print(f"\n      📅 Period {period}:")
            print(f"         🟢 APPROVED: {len(approved_in_period)}")
            print(f"         🟡 PENDING: {len(pending_in_period)}")
            print(f"         🔴 REJECTED: {len(rejected_in_period)}")
            
            # Within this period: Keep only 1 APPROVED (newest)
            if len(approved_in_period) > 1:
                # Sort by created_at desc (newest first)
                approved_in_period.sort(key=lambda x: x.created_at, reverse=True)
                keep_approved = approved_in_period[0]
                delete_approved = approved_in_period[1:]
                
                print(f"         ✅ Giữ: VER{keep_approved.id} (APPROVED - {keep_approved.created_at.strftime('%d/%m %H:%M')})")
                for ver in delete_approved:
                    print(f"         ❌ Xóa: VER{ver.id} (APPROVED duplicate - {ver.created_at.strftime('%d/%m %H:%M')})")
                    to_delete.append(ver)
            
            # Keep only 1 PENDING (newest)
            if len(pending_in_period) > 1:
                pending_in_period.sort(key=lambda x: x.created_at, reverse=True)
                keep_pending = pending_in_period[0]
                delete_pending = pending_in_period[1:]
                
                print(f"         ✅ Giữ: VER{keep_pending.id} (PENDING - {keep_pending.created_at.strftime('%d/%m %H:%M')})")
                for ver in delete_pending:
                    print(f"         ❌ Xóa: VER{ver.id} (PENDING duplicate - {ver.created_at.strftime('%d/%m %H:%M')})")
                    to_delete.append(ver)
            
            # Keep only 1 REJECTED (newest)
            if len(rejected_in_period) > 1:
                rejected_in_period.sort(key=lambda x: x.created_at, reverse=True)
                keep_rejected = rejected_in_period[0]
                delete_rejected = rejected_in_period[1:]
                
                print(f"         ✅ Giữ: VER{keep_rejected.id} (REJECTED - {keep_rejected.created_at.strftime('%d/%m %H:%M')})")
                for ver in delete_rejected:
                    print(f"         ❌ Xóa: VER{ver.id} (REJECTED duplicate - {ver.created_at.strftime('%d/%m %H:%M')})")
                    to_delete.append(ver)
    
    print("\n" + "="*70)
    print(f"\n📊 SUMMARY:")
    print(f"   Total to delete: {len(to_delete)} requests")
    print(f"   Remaining: {len(all_vers) - len(to_delete)} requests")
    print("="*70 + "\n")
    
    if to_delete:
        print("❗ EXECUTING CLEANUP...")
        for ver in to_delete:
            db.delete(ver)
        
        db.commit()
        print(f"✅ Đã xóa {len(to_delete)} duplicate requests!\n")
    else:
        print("✅ Không có duplicate nào cần xóa!\n")
    
    # Show final state
    print("\n" + "="*70)
    print("📊 TRẠNG THÁI SAU KHI CLEANUP:")
    print("="*70 + "\n")
    
    remaining = db.query(PaymentVerification).order_by(
        PaymentVerification.user_id,
        PaymentVerification.created_at.desc()
    ).all()
    
    print(f"📦 Tổng cộng: {len(remaining)} yêu cầu\n")
    
    # Group by user again
    user_verifications_final = defaultdict(list)
    for ver in remaining:
        user_verifications_final[ver.user_id].append(ver)
    
    for user_id, verifications in user_verifications_final.items():
        user = db.query(User).filter(User.id == user_id).first()
        username = user.username if user else "N/A"
        full_name = user.full_name if user else "N/A"
        
        print(f"👤 {full_name} (@{username}) - ID: {user_id}")
        
        for ver in verifications:
            status_emoji = {
                "PENDING": "🟡",
                "APPROVED": "🟢",
                "REJECTED": "🔴"
            }.get(ver.status, "⚪")
            
            date_str = ver.created_at.strftime('%d/%m/%Y %H:%M') if ver.created_at else "N/A"
            period = get_period_key(ver.created_at)
            
            print(f"   {status_emoji} VER{ver.id:3d} | {ver.status:8s} | {date_str} | {ver.amount:,.0f} VND | Period: {period}")
    
    print("\n" + "="*70)
    print("✅ HOÀN TẤT!\n")
    
    db.close()


async def demo_multi_year_scenario():
    """
    Demo scenario: User has multiple APPROVED across different years
    This should preserve ALL of them (payment history)
    """
    
    print("\n" + "="*70)
    print("📚 DEMO: MULTI-YEAR PAYMENT HISTORY")
    print("="*70 + "\n")
    
    print("Scenario: User renews Premium every year")
    print()
    print("2025-02: VER1 APPROVED (999,000 VND) - First year")
    print("2026-02: VER5 APPROVED (999,000 VND) - Renewal year 2")
    print("2027-02: VER10 APPROVED (999,000 VND) - Renewal year 3")
    print()
    print("❌ OLD LOGIC: Would delete VER1, VER5 (keep only newest)")
    print("✅ NEW LOGIC: Keeps ALL 3 (different periods = payment history)")
    print()
    print("💡 Only deletes duplicates within SAME period:")
    print("   Example: 2026-02 has VER5 + VER6 (both APPROVED)")
    print("   → Keeps VER6 (newest), deletes VER5")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    print("\n🤖 Freedom Wallet Bot - Smart Cleanup Tool\n")
    
    # Show demo first
    asyncio.run(demo_multi_year_scenario())
    
    # Run cleanup
    asyncio.run(smart_cleanup())
