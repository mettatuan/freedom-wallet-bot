"""
Quick Record - Direct Write (OPTION 1)
Parse natural language and write to Google Sheets
Requires EDITOR permission
"""
from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger
from bot.services.sheets_api_client import SheetsAPIClient
from bot.core.subscription import SubscriptionManager, SubscriptionTier
from bot.utils.database import get_user_by_id
from bot.services.analytics import Analytics
import re


async def handle_quick_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Parse and record expense from natural language
    
    Examples:
    - "chi 50k tiền ăn"
    - "mua sắm 200k"
    - "xăng xe 150000 đổ xăng Shell"
    """
    user_id = update.effective_user.id
    user = await get_user_by_id(user_id)
    tier = SubscriptionManager.get_user_tier(user)
    
    # Check Premium
    if tier not in [SubscriptionTier.PREMIUM, SubscriptionTier.TRIAL]:
        await update.message.reply_text(
            "🔒 **Tính năng Premium**\n\n"
            "Quick Record chỉ dành cho Premium/Trial.\n\n"
            "🎁 Dùng thử 7 ngày FREE: /start"
        )
        return
    
    # Check if Sheets connected
    if not user.spreadsheet_id:
        await update.message.reply_text(
            "📊 **Chưa kết nối Google Sheets**\n\n"
            "Để ghi chi tiêu tự động, hãy:\n"
            "1. Kết nối Sheets: /connectsheets\n"
            "2. Share quyền **Editor** (thay vì Viewer)\n\n"
            "⚠️ Lưu ý: Bot cần Editor để ghi được data!"
        )
        return
    
    client = SheetsAPIClient(user.spreadsheet_id, user.web_app_url)
    
    # Parse message
    text = update.message.text
    parsed = parse_expense_message(text)
    
    if not parsed:
        await update.message.reply_text(
            "❌ **Không hiểu format!**\n\n"
            "Thử lại với format:\n"
            "• `chi 50k tiền ăn`\n"
            "• `mua sắm 200k`\n"
            "• `xăng xe 150000 đổ tại Shell`\n\n"
            "Hoặc dùng: /record"
        )
        return
    
    amount = parsed['amount']
    category = parsed['category']
    note = parsed.get('note', '')
    
    # Confirm before writing
    await update.message.reply_text(
        f"📝 **Xác nhận ghi:**\n\n"
        f"💸 Số tiền: {amount:,.0f} VNĐ\n"
        f"📂 Danh mục: {category}\n"
        f"📌 Ghi chú: {note if note else '(trống)'}\n\n"
        f"🔄 Đang ghi vào Google Sheets..."
    )
    
    # Write to Sheets
    try:
        result = await client.add_transaction(
            amount=amount,
            category=category,
            note=note,
            transaction_type="Chi"
        )
        
        if result.get('success'):
            await update.message.reply_text(
                f"✅ **Đã ghi thành công!**\n\n"
                f"💸 Chi: {amount:,.0f} VNĐ\n"
                f"📂 {category}\n\n"
                f"📊 Xem số dư: /balance"
            )
            
            # Track usage
            Analytics.track_event(user_id, 'quick_record_success', {
                'amount': amount,
                'category': category,
                'method': 'direct_write'
            })
            
            logger.info(f"User {user_id} recorded expense: {amount} - {category}")
        else:
            await update.message.reply_text(
                "❌ **Lỗi ghi dữ liệu!**\n\n"
                "Kiểm tra:\n"
                "• Đã share quyền Editor chưa?\n"
                "• Google Sheets có cột đúng format chưa?\n\n"
                "Liên hệ /support nếu vẫn lỗi"
            )
    
    except Exception as e:
        await update.message.reply_text(
            f"❌ **Lỗi ghi!**\n\n"
            f"Chi tiết: {str(e)}\n\n"
            f"Liên hệ /support"
        )
        logger.error(f"Quick record error for user {user_id}: {e}")


def parse_expense_message(text: str) -> dict:
    """
    Parse natural language expense message
    
    Examples:
    - "chi 50k tiền ăn" → {amount: 50000, category: "tiền ăn"}
    - "mua sắm 200k quần áo" → {amount: 200000, category: "mua sắm", note: "quần áo"}
    - "150000 xăng xe" → {amount: 150000, category: "xăng xe"}
    
    Returns:
        dict with amount, category, note or None if parse failed
    """
    text = text.lower().strip()
    
    # Pattern 1: "chi 50k tiền ăn"
    # Pattern 2: "mua sắm 200k"
    # Pattern 3: "150000 xăng xe"
    
    # Extract amount (with k/K multiplier)
    amount_pattern = r'(\d+(?:[,\.]\d+)?)\s*k?'
    amount_match = re.search(amount_pattern, text)
    
    if not amount_match:
        return None
    
    amount_str = amount_match.group(1).replace(',', '.')
    amount = float(amount_str)
    
    # Check if has 'k' suffix
    if 'k' in text[amount_match.start():amount_match.end()].lower():
        amount *= 1000
    
    # Extract category and note
    # Remove amount part from text
    remaining = text[:amount_match.start()] + text[amount_match.end():]
    remaining = remaining.strip()
    
    # Remove common prefixes
    prefixes = ['chi', 'mua', 'trả', 'thanh toán']
    for prefix in prefixes:
        if remaining.startswith(prefix):
            remaining = remaining[len(prefix):].strip()
            break
    
    # Split into category and note
    parts = remaining.split(maxsplit=2)
    
    if not parts:
        category = "Khác"
        note = ""
    elif len(parts) == 1:
        category = parts[0]
        note = ""
    else:
        category = parts[0]
        note = ' '.join(parts[1:])
    
    # Map common categories
    category_map = {
        'ăn': 'Ăn uống',
        'uống': 'Ăn uống',
        'cơm': 'Ăn uống',
        'cafe': 'Cafe',
        'cà phê': 'Cafe',
        'xăng': 'Xăng xe',
        'xe': 'Xăng xe',
        'điện': 'Hóa đơn',
        'nước': 'Hóa đơn',
        'internet': 'Hóa đơn',
        'mua': 'Mua sắm',
        'sắm': 'Mua sắm',
        'quần': 'Quần áo',
        'áo': 'Quần áo',
    }
    
    for key, value in category_map.items():
        if key in category.lower():
            category = value
            break
    
    return {
        'amount': amount,
        'category': category.capitalize(),
        'note': note
    }


# Register handler
def register_quick_record_direct_handler(application):
    """Register Quick Record handler (direct write)"""
    from telegram.ext import MessageHandler, filters
    
    # Match messages like "chi 50k tiền ăn"
    expense_pattern = r'(?:chi|mua|trả|thanh toán)?\s*\d+(?:[,\.]\d+)?\s*k?\s*.+'
    
    application.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(expense_pattern, re.IGNORECASE),
        handle_quick_expense
    ))
    
    logger.info("✅ Quick Record (direct write) handler registered")
