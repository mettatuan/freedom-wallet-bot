"""
Quick Record - Webhook Method (OPTION 2 - RECOMMENDED)
Send transaction data to Google Apps Script webhook
Bot doesn't need WRITE permission - more secure!
"""
from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger
from bot.core.subscription import SubscriptionManager, SubscriptionTier
from bot.utils.database import get_user_by_id, SessionLocal, User, run_sync
from bot.services.analytics import Analytics
import re
import aiohttp
from datetime import datetime
from typing import Optional


def _save_webhook_url_sync(user_id: int, webhook_url: str) -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.webhook_url = webhook_url
            db.commit()
    finally:
        db.close()


async def handle_quick_expense_webhook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Parse and send expense to Google Apps Script webhook
    
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
    
    # Check if webhook configured
    if not user.spreadsheet_id or not user.webhook_url:
        await update.message.reply_text(
            "📊 **Chưa cấu hình Quick Record**\n\n"
            "Để ghi chi tiêu tự động:\n"
            "1. Cài đặt Apps Script: /setupwebhook\n"
            "2. Hoặc xem hướng dẫn: /quickrecord_help\n\n"
            "💡 Phương pháp này BẢO MẬT hơn (bot không cần quyền Editor)"
        )
        return
    
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
    
    # Confirm before sending
    await update.message.reply_text(
        f"📝 **Xác nhận ghi:**\n\n"
        f"💸 Số tiền: {amount:,.0f} VNĐ\n"
        f"📂 Danh mục: {category}\n"
        f"📌 Ghi chú: {note if note else '(trống)'}\n\n"
        f"🔄 Đang gửi tới Google Sheets..."
    )
    
    # Send to webhook
    try:
        success, message = await send_transaction_to_webhook(
            webhook_url=user.webhook_url,
            transaction_type='expense',
            amount=amount,
            category=category,
            note=note,
            user_id=user_id
        )
        
        if success:
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
                'method': 'webhook'
            })
            
            logger.info(f"User {user_id} recorded expense via webhook: {amount} - {category}")
        else:
            await update.message.reply_text(
                f"❌ **Lỗi ghi dữ liệu!**\n\n"
                f"Chi tiết: {message}\n\n"
                f"Kiểm tra:\n"
                f"• Apps Script đang hoạt động?\n"
                f"• Webhook URL còn đúng?\n\n"
                f"Cài lại: /setupwebhook"
            )
    
    except Exception as e:
        await update.message.reply_text(
            f"❌ **Lỗi kết nối!**\n\n"
            f"Chi tiết: {str(e)}\n\n"
            f"Liên hệ /support"
        )
        logger.error(f"Webhook error for user {user_id}: {e}")


