"""
Advanced Cleanup - Xóa TẤT CẢ duplicate payments
Giữ lại 1 request mới nhất cho mỗi user
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from bot.utils.database import get_db, PaymentVerification, User
from loguru import logger


async def show_all_verifications():
    """Hiển thị tất cả verifications group by user"""
    
    print("\n" + "="*70)
    print("📊 DANH SÁCH TẤT CẢ PAYMENT VERIFICATIONS")
    print("="*70 + "\n")
    
    db = next(get_db())
    
    # Get all verifications
    all_vers = db.query(PaymentVerification).order_by(
        PaymentVerification.user_id, 
        PaymentVerification.created_at.desc()
    ).all()
    
    print(f"📦 Tổng cộng: {len(all_vers)} yêu cầu\n")
    
    # Group by user
    user_verifications = {}
    for ver in all_vers:
        if ver.user_id not in user_verifications:
            user_verifications[ver.user_id] = []
        user_verifications[ver.user_id].append(ver)
    
    print(f"👥 Số user: {len(user_verifications)}\n")
    print("="*70)
    
    for user_id, verifications in user_verifications.items():
        user = db.query(User).filter(User.id == user_id).first()
        username = user.username if user else "N/A"
        full_name = user.full_name if user else "N/A"
        
        print(f"\n👤 {full_name} (@{username}) - ID: {user_id}")
        print(f"   Tổng: {len(verifications)} yêu cầu")
        
        for ver in verifications:
            status_emoji = {
                "PENDING": "🟡",
                "APPROVED": "🟢",
                "REJECTED": "🔴"
            }.get(ver.status, "⚪")
            
            date_str = ver.created_at.strftime('%d/%m %H:%M') if ver.created_at else "N/A"
            
            print(f"      {status_emoji} VER{ver.id:3d} | {ver.status:8s} | {date_str} | {ver.amount:,.0f} VND")
    
    print("\n" + "="*70 + "\n")
    db.close()
    
    return user_verifications


async def cleanup_strategy_1():
    """
    Strategy 1: Giữ 1 APPROVED request mới nhất mỗi user
    Xóa tất cả PENDING và request APPROVED cũ hơn
    """
    
    print("\n" + "="*70)
    print("🧹 STRATEGY 1: Giữ 1 APPROVED mới nhất/user")
    print("="*70 + "\n")
    
    db = next(get_db())
    
    all_vers = db.query(PaymentVerification).order_by(
        PaymentVerification.user_id,
        PaymentVerification.created_at.desc()
    ).all()
    
    # Group by user
    user_verifications = {}
    for ver in all_vers:
        if ver.user_id not in user_verifications:
            user_verifications[ver.user_id] = []
        user_verifications[ver.user_id].append(ver)
    
    to_delete = []
    to_keep = []
    
    for user_id, verifications in user_verifications.items():
        user = db.query(User).filter(User.id == user_id).first()
        username = user.username if user else "N/A"
        full_name = user.full_name if user else "N/A"
        
        # Tìm APPROVED request mới nhất
        approved = [v for v in verifications if v.status == "APPROVED"]
        pending = [v for v in verifications if v.status == "PENDING"]
        rejected = [v for v in verifications if v.status == "REJECTED"]
        
        if approved:
            # Giữ APPROVED mới nhất
            keep = approved[0]
            to_keep.append(keep)
            
            # Xóa tất cả APPROVED cũ hơn + tất cả PENDING
            delete = approved[1:] + pending + rejected
            
            if delete:
                print(f"👤 {full_name} (@{username})")
                print(f"   ✅ Giữ: VER{keep.id} ({keep.status}) - {keep.created_at.strftime('%d/%m %H:%M')}")
                print(f"   ❌ Xóa {len(delete)} request:")
                for v in delete:
                    print(f"      - VER{v.id} ({v.status}) - {v.created_at.strftime('%d/%m %H:%M')}")
                print()
                
                to_delete.extend(delete)
        
        elif pending:
            # Chưa có APPROVED, giữ 1 PENDING mới nhất
            keep = pending[0]
            to_keep.append(keep)
            
            delete = pending[1:] + rejected
            
            if delete:
                print(f"👤 {full_name} (@{username})")
                print(f"   ⏳ Giữ: VER{keep.id} (PENDING) - {keep.created_at.strftime('%d/%m %H:%M')}")
                print(f"   ❌ Xóa {len(delete)} request:")
                for v in delete:
                    print(f"      - VER{v.id} ({v.status}) - {v.created_at.strftime('%d/%m %H:%M')}")
                print()
                
                to_delete.extend(delete)
        
        elif rejected:
            # Chỉ có REJECTED, giữ 1 mới nhất
            keep = rejected[0]
            to_keep.append(keep)
            
            delete = rejected[1:]
            
            if delete:
                print(f"👤 {full_name} (@{username})")
                print(f"   🔴 Giữ: VER{keep.id} (REJECTED) - {keep.created_at.strftime('%d/%m %H:%M')}")
                print(f"   ❌ Xóa {len(delete)} request cũ hơn")
                print()
                
                to_delete.extend(delete)
    
    if to_delete:
        print(f"\n📊 TỔNG KẾT:")
        print(f"   ✅ Giữ lại: {len(to_keep)} requests")
        print(f"   ❌ Xóa: {len(to_delete)} requests\n")
        
        # Auto confirm
        print("✅ Tự động thực hiện cleanup...\n")
        
        for ver in to_delete:
            db.delete(ver)
        
        db.commit()
        print(f"✅ Đã xóa {len(to_delete)} requests!")
        
    else:
        print("✅ Không có duplicate nào cần xóa!")
    
    db.close()
    return len(to_delete)


async def cleanup_strategy_2():
    """
    Strategy 2: XÓA TẤT CẢ - Giữ 0 request
    Reset hoàn toàn database
    """
    
    print("\n" + "="*70)
    print("🗑️  STRATEGY 2: XÓA TẤT CẢ REQUESTS")
    print("="*70 + "\n")
    
    print("⚠️  CẢNH BÁO: Xóa tất cả payment verifications!")
    print("   Tất cả dữ liệu thanh toán sẽ bị mất.\n")
    
    db = next(get_db())
    
    all_vers = db.query(PaymentVerification).all()
    
    print(f"📊 Tìm thấy {len(all_vers)} requests")
    
    if all_vers:
        print("✅ Tự động xóa tất cả...\n")
        
        for ver in all_vers:
            db.delete(ver)
        
        db.commit()
        print(f"✅ Đã xóa {len(all_vers)} requests!")
    else:
        print("✅ Database đã trống!")
    
    db.close()
    return len(all_vers)


async def main():
    """Main function"""
    
    print("\n" + "🧹 "*25)
    print("          ADVANCED CLEANUP - XÓA TẤT CẢ DUPLICATES")
    print("🧹 "*25 + "\n")
    
    # Step 1: Show current state
    user_vers = await show_all_verifications()
    
    print("🎯 CHỌN STRATEGY:\n")
    print("1️⃣  STRATEGY 1: Giữ 1 request mới nhất/user (Recommended)")
    print("     - User có APPROVED → Giữ APPROVED mới nhất")
    print("     - User chỉ có PENDING → Giữ PENDING mới nhất")
    print("     - Xóa tất cả duplicate\n")
    
    print("2️⃣  STRATEGY 2: XÓA TẤT CẢ (Reset database)")
    print("     - Xóa hết tất cả payment verifications")
    print("     - Bắt đầu lại từ đầu\n")
    
    print("Chọn Strategy 1 (Recommended)...\n")
    
    deleted = await cleanup_strategy_1()
    
    if deleted > 0:
        print("\n" + "="*70)
        print("✅ CLEANUP THÀNH CÔNG!")
        print(f"   Đã xóa {deleted} duplicate requests")
        print("="*70 + "\n")
        
        # Show final state
        print("📊 TRẠNG THÁI SAU KHI CLEANUP:\n")
        await show_all_verifications()


if __name__ == "__main__":
    asyncio.run(main())
