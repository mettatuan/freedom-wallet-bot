"""
Cleanup Duplicate Payment Verifications & Sync to Google Sheets
- Xóa yêu cầu trùng lặp (cùng user, cùng trạng thái PENDING)
- Đồng bộ tất cả vào Google Sheets với tô màu
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from bot.utils.database import get_db, PaymentVerification, User
from bot.utils.sheets import get_sheets_client
from config.settings import settings
from loguru import logger


async def cleanup_duplicate_verifications():
    """Xóa các yêu cầu thanh toán trùng lặp"""
    
    print("\n" + "="*60)
    print("🧹 CLEANUP DUPLICATE PAYMENT VERIFICATIONS")
    print("="*60 + "\n")
    
    db = next(get_db())
    
    # Lấy tất cả PENDING verifications
    pending = db.query(PaymentVerification).filter(
        PaymentVerification.status == "PENDING"
    ).order_by(PaymentVerification.user_id, PaymentVerification.created_at).all()
    
    print(f"📊 Tìm thấy {len(pending)} yêu cầu PENDING\n")
    
    # Group by user_id
    user_verifications = {}
    for ver in pending:
        if ver.user_id not in user_verifications:
            user_verifications[ver.user_id] = []
        user_verifications[ver.user_id].append(ver)
    
    # Tìm duplicates (cùng user có nhiều hơn 1 PENDING request)
    duplicates_to_delete = []
    
    for user_id, verifications in user_verifications.items():
        if len(verifications) > 1:
            user = db.query(User).filter(User.id == user_id).first()
            username = user.username if user else "N/A"
            full_name = user.full_name if user else "N/A"
            
            print(f"👤 User: {full_name} (@{username}) - ID: {user_id}")
            print(f"   Có {len(verifications)} yêu cầu PENDING:")
            
            # Giữ lại cái mới nhất, xóa các cái cũ
            verifications.sort(key=lambda x: x.created_at, reverse=True)
            
            keep = verifications[0]
            delete = verifications[1:]
            
            print(f"   ✅ Giữ lại: VER{keep.id} ({keep.created_at})")
            
            for ver in delete:
                print(f"   ❌ Xóa: VER{ver.id} ({ver.created_at})")
                duplicates_to_delete.append(ver)
            
            print()
    
    if duplicates_to_delete:
        print(f"\n🗑️  Tổng cộng {len(duplicates_to_delete)} yêu cầu trùng lặp sẽ bị xóa\n")
        
        # Auto confirm (for automation)
        print("✅ Tự động xác nhận xóa...\n")
        
        for ver in duplicates_to_delete:
            db.delete(ver)
        db.commit()
        print(f"\n✅ Đã xóa {len(duplicates_to_delete)} yêu cầu trùng lặp!")
    else:
        print("✅ Không có yêu cầu trùng lặp nào!")
    
    db.close()
    return True


async def sync_all_to_sheets():
    """Đồng bộ tất cả payment verifications vào Google Sheets"""
    
    print("\n" + "="*60)
    print("📊 SYNC TO GOOGLE SHEETS")
    print("="*60 + "\n")
    
    try:
        # Get sheets client
        client = get_sheets_client()
        if not client:
            print("❌ Không thể kết nối Google Sheets")
            return False
        
        # Open spreadsheet
        sheet_id = settings.SUPPORT_SHEET_ID
        spreadsheet = client.open_by_key(sheet_id)
        
        print(f"✅ Đã mở sheet: {spreadsheet.title}\n")
        
        # Get or create "Payments" worksheet
        try:
            worksheet = spreadsheet.worksheet("Payments")
            print("✅ Worksheet 'Payments' đã tồn tại")
            
            # Clear existing data but keep structure
            worksheet.clear()
            
        except:
            worksheet = spreadsheet.add_worksheet(title="Payments", rows=1000, cols=11)
            print("✅ Tạo worksheet 'Payments' mới")
        
        # Set headers
        headers = [
            'Mã Xác Nhận',
            'User ID',
            'Username',
            'Họ Tên',
            'Số Tiền (VND)',
            'Trạng Thái',
            'Ngày Tạo',
            'Ngày Duyệt',
            'Admin Duyệt',
            'Ghi Chú',
            'Gói'
        ]
        
        worksheet.update('A1:K1', [headers])
        
        # Format header
        worksheet.format('A1:K1', {
            'backgroundColor': {'red': 0.2, 'green': 0.2, 'blue': 0.2},
            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
            'horizontalAlignment': 'CENTER'
        })
        
        print("✅ Đã set headers\n")
        
        # Get all verifications from database
        db = next(get_db())
        verifications = db.query(PaymentVerification).order_by(
            PaymentVerification.created_at.desc()
        ).all()
        
        print(f"📋 Tìm thấy {len(verifications)} yêu cầu thanh toán")
        print(f"   - PENDING: {sum(1 for v in verifications if v.status == 'PENDING')}")
        print(f"   - APPROVED: {sum(1 for v in verifications if v.status == 'APPROVED')}")
        print(f"   - REJECTED: {sum(1 for v in verifications if v.status == 'REJECTED')}\n")
        
        # Prepare data
        rows = []
        for ver in verifications:
            user = db.query(User).filter(User.id == ver.user_id).first()
            
            row = [
                f"VER{ver.id}",
                str(ver.user_id),
                user.username if user else "N/A",
                user.full_name if user and user.full_name else "N/A",
                ver.amount,
                ver.status,
                ver.created_at.strftime('%Y-%m-%d %H:%M:%S') if ver.created_at else "",
                ver.approved_at.strftime('%Y-%m-%d %H:%M:%S') if ver.approved_at else "",
                str(ver.approved_by) if ver.approved_by else "",
                ver.notes if ver.notes else "",
                "PREMIUM_365" if ver.status == "APPROVED" else ""
            ]
            rows.append(row)
        
        # Update all rows at once
        if rows:
            # Resize worksheet to fit data
            worksheet.resize(rows=len(rows)+1, cols=11)
            
            worksheet.update(f'A2:K{len(rows)+1}', rows, value_input_option='USER_ENTERED')
            print(f"✅ Đã ghi {len(rows)} dòng vào sheet\n")
            
            # Apply color formatting based on status
            print("🎨 Đang tô màu theo trạng thái...\n")
            
            requests = []
            for idx, ver in enumerate(verifications):
                row_idx = idx + 1  # Row 0 is header, data starts at row 1 (index)
                
                # Set background color based on status
                if ver.status == "APPROVED":
                    color = {'red': 0.7, 'green': 1, 'blue': 0.7}  # Light green
                elif ver.status == "REJECTED":
                    color = {'red': 1, 'green': 0.7, 'blue': 0.7}  # Light red
                else:  # PENDING
                    color = {'red': 1, 'green': 1, 'blue': 0.7}  # Light yellow
                
                requests.append({
                    'repeatCell': {
                        'range': {
                            'sheetId': worksheet.id,
                            'startRowIndex': row_idx,
                            'endRowIndex': row_idx + 1,
                            'startColumnIndex': 0,
                            'endColumnIndex': 11
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': color
                            }
                        },
                        'fields': 'userEnteredFormat.backgroundColor'
                    }
                })
            
            # Batch update colors
            if requests:
                spreadsheet.batch_update({'requests': requests})
                print("✅ Đã tô màu:")
                print("   🟢 APPROVED = Xanh lá")
                print("   🔴 REJECTED = Đỏ")
                print("   🟡 PENDING = Vàng\n")
        
        db.close()
        
        print("="*60)
        print(f"✅ HOÀN TẤT! Xem sheet:")
        print(f"https://docs.google.com/spreadsheets/d/{sheet_id}/")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main function"""
    
    print("\n" + "🔧 "*20)
    print("     CLEANUP & SYNC PAYMENT VERIFICATIONS")
    print("🔧 "*20 + "\n")
    
    # Step 1: Cleanup duplicates
    cleaned = await cleanup_duplicate_verifications()
    
    if not cleaned:
        print("\n⚠️  Cleanup bị hủy. Bỏ qua sync.")
        return
    
    # Step 2: Sync to sheets
    await sync_all_to_sheets()
    
    print("\n✅ XONG! Bây giờ bạn có thể:")
    print("   1. Mở Google Sheets để xem tất cả payments")
    print("   2. Duyệt các yêu cầu PENDING (màu vàng)")
    print("   3. Kiểm tra ai đã thanh toán (màu xanh)\n")


if __name__ == "__main__":
    asyncio.run(main())
