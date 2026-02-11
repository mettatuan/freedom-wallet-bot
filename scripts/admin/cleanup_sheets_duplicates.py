"""
Cleanup Duplicate Rows in Google Sheets
Keep only the newest row for each verification_id
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from bot.utils.sheets import get_sheets_client
from config.settings import settings


def cleanup_duplicate_rows():
    """Remove duplicate rows, keep newest for each VER ID"""
    
    print("\n" + "="*70)
    print("🧹 CLEANUP DUPLICATE ROWS IN GOOGLE SHEETS")
    print("="*70 + "\n")
    
    try:
        # Get sheets client
        client = get_sheets_client()
        if not client:
            print("❌ Cannot connect to Google Sheets")
            return
        
        # Open spreadsheet
        sheet_id = settings.SUPPORT_SHEET_ID
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.worksheet("Payments")
        
        print(f"✅ Connected to sheet: {spreadsheet.title}\n")
        
        # Get all values
        all_values = worksheet.get_all_values()
        headers = all_values[0]
        data_rows = all_values[1:]
        
        print(f"📊 Total rows: {len(data_rows)}\n")
        
        # Group by verification_id (column A)
        ver_groups = {}
        for idx, row in enumerate(data_rows, start=2):  # Start at row 2 (skip header)
            if not row or not row[0]:
                continue
            
            ver_id = row[0]
            if ver_id not in ver_groups:
                ver_groups[ver_id] = []
            
            ver_groups[ver_id].append({
                'row_number': idx,
                'data': row,
                'status': row[5] if len(row) > 5 else '',  # Column F (Trạng Thái)
                'approved_at': row[7] if len(row) > 7 else ''  # Column H (Ngày Duyệt)
            })
        
        # Find duplicates
        duplicates_to_delete = []
        
        for ver_id, rows in ver_groups.items():
            if len(rows) > 1:
                print(f"⚠️ Found {len(rows)} rows for {ver_id}:")
                
                # Sort by: APPROVED first, then by approved_at/created_at (newest first)
                def sort_key(r):
                    priority = 0 if r['status'] == 'APPROVED' else 1 if r['status'] == 'PENDING' else 2
                    timestamp = r['approved_at'] or r['data'][6]  # approved_at or created_at
                    return (priority, timestamp)
                
                rows.sort(key=sort_key)
                
                # Keep first (best), delete the rest
                keep_row = rows[0]
                delete_rows = rows[1:]
                
                for r in rows:
                    status_icon = "🟢" if r['status'] == "APPROVED" else "🟡" if r['status'] == "PENDING" else "🔴"
                    action = "✅ KEEP" if r == keep_row else "❌ DELETE"
                    print(f"   Row {r['row_number']}: {status_icon} {r['status']} - {action}")
                
                duplicates_to_delete.extend([r['row_number'] for r in delete_rows])
                print()
        
        if not duplicates_to_delete:
            print("✅ No duplicates found!")
            return
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total duplicates to delete: {len(duplicates_to_delete)}")
        print(f"   Rows: {sorted(duplicates_to_delete)}")
        print()
        
        # Delete rows (from bottom to top to avoid index shifts)
        duplicates_to_delete.sort(reverse=True)
        
        print("🔄 Deleting duplicate rows...")
        for row_num in duplicates_to_delete:
            worksheet.delete_rows(row_num)
            print(f"   Deleted row {row_num}")
        
        print()
        print("="*70)
        print("✅ CLEANUP COMPLETE!")
        print("="*70)
        print(f"\nDeleted {len(duplicates_to_delete)} duplicate rows")
        print(f"Remaining: {len(data_rows) - len(duplicates_to_delete)} rows\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🤖 Freedom Wallet Bot - Google Sheets Cleanup\n")
    cleanup_duplicate_rows()
