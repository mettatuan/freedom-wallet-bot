"""
Quick Record Handler (Option 3 - Template Integration)
Parse "chi 50k tiền ăn" và gọi API để ghi vào Google Sheets
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, ApplicationHandlerStop, CallbackQueryHandler
from app.utils.database import get_db, User
from app.services.sheets_api_client import SheetsAPIClient
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Transaction type keywords
# Grammar keywords - Always remove (they're just markers)
GRAMMAR_EXPENSE_KEYWORDS = ['chi', 'trả', 'tiêu', 'tốn', 'đóng', 'nạp']
GRAMMAR_INCOME_KEYWORDS = ['thu', 'nhận', 'được']

# Semantic keywords - Keep as part of note (they're the category itself)  
SEMANTIC_EXPENSE_KEYWORDS = ['mua']  # Keep if part of phrase like "mua sắm"
SEMANTIC_INCOME_KEYWORDS = ['lương', 'thưởng', 'bán']
SEMANTIC_INVESTMENT_KEYWORDS = ['đầu tư']  # Investment transactions

# Combined for detection
EXPENSE_KEYWORDS = GRAMMAR_EXPENSE_KEYWORDS + SEMANTIC_EXPENSE_KEYWORDS
INCOME_KEYWORDS = GRAMMAR_INCOME_KEYWORDS + SEMANTIC_INCOME_KEYWORDS
INVESTMENT_KEYWORDS = SEMANTIC_INVESTMENT_KEYWORDS

# Amount pattern - Prioritize longer units first (triệu before tr)
AMOUNT_PATTERN = r'(\d+(?:[,.\d]*)?)\s*(triệu|nghìn|nghin|tr|k)?'


def parse_amount(amount_str: str) -> float:
    """
    Parse amount string to float
    
    Examples:
        "50" -> 50000
        "50k" -> 50000
        "50 nghìn" -> 50000
        "1.5tr" -> 1500000
        "1,5 triệu" -> 1500000
        "1,500,000" -> 1500000
    """
    # Remove spaces
    amount_str = amount_str.replace(' ', '').lower()
    
    # Determine multiplier - Longest matches first!
    multiplier = 1
    if 'triệu' in amount_str or 'trieu' in amount_str:
        multiplier = 1000000
        amount_str = re.sub(r'(triệu|trieu)', '', amount_str)
    elif 'nghìn' in amount_str or 'nghin' in amount_str:
        multiplier = 1000
        amount_str = re.sub(r'(nghìn|nghin)', '', amount_str)
    elif 'tr' in amount_str:
        multiplier = 1000000
        amount_str = amount_str.replace('tr', '')
    elif 'k' in amount_str:
        multiplier = 1000
        amount_str = amount_str.replace('k', '')
    
    # Replace comma with dot for Vietnamese number format (1,5 = 1.5)
    # But also handle 1,500,000 format
    if ',' in amount_str:
        # If multiple commas or comma followed by 3 digits, it's a separator
        if amount_str.count(',') > 1 or re.search(r',\d{3}', amount_str):
            amount_str = amount_str.replace(',', '')  # Remove thousand separators
        else:
            amount_str = amount_str.replace(',', '.')  # Vietnamese decimal: 1,5 -> 1.5
    
    try:
        amount = float(amount_str) * multiplier
        return amount
    except ValueError:
        return 0


def match_category_smart(note: str, transaction_type: str, categories: list) -> dict:
    """
    Smart category matching
    
    Args:
        note: Transaction note
        transaction_type: "Chi" or "Thu"
        categories: List of category dicts from API
    
    Returns:
        Matched category dict or None
    """
    note_lower = note.lower().strip()
    
    # Filter by transaction type
    filtered = [c for c in categories if c.get('type') == transaction_type]
    
    # Try exact match first
    for cat in filtered:
        if cat['name'].lower() == note_lower:
            return cat
    
    # Try partial match (note contains category name or vice versa)
    for cat in filtered:
        cat_name_lower = cat['name'].lower()
        if note_lower in cat_name_lower or cat_name_lower in note_lower:
            return cat
    
    # Keyword matching for common phrases
    keywords = {
        # Income keywords (Thu)
        'lương': 'Lương',
        'luong': 'Lương',
        'salary': 'Lương',
        'thưởng': 'Lương',
        'thuong': 'Lương',
        'bonus': 'Lương',
        'kinh doanh': 'Kinh doanh',
        'bán hàng': 'Bán hàng',
        'ban hang': 'Bán hàng',
        'cho thuê': 'Cho thuê',
        'cho thue': 'Cho thuê',
        'rent': 'Cho thuê',
        'lãi': 'Lãi đầu tư',
        'lai': 'Lãi đầu tư',
        'cổ tức': 'Lãi đầu tư',
        'co tuc': 'Lãi đầu tư',
        'dividend': 'Lãi đầu tư',
        
        # Investment products
        'sp500': 'Chứng khoán',
        's&p500': 'Chứng khoán',
        's&p': 'Chứng khoán',
        'vn30': 'Chứng khoán',
        'vnindex': 'Chứng khoán',
        'nasdaq': 'Chứng khoán',
        'dow jones': 'Chứng khoán',
        'vti': 'Quỹ đầu tư',
        'voo': 'Quỹ đầu tư',
        'etf': 'Quỹ ETF',
        'quỹ': 'Quỹ đầu tư',
        'quy': 'Quỹ đầu tư',
        'btc': 'Crypto',
        'bitcoin': 'Crypto',
        'eth': 'Crypto',
        'ethereum': 'Crypto',
        'usdt': 'Crypto',
        'crypto': 'Crypto',
        'coin': 'Crypto',
        'tiền điện tử': 'Crypto',
        'tien dien tu': 'Crypto',
        'cổ phiếu': 'Cổ phiếu',
        'co phieu': 'Cổ phiếu',
        'cp': 'Cổ phiếu',
        'chứng khoán': 'Chứng khoán',
        'chung khoan': 'Chứng khoán',
        'ck': 'Chứng khoán',
        'vàng': 'Vàng đầu tư',
        'vang': 'Vàng đầu tư',
        'gold': 'Vàng đầu tư',
        
        # Expense keywords
        'ăn': 'Ăn uống',
        'an': 'Ăn uống',
        'cơm': 'Ăn uống',
        'com': 'Ăn uống',
        'cà phê': 'Ăn uống',
        'ca phe': 'Ăn uống',
        'cafe': 'Ăn uống',
        'trà': 'Ăn uống',
        'tra': 'Ăn uống',
        'nhà hàng': 'Ăn uống',
        'nha hang': 'Ăn uống',
        'mua': 'Mua sắm',
        'áo': 'Mua sắm',
        'ao': 'Mua sắm',
        'quần': 'Mua sắm',
        'quan': 'Mua sắm',
        'giày': 'Mua sắm',
        'giay': 'Mua sắm',
        'phim': 'Giải trí',
        'game': 'Giải trí',
        'du lịch': 'Giải trí',
        'du lich': 'Giải trí',
        'travel': 'Giải trí',
        'bệnh': 'Y tế',
        'benh': 'Y tế',
        'thuốc': 'Y tế',
        'thuoc': 'Y tế',
        'khám': 'Y tế',
        'kham': 'Y tế',
        'học': 'Giáo dục',
        'hoc': 'Giáo dục',
        'sách': 'Giáo dục',
        'sach': 'Giáo dục',
        'khoá học': 'Giáo dục',
        'khoa hoc': 'Giáo dục',
        'course': 'Giáo dục',
        'điện': 'Điện nước',
        'dien': 'Điện nước',
        'nước': 'Điện nước',
        'nuoc': 'Điện nước',
        'internet': 'Điện nước',
        'xăng': 'Xăng xe',
        'xang': 'Xăng xe',
        'gas': 'Xăng xe',
        'xe': 'Xăng xe',
        'quà': 'Quà tặng',
        'qua': 'Quà tặng',
        'gift': 'Quà tặng',
    }
    
    for keyword, cat_name in keywords.items():
        if keyword in note_lower:
            for cat in filtered:
                if cat['name'] == cat_name:
                    return cat
    
    return None


def get_popular_categories() -> list:
    """Get popular fallback categories when API fails"""
    return [
        # Income
        {'id': 'CAT031', 'name': 'Lương', 'type': 'Thu', 'icon': '💼', 'jarId': '', 'autoAllocate': True},
        {'id': 'CAT032', 'name': 'Kinh doanh', 'type': 'Thu', 'icon': '💼', 'jarId': '', 'autoAllocate': True},
        {'id': 'CAT033', 'name': 'Cho thuê', 'type': 'Thu', 'icon': '🏠', 'jarId': 'FFA', 'autoAllocate': False},
        {'id': 'CAT034', 'name': 'Lãi đầu tư', 'type': 'Thu', 'icon': '📈', 'jarId': 'FFA', 'autoAllocate': False},
        {'id': 'CAT037', 'name': 'Bán hàng', 'type': 'Thu', 'icon': '💰', 'jarId': '', 'autoAllocate': True},
        
        # Expense
        {'id': 'CAT021', 'name': 'Ăn uống', 'type': 'Chi', 'icon': '🍽️', 'jarId': 'NEC', 'autoAllocate': False},
        {'id': 'CAT022', 'name': 'Mua sắm', 'type': 'Chi', 'icon': '🛒', 'jarId': 'NEC', 'autoAllocate': False},
        {'id': 'CAT023', 'name': 'Giải trí', 'type': 'Chi', 'icon': '🎬', 'jarId': 'PLAY', 'autoAllocate': False},
        {'id': 'CAT024', 'name': 'Y tế', 'type': 'Chi', 'icon': '🏥', 'jarId': 'NEC', 'autoAllocate': False},
        {'id': 'CAT025', 'name': 'Giáo dục', 'type': 'Chi', 'icon': '📚', 'jarId': 'EDU', 'autoAllocate': False},
        {'id': 'CAT026', 'name': 'Điện nước', 'type': 'Chi', 'icon': '💡', 'jarId': 'NEC', 'autoAllocate': False},
        {'id': 'CAT027', 'name': 'Xăng xe', 'type': 'Chi', 'icon': '⛽', 'jarId': 'NEC', 'autoAllocate': False},
        {'id': 'CAT029', 'name': 'Quà tặng', 'type': 'Chi', 'icon': '🎁', 'jarId': 'GIVE', 'autoAllocate': False},
    ]


def get_jar_name(jar_id: str) -> str:
    """Get jar display name from ID"""
    jar_names = {
        'NEC': '🏠 Nhu cầu thiết yếu',
        'LTSS': '💎 Tiết kiệm dài hạn',
        'EDU': '🎓 Học tập & Phát triển',
        'PLAY': '🎉 Giải trí & Tận hưởng',
        'FFA': '📈 Đầu tư & Tự do tài chính',
        'GIVE': '❤️ Cho đi & Cộng đồng',
        'AUTO_6JARS': '🏺 Tự động phân bổ 6 hũ',
        'NO_JAR': '❌ Không phân bổ'
    }
    return jar_names.get(jar_id, jar_id)


def parse_quick_record_message(text: str) -> tuple[str, float, str]:
    """
    Smart parsing for natural language transaction messages
    
    Args:
        text: User message
    
    Returns:
        (type, amount, note)
        - type: "Chi" or "Thu"
        - amount: Transaction amount
        - note: Transaction note/category
    
    Examples:
        "chi 150k xem phim" -> ("Chi", 150000, "xem phim")
        "chi xem phim 150k" -> ("Chi", 150000, "xem phim")
        "xem phim 150k" -> ("Chi", 150000, "xem phim")
        "150k xem phim" -> ("Chi", 150000, "xem phim")
        "thu lương 5tr" -> ("Thu", 5000000, "lương")
        "nhận 500k thưởng" -> ("Thu", 500000, "thưởng")
        "lương 5 triệu" -> ("Thu", 5000000, "lương")
    """
    text = text.strip()
    text_lower = text.lower()
    
    # Step 1: Detect transaction type from keywords
    transaction_type = None
    type_keyword = None
    
    # Check for investment keywords first (highest priority)
    for keyword in INVESTMENT_KEYWORDS:
        if keyword in text_lower:
            transaction_type = "Đầu tư"
            type_keyword = keyword
            break
    
    # Check for expense keywords
    if not transaction_type:
        for keyword in EXPENSE_KEYWORDS:
            if keyword in text_lower:
                transaction_type = "Chi"
                type_keyword = keyword
                break
    
    # Check for income keywords
    if not transaction_type:
        for keyword in INCOME_KEYWORDS:
            if keyword in text_lower:
                transaction_type = "Thu"
                type_keyword = keyword
                break
    
    # Step 2: Extract amount using regex - find ALL matches and pick the best one
    amount = 0
    amount_match = None
    
    # Find all potential amount matches
    all_matches = list(re.finditer(AMOUNT_PATTERN, text, re.IGNORECASE))
    
    if all_matches:
        # Filter out matches that have letters immediately before (like SP500, CAT001)
        valid_matches = []
        for match in all_matches:
            start_pos = match.start()
            # Check if there's a letter immediately before the number
            if start_pos > 0 and text[start_pos - 1].isalpha():
                continue  # Skip this match (it's part of a word/code)
            valid_matches.append(match)
        
        if valid_matches:
            # Prioritize matches with units (triệu, tr, k) over raw numbers
            matches_with_units = [m for m in valid_matches if m.group(2)]
            if matches_with_units:
                # Use the first match with unit
                amount_match = matches_with_units[0]
            else:
                # Use the first valid match without unit
                amount_match = valid_matches[0]
            
            if amount_match:
                amount_str = amount_match.group(1)  # Number part
                unit_str = amount_match.group(2) or ''  # Unit part (k, tr, triệu, nghìn)
                
                # Combine for parsing
                full_amount_str = amount_str + unit_str
                amount = parse_amount(full_amount_str)
    
    if amount <= 0:
        return None, 0, ""  # No valid amount found
    
    # Step 3: Extract note (everything except type keyword and amount)
    # Collect all parts to remove with their positions
    parts_to_remove = []
    
    # Smart keyword removal based on keyword type
    if type_keyword:
        keyword_match = re.search(rf'\b{type_keyword}\b', text, re.IGNORECASE)
        if keyword_match:
            should_remove = False
            
            # Always remove grammar keywords (chi, thu, nhận, trả, etc.)
            if type_keyword in GRAMMAR_EXPENSE_KEYWORDS or type_keyword in GRAMMAR_INCOME_KEYWORDS:
                should_remove = True
            
            # Investment keywords (đầu tư) - Never remove, they ARE the category
            elif type_keyword in SEMANTIC_INVESTMENT_KEYWORDS:
                should_remove = False
            
            # For semantic keywords, only remove in specific cases
            elif type_keyword in SEMANTIC_EXPENSE_KEYWORDS:  # "mua"
                # Remove "mua" only if it's immediately before amount
                # e.g., "mua 50k" → remove "mua"
                # but "mua sắm 50k" → keep "mua" as part of "mua sắm"
                if amount_match:
                    text_between = text[keyword_match.end():amount_match.start()].strip()
                    if len(text_between) == 0:  # Nothing between "mua" and amount
                        should_remove = True
            
            # Semantic income keywords (lương, thưởng, bán) - Never remove
            # They ARE the category/note itself
            
            if should_remove:
                parts_to_remove.append((keyword_match.start(), keyword_match.end()))
    
    # Add amount position
    if amount_match:
        parts_to_remove.append((amount_match.start(), amount_match.end()))
    
    # Sort by position (reverse so we remove from end to start)
    parts_to_remove.sort(reverse=True)
    
    # Remove all parts
    note = text
    for start, end in parts_to_remove:
        note = note[:start] + note[end:]
    
    # Clean up note
    note = note.strip()
    note = re.sub(r'\s+', ' ', note)  # Collapse multiple spaces
    
    if not note:
        note = "Giao dịch"  # Default note if empty
    
    # Step 4: Default to "Chi" if no type keyword found but has amount
    if not transaction_type:
        # Check if note contains income-related words for smart defaulting
        income_hints = ['lương', 'thưởng', 'bán', 'nhận', 'thu nhập', 'tiền về']
        if any(hint in text_lower for hint in income_hints):
            transaction_type = "Thu"
        else:
            # Default to expense (most common case)
            transaction_type = "Chi"
    
    return transaction_type, amount, note


async def handle_quick_record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for quick record messages like "chi 50k tiền ăn"
    """
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # CRITICAL: Skip if user is in connection flow
    if context.user_data.get('waiting_for_sheet_url') or context.user_data.get('waiting_for_webapp_url'):
        return  # Let message handler process it
    
    # Parse message
    transaction_type, amount, note = parse_quick_record_message(message_text)
    
    if not transaction_type or amount <= 0:
        # Not a valid quick record message, ignore
        return
    
    # Check if user has connected Sheets
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.spreadsheet_id:
        # User not connected
        await update.message.reply_text(
            "⚠️ Bạn chưa kết nối Google Sheets!\n\n"
            "Dùng /connectsheets để kết nối trước nhé. 😊"
        )
        return
    
    # Get categories from API for smart matching
    try:
        client = SheetsAPIClient(user.spreadsheet_id, user.web_app_url)
        categories_result = await client.get_categories()
        
        if not categories_result.get("success"):
            logger.warning(f"Failed to get categories: {categories_result.get('error')}")
            categories = []
        else:
            categories = categories_result.get("categories", [])
            logger.info(f"✅ Loaded {len(categories)} categories for user {user.id}")
            if categories:
                logger.debug(f"Categories preview: {[c.get('name') for c in categories[:5]]}")
    except Exception as e:
        logger.error(f"❌ Error getting categories: {e}")
        categories = []
    
    # Fallback: Use popular categories if API fails
    if not categories:
        logger.warning(f"⚠️ No categories from API. Using popular fallback for user {user.id}")
        categories = get_popular_categories()
    
    # Try smart matching
    matched_category = match_category_smart(note, transaction_type, categories) if categories else None
    
    if matched_category:
        # Found a match! Show confirmation
        suggested_jar = matched_category.get('jarId', 'NEC')
        suggested_account = 'Cash'  # Default
        
        # Save transaction data to context
        context.user_data['pending_transaction'] = {
            'type': transaction_type,
            'amount': amount,
            'note': note,
            'category': matched_category['name'],
            'category_id': matched_category.get('id'),
            'category_icon': matched_category.get('icon', '📝'),
            'jar': suggested_jar,
            'account': suggested_account,
            'timestamp': datetime.now().isoformat()
        }
        
        # Show confirmation with edit options
        keyboard = [
            [InlineKeyboardButton("✅ Xác nhận và ghi", callback_data="qr_confirm")],
            [
                InlineKeyboardButton("✏️ Sửa danh mục", callback_data="qr_edit_category"),
                InlineKeyboardButton("✏️ Sửa hũ", callback_data="qr_edit_jar"),
            ],
            [
                InlineKeyboardButton("💳 Đổi tài khoản", callback_data="qr_edit_account"),
                InlineKeyboardButton("❌ Hủy", callback_data="qr_cancel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"📝 **Phân loại tự động**\n\n"
            f"• {transaction_type}: **{amount:,.0f} ₫**\n"
            f"• Danh mục: {matched_category.get('icon', '📝')} **{matched_category['name']}**\n"
            f"• Hũ: **{suggested_jar}** - {get_jar_name(suggested_jar)}\n"
            f"• Tài khoản: **{suggested_account}**\n"
            f"• Ghi chú: {note}\n\n"
            f"💡 **Đúng không? Xác nhận hoặc chỉnh sửa:**",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        # Stop propagation
        raise ApplicationHandlerStop
    
    else:
        # No match found - show category suggestions
        # Save transaction data to context
        context.user_data['pending_transaction'] = {
            'type': transaction_type,
            'amount': amount,
            'note': note,
            'category': note,  # Will be auto-detected by API
            'timestamp': datetime.now().isoformat()
        }
        
        # Filter categories by transaction type
        filtered_cats = [c for c in categories if c.get('type') == transaction_type]
        
        # Build keyboard with category suggestions
        keyboard = []
        
        if transaction_type == "Thu":
            # Income: Show popular income categories
            income_cats = [c for c in filtered_cats if c.get('name') in ['Lương', 'Kinh doanh', 'Cho thuê', 'Lãi đầu tư', 'Bán hàng', 'Quà tặng']]
            
            # Add category buttons (max 6, 2 per row)
            for i in range(0, min(6, len(income_cats)), 2):
                row = []
                for cat in income_cats[i:i+2]:
                    icon = cat.get('icon', '💰')
                    name = cat['name']
                    cat_id = cat.get('id', '')
                    row.append(InlineKeyboardButton(
                        f"{icon} {name}",
                        callback_data=f"qr_cat_{cat_id}"
                    ))
                keyboard.append(row)
        else:
            # Expense: Show popular expense categories
            expense_cats = [c for c in filtered_cats if c.get('name') in ['Ăn uống', 'Mua sắm', 'Giải trí', 'Y tế', 'Giáo dục', 'Điện nước']]
            
            # Add category buttons (max 6, 2 per row)
            for i in range(0, min(6, len(expense_cats)), 2):
                row = []
                for cat in expense_cats[i:i+2]:
                    icon = cat.get('icon', '💸')
                    name = cat['name']
                    cat_id = cat.get('id', '')
                    row.append(InlineKeyboardButton(
                        f"{icon} {name}",
                        callback_data=f"qr_cat_{cat_id}"
                    ))
                keyboard.append(row)
        
        # Add "Other category..." button
        keyboard.append([
            InlineKeyboardButton("📝 Chọn danh mục khác...", callback_data="qr_show_all_cats")
        ])
        
        # Add Cancel button
        keyboard.append([
            InlineKeyboardButton("❌ Hủy", callback_data="qr_cancel")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Build message
        message_text = (
            f"📝 **Giao dịch mới**\n\n"
            f"• Loại: **{transaction_type}**\n"
            f"• Số tiền: **{amount:,.0f} ₫**\n"
            f"• Ghi chú: {note}\n\n"
        )
        
        if filtered_cats:
            message_text += f"💡 **Chọn danh mục phù hợp:**"
        else:
            message_text += f"⚠️ Không tìm thấy danh mục. Tạo giao dịch với tự động phân bổ hoặc chọn hũ:"
        
        await update.message.reply_text(
            message_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        # Stop propagation to prevent AI handler
        raise ApplicationHandlerStop


async def handle_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category selection callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Check if pending transaction exists
    if 'pending_transaction' not in context.user_data:
        await query.edit_message_text("⚠️ Không tìm thấy giao dịch. Vui lòng thử lại.")
        return
    
    # Get selected category ID
    cat_id = query.data.replace("qr_cat_", "")
    
    # Get user from database
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.spreadsheet_id:
        await query.edit_message_text("⚠️ Bạn chưa kết nối Google Sheets!")
        return
    
    try:
        client = SheetsAPIClient(user.spreadsheet_id, user.web_app_url)
        categories_result = await client.get_categories()
        
        if not categories_result.get("success"):
            categories = get_popular_categories()
        else:
            categories = categories_result.get("categories", [])
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        categories = get_popular_categories()
    
    # Find selected category
    selected_cat = next((c for c in categories if c.get('id') == cat_id), None)
    
    if not selected_cat:
        await query.edit_message_text("⚠️ Danh mục không tồn tại. Vui lòng thử lại.")
        return
    
    # Save category to pending transaction
    context.user_data['pending_transaction']['category'] = selected_cat['name']
    context.user_data['pending_transaction']['category_id'] = cat_id
    context.user_data['pending_transaction']['category_icon'] = selected_cat.get('icon', '📝')
    
    transaction = context.user_data['pending_transaction']
    
    # ✅ Check if category has default jar assignment
    has_auto_allocate = selected_cat.get('autoAllocate', False)
    has_jar_id = selected_cat.get('jarId') and str(selected_cat.get('jarId')).strip() != ''
    
    # If category has jar assignment → Auto-assign and skip jar selection
    if has_auto_allocate or has_jar_id:
        # Determine jar value
        if has_auto_allocate:
            jar_id = 'AUTO_6JARS'
            jar_display = '🏺 Tự động phân bổ 6 hũ'
        else:
            jar_id = str(selected_cat.get('jarId')).strip()
            jar_display_names = {
                'NEC': '🏠 NEC - Nhu cầu thiết yếu (45%)',
                'LTSS': '💰 LTSS - Tiết kiệm dài hạn (10%)',
                'EDU': '📚 EDU - Giáo dục (10%)',
                'PLAY': '🎮 PLAY - Giải trí (5%)',
                'FFA': '💎 FFA - Tự do tài chính (25%)',
                'GIVE': '❤️ GIVE - Từ thiện (5%)'
            }
            jar_display = jar_display_names.get(jar_id, jar_id)
        
        # Save jar to pending transaction
        context.user_data['pending_transaction']['jar'] = jar_id
        
        # Show account selection directly
        keyboard = [
            [
                InlineKeyboardButton("💵 Cash", callback_data="qr_acc_Cash"),
                InlineKeyboardButton("🏦 Vietcombank", callback_data="qr_acc_VCB"),
            ],
            [
                InlineKeyboardButton("🏦 Techcombank", callback_data="qr_acc_TCB"),
                InlineKeyboardButton("🏦 OCB", callback_data="qr_acc_OCB"),
            ],
            [
                InlineKeyboardButton("💰 ZALO", callback_data="qr_acc_ZALO"),
                InlineKeyboardButton("💰 Khác", callback_data="qr_acc_Other"),
            ],
            [
                InlineKeyboardButton("« Quay lại", callback_data="qr_back_to_category"),
                InlineKeyboardButton("❌ Hủy", callback_data="qr_cancel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"📝 **Giao dịch mới**\n\n"
            f"• Loại: **{transaction['type']}**\n"
            f"• Số tiền: **{transaction['amount']:,.0f} ₫**\n"
            f"• Danh mục: {selected_cat.get('icon', '📝')} **{selected_cat['name']}**\n"
            f"• Ghi chú: {transaction['note']}\n"
            f"• Hũ phân bổ: **{jar_display}** ✅\n\n"
            f"💳 **Chọn tài khoản nguồn:**",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        # Category has NO jar assignment → Show jar selection menu
        keyboard = [
            [
                InlineKeyboardButton("🏠 NEC (45%)", callback_data="qr_jar_NEC"),
                InlineKeyboardButton("💰 LTSS (10%)", callback_data="qr_jar_LTSS"),
            ],
            [
                InlineKeyboardButton("📚 EDU (10%)", callback_data="qr_jar_EDU"),
                InlineKeyboardButton("🎮 PLAY (5%)", callback_data="qr_jar_PLAY"),
            ],
            [
                InlineKeyboardButton("💎 FFA (25%)", callback_data="qr_jar_FFA"),
                InlineKeyboardButton("❤️ GIVE (5%)", callback_data="qr_jar_GIVE"),
            ],
            [InlineKeyboardButton("🏺 Tự động phân bổ 6 hũ", callback_data="qr_jar_AUTO_6JARS")],
            [InlineKeyboardButton("❌ Không phân bổ hũ nào", callback_data="qr_jar_NO_JAR")],
            [InlineKeyboardButton("« Quay lại", callback_data="qr_back_to_category")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"💰 **Chọn hũ phân bổ**\n\n"
            f"• {transaction['type']}: **{transaction['amount']:,.0f} ₫**\n"
            f"• Danh mục: {selected_cat.get('icon', '📝')} **{selected_cat['name']}**\n"
            f"• Ghi chú: {transaction['note']}\n\n"
            f"⚠️ Danh mục này chưa có hũ mặc định\n"
            f"👇 **Chọn hũ để phân bổ tiền vào:**",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )


# NOTE: Function này không còn dùng từ 2026-02-16
# Logic mới: Category có jarId/autoAllocate → tự động dùng, skip jar menu
#           Category chưa có → show jar menu (8 options bao gồm cả Auto)
# 
# async def handle_auto_allocate(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handle auto allocate to 6 jars - DEPRECATED"""
#     pass


async def handle_show_all_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all categories for selection"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Check if pending transaction exists
    if 'pending_transaction' not in context.user_data:
        await query.edit_message_text("⚠️ Không tìm thấy giao dịch. Vui lòng thử lại.")
        return
    
    transaction = context.user_data['pending_transaction']
    transaction_type = transaction['type']
    
    # Get user from database
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.spreadsheet_id:
        await query.edit_message_text("⚠️ Bạn chưa kết nối Google Sheets!")
        return
    
    try:
        client = SheetsAPIClient(user.spreadsheet_id, user.web_app_url)
        categories_result = await client.get_categories()
        
        if not categories_result.get("success"):
            categories = get_popular_categories()
        else:
            categories = categories_result.get("categories", [])
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        categories = get_popular_categories()
    
    # Filter by transaction type
    filtered_cats = [c for c in categories if c.get('type') == transaction_type]
    
    if not filtered_cats:
        await query.edit_message_text(
            f"⚠️ Không có danh mục {transaction_type} nào.\n"
            f"Vui lòng thêm danh mục vào Google Sheets của bạn."
        )
        return
    
    # Build keyboard (3 columns, multiple rows)
    keyboard = []
    for i in range(0, len(filtered_cats), 3):
        row = []
        for cat in filtered_cats[i:i+3]:
            icon = cat.get('icon', '📝')
            name = cat['name']
            # Shorten name if too long
            if len(name) > 8:
                name = name[:7] + '.'
            cat_id = cat.get('id', '')
            row.append(InlineKeyboardButton(
                f"{icon} {name}",
                callback_data=f"qr_cat_{cat_id}"
            ))
        keyboard.append(row)
    
    # Add cancel button
    keyboard.append([
        InlineKeyboardButton("❌ Hủy", callback_data="qr_cancel")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"📝 **Chọn danh mục {transaction_type}**\n\n"
        f"• Số tiền: **{transaction['amount']:,.0f} ₫**\n"
        f"• Ghi chú: {transaction['note']}\n\n"
        f"💡 **Chọn danh mục:**",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def handle_jar_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle jar selection callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Check if cancelled
    if query.data == "qr_cancel":
        await query.edit_message_text("❌ Đã hủy giao dịch.")
        context.user_data.pop('pending_transaction', None)
        return
    
    # Get jar selection
    jar_id = query.data.replace("qr_jar_", "")
    
    # Check if pending transaction exists
    if 'pending_transaction' not in context.user_data:
        await query.edit_message_text("⚠️ Không tìm thấy giao dịch. Vui lòng thử lại.")
        return
    
    # Save jar to pending transaction
    context.user_data['pending_transaction']['jar'] = jar_id
    
    # ✅ FIX: Get jar display name
    jar_display_names = {
        'NEC': '🏠 NEC - Nhu cầu thiết yếu (45%)',
        'LTSS': '💰 LTSS - Tiết kiệm dài hạn (10%)',
        'EDU': '📚 EDU - Giáo dục (10%)',
        'PLAY': '🎮 PLAY - Giải trí (5%)',
        'FFA': '💎 FFA - Tự do tài chính (25%)',
        'GIVE': '❤️ GIVE - Từ thiện (5%)',
        'AUTO_6JARS': '🏺 Tự động phân bổ 6 hũ',
        'NO_JAR': '❌ Không phân bổ hũ nào'
    }
    jar_display = jar_display_names.get(jar_id, jar_id)
    
    # Show account selection keyboard
    keyboard = [
        [
            InlineKeyboardButton("💵 Cash", callback_data="qr_acc_Cash"),
            InlineKeyboardButton("🏦 Vietcombank", callback_data="qr_acc_VCB"),
        ],
        [
            InlineKeyboardButton("🏦 Techcombank", callback_data="qr_acc_TCB"),
            InlineKeyboardButton("🏦 OCB", callback_data="qr_acc_OCB"),
        ],
        [
            InlineKeyboardButton("💰 ZALO", callback_data="qr_acc_ZALO"),
            InlineKeyboardButton("💰 Khác", callback_data="qr_acc_Other"),
        ],
        [
            InlineKeyboardButton("« Quay lại", callback_data="qr_back_jar"),
            InlineKeyboardButton("❌ Hủy", callback_data="qr_cancel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    transaction = context.user_data['pending_transaction']
    await query.edit_message_text(
        f"📝 **Giao dịch mới**\n\n"
        f"• Loại: **{transaction['type']}**\n"
        f"• Số tiền: **{transaction['amount']:,.0f} ₫**\n"
        f"• Ghi chú: {transaction['note']}\n"
        f"• Hũ phân bổ: **{jar_display}**\n\n"
        f"💳 **Chọn tài khoản nguồn:**",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def handle_account_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle account selection and write to sheet"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Check if cancelled
    if query.data == "qr_cancel":
        await query.edit_message_text("❌ Đã hủy giao dịch.")
        context.user_data.pop('pending_transaction', None)
        return
    
    # Check if back button
    if query.data == "qr_back_jar":
        # Show jar selection again
        keyboard = [
            [
                InlineKeyboardButton("💰 NEC - Necessities", callback_data="qr_jar_NEC"),
                InlineKeyboardButton("🎯 FFA - Play", callback_data="qr_jar_FFA"),
            ],
            [
                InlineKeyboardButton("🎮 PLAY - Giải trí", callback_data="qr_jar_PLAY"),
                InlineKeyboardButton("📚 LTS - Học tập", callback_data="qr_jar_LTS"),
            ],
            [
                InlineKeyboardButton("🎓 EDU - Giáo dục", callback_data="qr_jar_EDU"),
                InlineKeyboardButton("💝 GIVE - Cho đi", callback_data="qr_jar_GIVE"),
            ],
            [
                InlineKeyboardButton("❌ Hủy", callback_data="qr_cancel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        transaction = context.user_data['pending_transaction']
        await query.edit_message_text(
            f"📝 **Giao dịch mới**\n\n"
            f"• Loại: **{transaction['type']}**\n"
            f"• Số tiền: **{transaction['amount']:,.0f} ₫**\n"
            f"• Ghi chú: {transaction['note']}\n\n"
            f"🏺 **Chọn hũ tiền để ghi:**",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return
    
    # Get account selection
    account_id = query.data.replace("qr_acc_", "")
    
    # Check if pending transaction exists
    if 'pending_transaction' not in context.user_data:
        await query.edit_message_text("⚠️ Không tìm thấy giao dịch. Vui lòng thử lại.")
        return
    
    transaction = context.user_data['pending_transaction']
    
    # ✅ CRITICAL FIX: Validate jar exists before proceeding
    if 'jar' not in transaction or not transaction['jar']:
        logger.error(f"❌ [Account Selection] Missing jar in transaction: {transaction}")
        await query.edit_message_text(
            "⚠️ **Lỗi dữ liệu giao dịch**\n\n"
            "Hũ tiền chưa được chọn. Vui lòng thử lại.\n\n"
            "Gõ lại số tiền để bắt đầu mới."
        )
        context.user_data.pop('pending_transaction', None)
        return
    
    transaction['account'] = account_id
    
    # Show processing message
    await query.edit_message_text(
        f"🔄 Đang ghi giao dịch...\n\n"
        f"• Loại: {transaction['type']}\n"
        f"• Số tiền: {transaction['amount']:,.0f} ₫\n"
        f"• Ghi chú: {transaction['note']}\n"
        f"• Hũ: {transaction['jar']}\n"
        f"• Tài khoản: {account_id}\n\n"
        f"⏳ Vui lòng đợi..."
    )
    
    # Get user from database
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.spreadsheet_id:
        await query.edit_message_text("⚠️ Không tìm thấy spreadsheet ID. Vui lòng /connectsheets lại.")
        context.user_data.pop('pending_transaction', None)
        return
    
    # Call API to write to sheet
    try:
        # ✅ FIX: Pass user's Web App URL to client
        logger.info(f"🔧 [Account] Creating SheetsAPIClient for user {user_id}")
        logger.info(f"📊 [Account] Spreadsheet ID: {user.spreadsheet_id[:20]}...")
        webapp_url_display = user.web_app_url[:80] if user.web_app_url else 'NOT SET'
        logger.info(f"🌐 [Account] Web App URL: {webapp_url_display}")
        
        client = SheetsAPIClient(user.spreadsheet_id, user.web_app_url)
        
        # ✅ FIX: Convert AUTO_6JARS and NO_JAR to empty string for backend
        jar_value = ""
        if transaction['jar'] not in ['AUTO_6JARS', 'NO_JAR']:
            jar_value = transaction['jar']
        
        logger.info(f"📤 [Account] Calling add_transaction: type={transaction['type']}, amount={transaction['amount']}, jar={jar_value}")
        result = await client.add_transaction(
            amount=transaction['amount'],
            category=transaction['category'],
            note=transaction['note'],
            transaction_type=transaction['type'],  # ✅ FIX: Pass transaction type
            from_jar=jar_value,
            from_account=account_id,
            to_account=""  # Not used for expense
        )
        
        if result.get("success"):
            # Success!
            category = result.get("category", transaction['note'])
            await query.edit_message_text(
                f"✅ Đã ghi thành công!\n\n"
                f"• {transaction['type']}: {transaction['amount']:,.0f} ₫\n"
                f"• Danh mục: {category}\n"
                f"• Hũ: {transaction['jar']}\n"
                f"• Tài khoản: {account_id}\n"
                f"• Ghi chú: {transaction['note']}\n"
                f"• Thời gian: {result.get('timestamp', 'N/A')}\n\n"
                f"💡 Dùng /balance để xem số dư nhé!"
            )
            logger.info(f"✅ User {user_id} quick record: {transaction['type']} {transaction['amount']:,.0f} - {category} - {transaction['jar']}")
        else:
            # Failed
            error_msg = result.get("error", "Unknown error")
            await query.edit_message_text(
                f"❌ **Không ghi được giao dịch**\n\n"
                f"Lá»—i: {error_msg}\n\n"
                f"Vui lòng thử lại hoặc liên hệ admin. 😢"
            )
            logger.error(f"❌ User {user_id} quick record failed: {error_msg}")
    
    except Exception as e:
        logger.error(f"❌ Error writing transaction: {e}")
        await query.edit_message_text(
            f"❌ **Lỗi khi ghi giao dịch**\n\n"
            f"Chi tiết: {str(e)}\n\n"
            f"Vui lòng thử lại sau. 😢"
        )
    
    # Clear pending transaction
    context.user_data.pop('pending_transaction', None)


async def handle_confirm_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle confirmation button - write transaction immediately"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Check if pending transaction exists
    if 'pending_transaction' not in context.user_data:
        await query.edit_message_text("⚠️ Không tìm thấy giao dịch. Vui lòng thử lại.")
        return
    
    transaction = context.user_data['pending_transaction']
    
    # Show processing message
    await query.edit_message_text(
        f"🔄 Đang ghi giao dịch...\n\n"
        f"• {transaction['type']}: {transaction['amount']:,.0f} ₫\n"
        f"• Danh mục: {transaction.get('category_icon', '📝')} {transaction['category']}\n"
        f"• Hũ: {transaction['jar']}\n"
        f"• Tài khoản: {transaction['account']}\n\n"
        f"⏳ Vui lòng đợi..."
    )
    
    # Get user from database
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.spreadsheet_id:
        await query.edit_message_text("⚠️ Không tìm thấy spreadsheet ID. Vui lòng /connectsheets lại.")
        context.user_data.pop('pending_transaction', None)
        return
    
    # Call API to write to sheet
    try:
        # ✅ FIX: Pass user's Web App URL to client
        logger.info(f"🔧 Creating SheetsAPIClient for user {user_id}")
        logger.info(f"📊 Spreadsheet ID: {user.spreadsheet_id[:20]}...")
        webapp_url_display = user.web_app_url[:80] if user.web_app_url else 'NOT SET'
        logger.info(f"🌐 Web App URL: {webapp_url_display}")
        logger.info(f"DEBUG - web_app_url type: {type(user.web_app_url)}, value: {user.web_app_url is not None}")
        
        client = SheetsAPIClient(user.spreadsheet_id, user.web_app_url)
        
        # ✅ FIX: Convert AUTO_6JARS and NO_JAR to empty string for backend
        jar_value = ""
        if transaction['jar'] not in ['AUTO_6JARS', 'NO_JAR']:
            jar_value = transaction['jar']
        
        logger.info(f"📤 Calling add_transaction: type={transaction['type']}, amount={transaction['amount']}, category={transaction['category']}, jar={jar_value}")
        result = await client.add_transaction(
            amount=transaction['amount'],
            category=transaction['category'],
            note=transaction['note'],
            transaction_type=transaction['type'],  # ✅ FIX: Pass transaction type
            from_jar=jar_value,
            from_account=transaction['account'],
            to_account=""
        )
        
        if result.get("success"):
            # Success!
            await query.edit_message_text(
                f"✅ **Đã ghi thành công!**\n\n"
                f"• {transaction['type']}: **{transaction['amount']:,.0f} ₫**\n"
                f"• Danh mục: {transaction.get('category_icon', '📝')} **{transaction['category']}**\n"
                f"• Hũ: **{transaction['jar']}** - {get_jar_name(transaction['jar'])}\n"
                f"• Tài khoản: **{transaction['account']}**\n"
                f"• Ghi chú: {transaction['note']}\n"
                f"• Thời gian: {result.get('timestamp', 'N/A')}\n\n"
                f"💡 Dùng /balance để xem số dư nhé!",
                parse_mode="Markdown"
            )
            logger.info(f"✅ User {user_id} confirmed quick record: {transaction['type']} {transaction['amount']:,.0f} - {transaction['category']} - {transaction['jar']}")
        else:
            # Failed
            error_msg = result.get("error", "Unknown error")
            await query.edit_message_text(
                f"❌ **Không ghi được giao dịch**\n\n"
                f"Lá»—i: {error_msg}\n\n"
                f"Vui lòng thử lại hoặc liên hệ admin. 😢"
            )
            logger.error(f"❌ User {user_id} quick record failed: {error_msg}")
    
    except Exception as e:
        logger.error(f"❌ Error writing transaction: {e}")
        await query.edit_message_text(
            f"❌ **Lỗi khi ghi giao dịch**\n\n"
            f"Chi tiết: {str(e)}\n\n"
            f"Vui lòng thử lại sau. 😢"
        )
    
    # Clear pending transaction
    context.user_data.pop('pending_transaction', None)


async def handle_edit_jar_from_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle edit jar button from confirmation screen"""
    query = update.callback_query
    await query.answer()
    
    # Check if pending transaction exists
    if 'pending_transaction' not in context.user_data:
        await query.edit_message_text("⚠️ Không tìm thấy giao dịch. Vui lòng thử lại.")
        return
    
    # Show jar selection
    keyboard = [
        [
            InlineKeyboardButton("💰 NEC - Necessities", callback_data="qr_jar_edit_NEC"),
            InlineKeyboardButton("🎯 FFA - Tự do tài chính", callback_data="qr_jar_edit_FFA"),
        ],
        [
            InlineKeyboardButton("🎮 PLAY - Giải trí", callback_data="qr_jar_edit_PLAY"),
            InlineKeyboardButton("📚 LTSS - Tiết kiệm", callback_data="qr_jar_edit_LTSS"),
        ],
        [
            InlineKeyboardButton("🎓 EDU - Giáo dục", callback_data="qr_jar_edit_EDU"),
            InlineKeyboardButton("💝 GIVE - Cho đi", callback_data="qr_jar_edit_GIVE"),
        ],
        [
            InlineKeyboardButton("« Quay lại", callback_data="qr_back_to_confirm"),
            InlineKeyboardButton("❌ Hủy", callback_data="qr_cancel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    transaction = context.user_data['pending_transaction']
    await query.edit_message_text(
        f"📝 **Chọn hũ mới**\n\n"
        f"• {transaction['type']}: **{transaction['amount']:,.0f} ₫**\n"
        f"• Danh mục: {transaction.get('category_icon', '📝')} {transaction['category']}\n"
        f"• Hũ hiện tại: **{transaction['jar']}**\n\n"
        f"🏺 **Chọn hũ khác:**",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def handle_jar_edit_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle jar selection from edit screen"""
    query = update.callback_query
    await query.answer()
    
    # Get jar ID from callback data
    jar_id = query.data.replace("qr_jar_edit_", "")
    
    # Check if pending transaction exists
    if 'pending_transaction' not in context.user_data:
        await query.edit_message_text("⚠️ Không tìm thấy giao dịch. Vui lòng thử lại.")
        return
    
    # Update jar in pending transaction
    context.user_data['pending_transaction']['jar'] = jar_id
    
    # Show updated confirmation
    transaction = context.user_data['pending_transaction']
    keyboard = [
        [InlineKeyboardButton("✅ Xác nhận và ghi", callback_data="qr_confirm")],
        [
            InlineKeyboardButton("✏️ Sửa danh mục", callback_data="qr_edit_category"),
            InlineKeyboardButton("✏️ Sửa hũ", callback_data="qr_edit_jar"),
        ],
        [
            InlineKeyboardButton("💳 Đổi tài khoản", callback_data="qr_edit_account"),
            InlineKeyboardButton("❌ Hủy", callback_data="qr_cancel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"📝 **Phân loại tự động** (đã cập nhật)\n\n"
        f"• {transaction['type']}: **{transaction['amount']:,.0f} ₫**\n"
        f"• Danh mục: {transaction.get('category_icon', '📝')} **{transaction['category']}**\n"
        f"• Hũ: **{jar_id}** - {get_jar_name(jar_id)}\n"
        f"• Tài khoản: **{transaction['account']}**\n"
        f"• Ghi chú: {transaction['note']}\n\n"
        f"💡 **Đúng không? Xác nhận hoặc chỉnh sửa:**",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def handle_back_to_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back button - return to confirmation screen"""
    query = update.callback_query
    await query.answer()
    
    # Check if pending transaction exists
    if 'pending_transaction' not in context.user_data:
        await query.edit_message_text("⚠️ Không tìm thấy giao dịch. Vui lòng thử lại.")
        return
    
    # Show confirmation screen again
    transaction = context.user_data['pending_transaction']
    keyboard = [
        [InlineKeyboardButton("✅ Xác nhận và ghi", callback_data="qr_confirm")],
        [
            InlineKeyboardButton("✏️ Sửa danh mục", callback_data="qr_edit_category"),
            InlineKeyboardButton("✏️ Sửa hũ", callback_data="qr_edit_jar"),
        ],
        [
            InlineKeyboardButton("💳 Đổi tài khoản", callback_data="qr_edit_account"),
            InlineKeyboardButton("❌ Hủy", callback_data="qr_cancel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"📝 **Phân loại tự động**\n\n"
        f"• {transaction['type']}: **{transaction['amount']:,.0f} ₫**\n"
        f"• Danh mục: {transaction.get('category_icon', '📝')} **{transaction['category']}**\n"
        f"• Hũ: **{transaction['jar']}** - {get_jar_name(transaction['jar'])}\n"
        f"• Tài khoản: **{transaction['account']}**\n"
        f"• Ghi chú: {transaction['note']}\n\n"
        f"💡 **Đúng không? Xác nhận hoặc chỉnh sửa:**",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def handle_edit_account_from_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle edit account button from confirmation screen"""
    query = update.callback_query
    await query.answer()
    
    # Check if pending transaction exists
    if 'pending_transaction' not in context.user_data:
        await query.edit_message_text("⚠️ Không tìm thấy giao dịch. Vui lòng thử lại.")
        return
    
    # Show account selection
    keyboard = [
        [
            InlineKeyboardButton("💵 Cash", callback_data="qr_acc_edit_Cash"),
            InlineKeyboardButton("🏦 Vietcombank", callback_data="qr_acc_edit_VCB"),
        ],
        [
            InlineKeyboardButton("🏦 Techcombank", callback_data="qr_acc_edit_TCB"),
            InlineKeyboardButton("🏦 OCB", callback_data="qr_acc_edit_OCB"),
        ],
        [
            InlineKeyboardButton("💰 ZALO", callback_data="qr_acc_edit_ZALO"),
            InlineKeyboardButton("💰 Khác", callback_data="qr_acc_edit_Other"),
        ],
        [
            InlineKeyboardButton("« Quay lại", callback_data="qr_back_to_confirm"),
            InlineKeyboardButton("❌ Hủy", callback_data="qr_cancel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    transaction = context.user_data['pending_transaction']
    await query.edit_message_text(
        f"📝 **Chọn tài khoản mới**\n\n"
        f"• {transaction['type']}: **{transaction['amount']:,.0f} ₫**\n"
        f"• Tài khoản hiện tại: **{transaction['account']}**\n\n"
        f"💳 **Chọn tài khoản khác:**",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def handle_account_edit_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle account selection from edit screen"""
    query = update.callback_query
    await query.answer()
    
    # Get account ID from callback data
    account_id = query.data.replace("qr_acc_edit_", "")
    
    # Check if pending transaction exists
    if 'pending_transaction' not in context.user_data:
        await query.edit_message_text("⚠️ Không tìm thấy giao dịch. Vui lòng thử lại.")
        return
    
    # Update account in pending transaction
    context.user_data['pending_transaction']['account'] = account_id
    
    # Show updated confirmation
    transaction = context.user_data['pending_transaction']
    keyboard = [
        [InlineKeyboardButton("✅ Xác nhận và ghi", callback_data="qr_confirm")],
        [
            InlineKeyboardButton("✏️ Sửa danh mục", callback_data="qr_edit_category"),
            InlineKeyboardButton("✏️ Sửa hũ", callback_data="qr_edit_jar"),
        ],
        [
            InlineKeyboardButton("💳 Đổi tài khoản", callback_data="qr_edit_account"),
            InlineKeyboardButton("❌ Hủy", callback_data="qr_cancel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"📝 **Phân loại tự động** (đã cập nhật)\n\n"
        f"• {transaction['type']}: **{transaction['amount']:,.0f} ₫**\n"
        f"• Danh mục: {transaction.get('category_icon', '📝')} **{transaction['category']}**\n"
        f"• Hũ: **{transaction['jar']}** - {get_jar_name(transaction['jar'])}\n"
        f"• Tài khoản: **{account_id}**\n"
        f"• Ghi chú: {transaction['note']}\n\n"
        f"💡 **Đúng không? Xác nhận hoặc chỉnh sửa:**",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


def register_quick_record_handlers(application):
    """Register quick record message handlers"""
    
    # Handler for messages matching quick record patterns
    # High priority (group=0) to process before AI handler
    # Match any text containing amount patterns:
    # - 50k, 1.5tr, 200 nghìn, 1,5 triệu, 1,500,000
    # - With or without keywords (chi, mua, thu, etc.)
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.Regex(
                r'\d+(?:[,.\d]*)?(?:\s*(?:k|tr|triệu|nghìn|nghin)\b|(?:,\d{3})+)'
            ),
            handle_quick_record
        ),
        group=0  # High priority - process first
    )
    
    # Callback handlers for confirmation flow
    application.add_handler(
        CallbackQueryHandler(handle_confirm_transaction, pattern=r'^qr_confirm$')
    )
    application.add_handler(
        CallbackQueryHandler(handle_edit_jar_from_confirmation, pattern=r'^qr_edit_jar$')
    )
    application.add_handler(
        CallbackQueryHandler(handle_jar_edit_selection, pattern=r'^qr_jar_edit_')
    )
    application.add_handler(
        CallbackQueryHandler(handle_edit_account_from_confirmation, pattern=r'^qr_edit_account$')
    )
    application.add_handler(
        CallbackQueryHandler(handle_account_edit_selection, pattern=r'^qr_acc_edit_')
    )
    application.add_handler(
        CallbackQueryHandler(handle_back_to_confirm, pattern=r'^qr_back_to_confirm$')
    )
    
    # NEW: Category selection handlers
    application.add_handler(
        CallbackQueryHandler(handle_category_selection, pattern=r'^qr_cat_')
    )
    application.add_handler(
        CallbackQueryHandler(handle_show_all_categories, pattern=r'^qr_show_all_cats$')
    )
    application.add_handler(
        CallbackQueryHandler(handle_show_all_categories, pattern=r'^qr_back_to_category$')  # Reuse same handler
    )
    
    # Callback handlers for jar and account selection (old flow - no match found)
    application.add_handler(
        CallbackQueryHandler(handle_jar_selection, pattern=r'^qr_jar_[^e]')  # Exclude qr_jar_edit_
    )
    application.add_handler(
        CallbackQueryHandler(handle_account_selection, pattern=r'^qr_acc_[^e]|^qr_back_jar$')  # Exclude qr_acc_edit_
    )
    application.add_handler(
        CallbackQueryHandler(handle_jar_selection, pattern=r'^qr_cancel$')  # Handle cancel in any flow
    )
    
    logger.info("✅ Quick Record (Template) handlers registered")