async def send_transaction_to_webhook(
    webhook_url: str,
    transaction_type: str,
    amount: float,
    category: str,
    note: str = "",
    user_id: int = 0
) -> tuple[bool, str]:
    """
    Send transaction data to Google Apps Script webhook
    
    Args:
        webhook_url: Apps Script Web App URL
        transaction_type: 'expense' or 'income'
        amount: Transaction amount
        category: Category
        note: Optional note
        user_id: Telegram user ID for logging
    
    Returns:
        (success: bool, message: str)
    """
    # Prepare payload
    payload = {
        'type': transaction_type,
        'date': datetime.now().strftime('%d/%m/%Y'),
        'time': datetime.now().strftime('%H:%M:%S'),
        'category': category,
        'amount': -abs(amount) if transaction_type == 'expense' else abs(amount),
        'jar': 'Necessities' if transaction_type == 'expense' else 'Income',
        'note': note,
        'method': 'Telegram Bot',
        'user_id': user_id
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                webhook_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    
                    if result.get('success'):
                        logger.info(f"✅ Webhook success for user {user_id}")
                        return True, result.get('message', 'Success')
                    else:
                        error_msg = result.get('error', 'Unknown error')
                        logger.error(f"❌ Webhook returned error: {error_msg}")
                        return False, error_msg
                else:
                    error_msg = f"HTTP {response.status}"
                    logger.error(f"❌ Webhook HTTP error: {error_msg}")
                    return False, error_msg
    
    except aiohttp.ClientTimeout:
        logger.error(f"❌ Webhook timeout for user {user_id}")
        return False, "Timeout - Apps Script không phản hồi"
    
    except Exception as e:
        logger.error(f"❌ Webhook exception: {e}")
        return False, str(e)


async def handle_setup_webhook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Guide user to setup Google Apps Script webhook
    """
    user_id = update.effective_user.id
    user = await get_user_by_id(user_id)
    tier = SubscriptionManager.get_user_tier(user)
    
    if tier not in [SubscriptionTier.PREMIUM, SubscriptionTier.TRIAL]:
        await update.message.reply_text("🔒 Tính năng Premium only")
        return
    
    message = """
📱 **CÀI ĐẶT QUICK RECORD QUA WEBHOOK**

**Bước 1: Mở Google Sheets của bạn**
Vào Sheet Freedom Wallet đã copy

**Bước 2: Vào Extensions → Apps Script**
Click menu Extensions → Apps Script

**Bước 3: Copy code này vào Apps Script:**
```javascript
function doPost(e) {
  try {
    // Parse request
    var data = JSON.parse(e.postData.contents);
    
    // Get Transactions sheet
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName('Transactions');
    
    if (!sheet) {
      return ContentService.createTextOutput(
        JSON.stringify({success: false, error: 'Sheet not found'})
      ).setMimeType(ContentService.MimeType.JSON);
    }
    
    // Append row: Date | Category | Amount | Jar | Note | Method
    sheet.appendRow([
      data.date,
      data.category,
      data.amount,
      data.jar,
      data.note,
      data.method
    ]);
    
    return ContentService.createTextOutput(
      JSON.stringify({
        success: true,
        message: 'Transaction recorded'
      })
    ).setMimeType(ContentService.MimeType.JSON);
    
  } catch (error) {
    return ContentService.createTextOutput(
      JSON.stringify({
        success: false,
        error: error.toString()
      })
    ).setMimeType(ContentService.MimeType.JSON);
  }
}
```

**Bước 4: Deploy as Web App**
• Click Deploy → New deployment
• Select type: Web app
• Execute as: Me
• Who has access: Anyone
• Click Deploy
• Copy Web App URL

**Bước 5: Gửi URL cho bot**
Gõ: `/setwebhook [URL]`

Ví dụ:
`/setwebhook https://script.google.com/macros/s/ABC123.../exec`

✅ **Xong! Giờ bạn có thể gõ:**
• "chi 50k tiền ăn"
• "mua sắm 200k"

Bot sẽ gửi tới Apps Script → Tự động ghi vào Sheets! 🎉

🔒 **Bảo mật:** Bot KHÔNG có quyền ghi, chỉ gửi request. Apps Script chạy dưới quyền BẠN.
"""
    
    await update.message.reply_text(message, parse_mode='Markdown')
    
    Analytics.track_event(user_id, 'webhook_setup_guide_viewed')


async def handle_set_webhook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Save webhook URL for user
    
    Usage: /setwebhook https://script.google.com/macros/s/ABC123.../exec
    """
    user_id = update.effective_user.id
    user = await get_user_by_id(user_id)
    tier = SubscriptionManager.get_user_tier(user)
    
    if tier not in [SubscriptionTier.PREMIUM, SubscriptionTier.TRIAL]:
        await update.message.reply_text("🔒 Premium only")
        return
    
    # Parse webhook URL
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "❌ **Thiếu URL!**\n\n"
            "Cách dùng:\n"
            "`/setwebhook https://script.google.com/macros/s/ABC.../exec`\n\n"
            "Xem hướng dẫn: /setupwebhook"
        )
        return
    
    webhook_url = context.args[0]
    
    # Validate URL
    if not webhook_url.startswith('https://script.google.com'):
        await update.message.reply_text(
            "❌ **URL không hợp lệ!**\n\n"
            "URL phải bắt đầu bằng:\n"
            "`https://script.google.com/macros/s/...`"
        )
        return
    
    # Test webhook
    await update.message.reply_text("🔄 Đang test webhook...")
    
    success, message = await send_transaction_to_webhook(
        webhook_url=webhook_url,
        transaction_type='expense',
        amount=0,
        category='TEST',
        note='Bot connection test',
        user_id=user_id
    )
    
    if success:
        # Save to database
        await run_sync(_save_webhook_url_sync, user_id, webhook_url)
        
        await update.message.reply_text(
            "✅ **Kết nối thành công!**\n\n"
            "Webhook đã được lưu.\n\n"
            "Thử ngay:\n"
            "• `chi 50k tiền ăn`\n"
            "• `mua sắm 100k`\n\n"
            "📊 Xem số dư: /balance"
        )
        
        Analytics.track_event(user_id, 'webhook_connected')
    else:
        await update.message.reply_text(
            f"❌ **Test thất bại!**\n\n"
            f"Lỗi: {message}\n\n"
            f"Kiểm tra:\n"
            f"• Deploy as Web App chưa?\n"
            f"• Execute as: Me\n"
            f"• Who has access: Anyone\n\n"
            f"Xem hướng dẫn: /setupwebhook"
        )


def parse_expense_message(text: str) -> Optional[dict]:
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


# Register handlers
def register_quick_record_webhook_handlers(application):
    """Register Quick Record webhook handlers"""
    from telegram.ext import CommandHandler, MessageHandler, filters
    
    application.add_handler(CommandHandler("setupwebhook", handle_setup_webhook))
    application.add_handler(CommandHandler("setwebhook", handle_set_webhook))
    
    # Match expense messages (case-insensitive via (?i) flag)
    expense_pattern = r'(?i)(?:chi|mua|trả|thanh toán)?\s*\d+(?:[,\.]\d+)?\s*k?\s*.+'
    
    application.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(expense_pattern),
        handle_quick_expense_webhook
    ))
    
    logger.info("✅ Quick Record (webhook) handlers registered")
