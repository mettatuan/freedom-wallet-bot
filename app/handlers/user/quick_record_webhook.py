"""
Quick Record - Webhook Method (OPTION 2 - RECOMMENDED)
Send transaction data to Google Apps Script webhook
Bot doesn't need WRITE permission - more secure!
"""
from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger
from app.core.subscription import SubscriptionManager, SubscriptionTier
from app.utils.database import get_user_by_id, SessionLocal
from app.services.analytics import Analytics
import re
import aiohttp
from datetime import datetime
from typing import Optional


async def handle_quick_expense_webhook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Parse and send expense to Google Apps Script webhook
    
    Examples:
    - "chi 50k tiá»n Äƒn"
    - "mua sáº¯m 200k"
    - "xÄƒng xe 150000 Ä‘á»• xÄƒng Shell"
    """
    user_id = update.effective_user.id
    user = await get_user_by_id(user_id)
    tier = SubscriptionManager.get_user_tier(user)
    
    # Check Premium
    if tier not in [SubscriptionTier.PREMIUM, SubscriptionTier.TRIAL]:
        await update.message.reply_text(
            "ðŸ”’ **TÃ­nh nÄƒng Premium**\n\n"
            "Quick Record chá»‰ dÃ nh cho Premium/Trial.\n\n"
            "ðŸŽ DÃ¹ng thá»­ 7 ngÃ y FREE: /start"
        )
        return
    
    # Check if webhook configured
    if not user.spreadsheet_id or not user.webhook_url:
        await update.message.reply_text(
            "ðŸ“Š **ChÆ°a cáº¥u hÃ¬nh Quick Record**\n\n"
            "Äá»ƒ ghi chi tiÃªu tá»± Ä‘á»™ng:\n"
            "1. CÃ i Ä‘áº·t Apps Script: /setupwebhook\n"
            "2. Hoáº·c xem hÆ°á»›ng dáº«n: /quickrecord_help\n\n"
            "ðŸ’¡ PhÆ°Æ¡ng phÃ¡p nÃ y Báº¢O Máº¬T hÆ¡n (bot khÃ´ng cáº§n quyá»n Editor)"
        )
        return
    
    # Parse message
    text = update.message.text
    parsed = parse_expense_message(text)
    
    if not parsed:
        await update.message.reply_text(
            "âŒ **KhÃ´ng hiá»ƒu format!**\n\n"
            "Thá»­ láº¡i vá»›i format:\n"
            "â€¢ `chi 50k tiá»n Äƒn`\n"
            "â€¢ `mua sáº¯m 200k`\n"
            "â€¢ `xÄƒng xe 150000 Ä‘á»• táº¡i Shell`\n\n"
            "Hoáº·c dÃ¹ng: /record"
        )
        return
    
    amount = parsed['amount']
    category = parsed['category']
    note = parsed.get('note', '')
    
    # Confirm before sending
    await update.message.reply_text(
        f"ðŸ“ **XÃ¡c nháº­n ghi:**\n\n"
        f"ðŸ’¸ Sá»‘ tiá»n: {amount:,.0f} VNÄ\n"
        f"ðŸ“‚ Danh má»¥c: {category}\n"
        f"ðŸ“Œ Ghi chÃº: {note if note else '(trá»‘ng)'}\n\n"
        f"ðŸ”„ Äang gá»­i tá»›i Google Sheets..."
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
                f"âœ… **ÄÃ£ ghi thÃ nh cÃ´ng!**\n\n"
                f"ðŸ’¸ Chi: {amount:,.0f} VNÄ\n"
                f"ðŸ“‚ {category}\n\n"
                f"ðŸ“Š Xem sá»‘ dÆ°: /balance"
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
                f"âŒ **Lá»—i ghi dá»¯ liá»‡u!**\n\n"
                f"Chi tiáº¿t: {message}\n\n"
                f"Kiá»ƒm tra:\n"
                f"â€¢ Apps Script Ä‘ang hoáº¡t Ä‘á»™ng?\n"
                f"â€¢ Webhook URL cÃ²n Ä‘Ãºng?\n\n"
                f"CÃ i láº¡i: /setupwebhook"
            )
    
    except Exception as e:
        await update.message.reply_text(
            f"âŒ **Lá»—i káº¿t ná»‘i!**\n\n"
            f"Chi tiáº¿t: {str(e)}\n\n"
            f"LiÃªn há»‡ /support"
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
                        logger.info(f"âœ… Webhook success for user {user_id}")
                        return True, result.get('message', 'Success')
                    else:
                        error_msg = result.get('error', 'Unknown error')
                        logger.error(f"âŒ Webhook returned error: {error_msg}")
                        return False, error_msg
                else:
                    error_msg = f"HTTP {response.status}"
                    logger.error(f"âŒ Webhook HTTP error: {error_msg}")
                    return False, error_msg
    
    except aiohttp.ClientTimeout:
        logger.error(f"âŒ Webhook timeout for user {user_id}")
        return False, "Timeout - Apps Script khÃ´ng pháº£n há»“i"
    
    except Exception as e:
        logger.error(f"âŒ Webhook exception: {e}")
        return False, str(e)


async def handle_setup_webhook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Guide user to setup Google Apps Script webhook
    """
    user_id = update.effective_user.id
    user = await get_user_by_id(user_id)
    tier = SubscriptionManager.get_user_tier(user)
    
    if tier not in [SubscriptionTier.PREMIUM, SubscriptionTier.TRIAL]:
        await update.message.reply_text("ðŸ”’ TÃ­nh nÄƒng Premium only")
        return
    
    message = """
ðŸ“± **CÃ€I Äáº¶T QUICK RECORD QUA WEBHOOK**

**BÆ°á»›c 1: Má»Ÿ Google Sheets cá»§a báº¡n**
VÃ o Sheet Freedom Wallet Ä‘Ã£ copy

**BÆ°á»›c 2: VÃ o Extensions â†’ Apps Script**
Click menu Extensions â†’ Apps Script

**BÆ°á»›c 3: Copy code nÃ y vÃ o Apps Script:**
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

**BÆ°á»›c 4: Deploy as Web App**
â€¢ Click Deploy â†’ New deployment
â€¢ Select type: Web app
â€¢ Execute as: Me
â€¢ Who has access: Anyone
â€¢ Click Deploy
â€¢ Copy Web App URL

**BÆ°á»›c 5: Gá»­i URL cho bot**
GÃµ: `/setwebhook [URL]`

VÃ­ dá»¥:
`/setwebhook https://script.google.com/macros/s/ABC123.../exec`

âœ… **Xong! Giá» báº¡n cÃ³ thá»ƒ gÃµ:**
â€¢ "chi 50k tiá»n Äƒn"
â€¢ "mua sáº¯m 200k"

Bot sáº½ gá»­i tá»›i Apps Script â†’ Tá»± Ä‘á»™ng ghi vÃ o Sheets! ðŸŽ‰

ðŸ”’ **Báº£o máº­t:** Bot KHÃ”NG cÃ³ quyá»n ghi, chá»‰ gá»­i request. Apps Script cháº¡y dÆ°á»›i quyá»n Báº N.
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
        await update.message.reply_text("ðŸ”’ Premium only")
        return
    
    # Parse webhook URL
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "âŒ **Thiáº¿u URL!**\n\n"
            "CÃ¡ch dÃ¹ng:\n"
            "`/setwebhook https://script.google.com/macros/s/ABC.../exec`\n\n"
            "Xem hÆ°á»›ng dáº«n: /setupwebhook"
        )
        return
    
    webhook_url = context.args[0]
    
    # Validate URL
    if not webhook_url.startswith('https://script.google.com'):
        await update.message.reply_text(
            "âŒ **URL khÃ´ng há»£p lá»‡!**\n\n"
            "URL pháº£i báº¯t Ä‘áº§u báº±ng:\n"
            "`https://script.google.com/macros/s/...`"
        )
        return
    
    # Test webhook
    await update.message.reply_text("ðŸ”„ Äang test webhook...")
    
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
        db = SessionLocal()
        user = db.merge(user)
        user.webhook_url = webhook_url
        db.commit()
        db.close()
        
        await update.message.reply_text(
            "âœ… **Káº¿t ná»‘i thÃ nh cÃ´ng!**\n\n"
            "Webhook Ä‘Ã£ Ä‘Æ°á»£c lÆ°u.\n\n"
            "Thá»­ ngay:\n"
            "â€¢ `chi 50k tiá»n Äƒn`\n"
            "â€¢ `mua sáº¯m 100k`\n\n"
            "ðŸ“Š Xem sá»‘ dÆ°: /balance"
        )
        
        Analytics.track_event(user_id, 'webhook_connected')
    else:
        await update.message.reply_text(
            f"âŒ **Test tháº¥t báº¡i!**\n\n"
            f"Lá»—i: {message}\n\n"
            f"Kiá»ƒm tra:\n"
            f"â€¢ Deploy as Web App chÆ°a?\n"
            f"â€¢ Execute as: Me\n"
            f"â€¢ Who has access: Anyone\n\n"
            f"Xem hÆ°á»›ng dáº«n: /setupwebhook"
        )


def parse_expense_message(text: str) -> Optional[dict]:
    """
    Parse natural language expense message
    
    Examples:
    - "chi 50k tiá»n Äƒn" â†’ {amount: 50000, category: "tiá»n Äƒn"}
    - "mua sáº¯m 200k quáº§n Ã¡o" â†’ {amount: 200000, category: "mua sáº¯m", note: "quáº§n Ã¡o"}
    - "150000 xÄƒng xe" â†’ {amount: 150000, category: "xÄƒng xe"}
    
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
    prefixes = ['chi', 'mua', 'tráº£', 'thanh toÃ¡n']
    for prefix in prefixes:
        if remaining.startswith(prefix):
            remaining = remaining[len(prefix):].strip()
            break
    
    # Split into category and note
    parts = remaining.split(maxsplit=2)
    
    if not parts:
        category = "KhÃ¡c"
        note = ""
    elif len(parts) == 1:
        category = parts[0]
        note = ""
    else:
        category = parts[0]
        note = ' '.join(parts[1:])
    
    # Map common categories
    category_map = {
        'Äƒn': 'Ä‚n uá»‘ng',
        'uá»‘ng': 'Ä‚n uá»‘ng',
        'cÆ¡m': 'Ä‚n uá»‘ng',
        'cafe': 'Cafe',
        'cÃ  phÃª': 'Cafe',
        'xÄƒng': 'XÄƒng xe',
        'xe': 'XÄƒng xe',
        'Ä‘iá»‡n': 'HÃ³a Ä‘Æ¡n',
        'nÆ°á»›c': 'HÃ³a Ä‘Æ¡n',
        'internet': 'HÃ³a Ä‘Æ¡n',
        'mua': 'Mua sáº¯m',
        'sáº¯m': 'Mua sáº¯m',
        'quáº§n': 'Quáº§n Ã¡o',
        'Ã¡o': 'Quáº§n Ã¡o',
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
    expense_pattern = r'(?i)(?:chi|mua|tráº£|thanh toÃ¡n)?\s*\d+(?:[,\.]\d+)?\s*k?\s*.+'
    
    application.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(expense_pattern),
        handle_quick_expense_webhook
    ))
    
    logger.info("âœ… Quick Record (webhook) handlers registered")

