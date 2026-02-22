"""
Message Handler - Process user messages with FAQ or AI
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
import json
import html
from pathlib import Path
from datetime import datetime
from bot.middleware.usage_tracker import check_message_limit
from config.settings import settings


# Load FAQ data
FAQ_FILE = Path(__file__).parent.parent / "knowledge" / "faq.json"
with open(FAQ_FILE, "r", encoding="utf-8") as f:
    FAQ_DATA = json.load(f)


def search_faq(query: str) -> dict:
    """
    Search FAQ based on keywords matching
    Returns: {"found": bool, "answer": str, "category": str}
    """
    query_lower = query.lower()
    
    # Check default responses first
    default_responses = FAQ_DATA.get("default_responses", {})
    
    # Greeting
    if any(word in query_lower for word in default_responses.get("greeting", [])):
        return {
            "found": True,
            "answer": default_responses.get("greeting_response"),
            "category": "greeting"
        }
    
    # Thanks
    if any(word in query_lower for word in default_responses.get("thanks", [])):
        return {
            "found": True,
            "answer": default_responses.get("thanks_response"),
            "category": "thanks"
        }
    
    # Goodbye
    if any(word in query_lower for word in default_responses.get("goodbye", [])):
        return {
            "found": True,
            "answer": default_responses.get("goodbye_response"),
            "category": "goodbye"
        }
    
    # Search in FAQ categories
    for category in FAQ_DATA.get("categories", []):
        for question in category.get("questions", []):
            keywords = question.get("keywords", [])
            
            # Check if any keyword matches
            if any(keyword.lower() in query_lower for keyword in keywords):
                return {
                    "found": True,
                    "answer": question.get("answer"),
                    "category": category.get("name"),
                    "icon": category.get("icon")
                }
    
    # Not found
    return {
        "found": False,
        "answer": None,
        "category": None
    }


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages from users"""
    
    user = update.effective_user
    message_text = update.message.text
    logger.info(f"User {user.id} ({user.username}): {message_text}")

    # CRITICAL: Skip keyboard menu button presses — they are handled by dedicated handlers
    try:
        from bot.core.keyboard import (
            BTN_RECORD, BTN_REPORT, BTN_SHEETS, BTN_WEBAPP,
            BTN_SHARE, BTN_DONATE, BTN_GUIDE, BTN_SETTINGS,
        )
        _MENU_BUTTONS = {BTN_RECORD, BTN_REPORT, BTN_SHEETS, BTN_WEBAPP,
                         BTN_SHARE, BTN_DONATE, BTN_GUIDE, BTN_SETTINGS}
    except Exception:
        _MENU_BUTTONS = set()
    if message_text in _MENU_BUTTONS:
        logger.info(f"  → Skipping AI handler - known menu button: {message_text!r}")
        return

    # CRITICAL: Skip if user is in a ConversationHandler flow
    # Check for any active conversation state in context
    conversation_state = context.user_data.get('conversation_state')
    if conversation_state is not None:
        logger.info(f"  → Skipping AI handler - user in conversation (state: {conversation_state})")
        return
    
    # Check if user is entering email for web-registration lookup
    if context.user_data.get('awaiting_web_email'):
        await handle_web_email_input(update, context)
        return

    # Check if user is sending payment proof
    if context.user_data.get('awaiting_payment_proof'):
        await handle_payment_proof_text(update, context)
        return
    
    # Check if admin is sending rejection reason
    if context.user_data.get('rejecting_payment'):
        await handle_admin_rejection_reason(update, context)
        return
    
    # Check message limit (FREE tier = 5 msg/day)
    can_send = await check_message_limit(update, context)
    if not can_send:
        return  # Middleware already sent upgrade prompt
    
    # Phase 1: Simple FAQ keyword matching
    faq_result = search_faq(message_text)
    
    if faq_result["found"]:
        # Found answer in FAQ
        answer = faq_result["answer"]
        category = faq_result.get("category", "")
        icon = faq_result.get("icon", "💬")
        
        # Quick action buttons
        keyboard = [
            [
                InlineKeyboardButton("✅ Giải quyết", callback_data="feedback_solved"),
                InlineKeyboardButton("❌ Vẫn lỗi", callback_data="feedback_unsolved")
            ],
            [
                InlineKeyboardButton("💬 Hỏi thêm", callback_data="ask_more"),
                InlineKeyboardButton("🆘 Liên hệ support", callback_data="contact_support")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            answer,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
    else:
        # Not found - fallback response
        fallback_text = """
🤔 **Xin lỗi, mình chưa hiểu câu hỏi của bạn.**

💡 **Gợi ý:**
• Hỏi bằng từ khóa đơn giản: "thêm giao dịch", "6 hũ", "tính ROI"
• Dùng /help để xem danh sách câu hỏi phổ biến
• Hoặc /support để liên hệ support team

🔍 **Ví dụ câu hỏi:**
• Làm sao thêm giao dịch?
• 6 hũ tiền là gì?
• Cách chuyển tiền giữa hũ?

💬 Thử hỏi lại nhé!
"""
        
        keyboard = [
            [
                InlineKeyboardButton("📚 Xem FAQ", callback_data="help_faq"),
                InlineKeyboardButton("🆘 Liên hệ support", callback_data="contact_support")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            fallback_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )


# Phase 2: Upgrade to AI-powered conversation
"""
from bot.ai.gpt_client import GPTClient

gpt_client = GPTClient()

async def handle_message_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Enhanced version with GPT-4
    
    # Try FAQ first (faster)
    faq_result = search_faq(message_text)
    if faq_result["found"]:
        # Send FAQ answer
        ...
        return
    
    # If not in FAQ, use GPT-4
    try:
        # Get conversation context
        user_context = await get_user_context(user.id)
        
        # Call GPT-4
        ai_response = await gpt_client.chat(
            message=message_text,
            context=user_context,
            user_id=user.id
        )
        
        # Save to context memory
        await save_message_to_context(user.id, message_text, ai_response)
        
        # Send AI response
        await update.message.reply_text(ai_response, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"GPT-4 error: {e}")
        # Fallback to not found message
        ...
"""


async def handle_payment_proof_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment proof submitted as text"""
    user_id = update.effective_user.id
    transaction_info = update.message.text
    
    # Clear the awaiting flag
    context.user_data['awaiting_payment_proof'] = False
    amount = context.user_data.get('payment_amount', 999000)
    
    # Create verification request
    from bot.services.payment_service import PaymentVerificationService
    
    try:
        verification_id = await PaymentVerificationService.create_verification_request(
            user_id=user_id,
            amount=amount,
            transaction_info=transaction_info,
            submitted_by=user_id
        )
        
        message = f"""
✅ **ĐÃ NHẬN THÔNG TIN**

Mã xác nhận: `{verification_id}`

━━━━━━━━━━━━━━━━━━━━━
📋 **THÔNG TIN NHẬN ĐƯỢC:**
━━━━━━━━━━━━━━━━━━━━━

{transaction_info}

━━━━━━━━━━━━━━━━━━━━━
⏱️ **TIẾP THEO:**
━━━━━━━━━━━━━━━━━━━━━

• Hệ thống đang kiểm tra thanh toán
• Nếu đúng nội dung CK → Tự động kích hoạt (5-10 phút)
• Nếu sai nội dung → Admin xác nhận thủ công (15-30 phút)

━━━━━━━━━━━━━━━━━━━━━
🔔 **THÔNG BÁO:**
━━━━━━━━━━━━━━━━━━━━━

✅ Bạn sẽ nhận thông báo khi Premium được kích hoạt
💬 Mọi thắc mắc, liên hệ Admin

Cảm ơn bạn đã tin tưởng Freedom Wallet! 💎
"""
        
        keyboard = [
            [InlineKeyboardButton("💬 Liên hệ Admin", callback_data="contact_support")],
            [InlineKeyboardButton("🏠 Về trang chủ", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        logger.info(f"Payment verification created: {verification_id} for user {user_id}")
        
        # Notify admin about new payment verification
        if settings.ADMIN_USER_ID:
            try:
                # Use HTML for safer parsing
                import html
                safe_username = html.escape(update.effective_user.username or 'N/A')
                safe_fullname = html.escape(update.effective_user.full_name or 'N/A')
                safe_transaction = html.escape(transaction_info)
                
                admin_message = f"""
🔔 <b>YÊU CẦU XÁC NHẬN THANH TOÁN MỚI</b>

Mã: <code>{verification_id}</code>
User ID: <code>{user_id}</code>
Username: @{safe_username}
Tên: {safe_fullname}
Số tiền: {amount:,.0f} VND

📋 <b>Thông tin:</b>
{safe_transaction}

⏱️ Thời gian: {update.message.date.strftime('%d/%m/%Y %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━
💡 <b>Hành động:</b>

• Xem pending: /payment_pending
• Duyệt: /payment_approve {verification_id}
• Từ chối: /payment_reject {verification_id} [lý do]
"""
                
                # Add inline buttons for quick action
                keyboard = [
                    [
                        InlineKeyboardButton("✅ Duyệt", callback_data=f"admin_approve_{verification_id}"),
                        InlineKeyboardButton("❌ Từ chối", callback_data=f"admin_reject_{verification_id}")
                    ],
                    [InlineKeyboardButton("📋 Xem tất cả pending", callback_data="admin_list_pending")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await context.bot.send_message(
                    chat_id=settings.ADMIN_USER_ID,
                    text=admin_message,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
                logger.info(f"Admin notification sent for {verification_id}")
            except Exception as notify_error:
                logger.error(f"Failed to notify admin: {notify_error}")
        
    except Exception as e:
        logger.error(f"Error creating payment verification: {e}")
        await update.message.reply_text(
            "❌ Có lỗi xảy ra. Vui lòng thử lại hoặc liên hệ Admin.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("💬 Liên hệ Admin", callback_data="contact_support")
            ]])
        )


async def handle_payment_proof_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment proof submitted as photo"""
    user_id = update.effective_user.id
    
    # Check if user is submitting payment proof
    if not context.user_data.get('awaiting_payment_proof'):
        # Not expecting payment proof, ignore
        return
    
    # Clear the awaiting flag
    context.user_data['awaiting_payment_proof'] = False
    amount = context.user_data.get('payment_amount', 999000)
    
    # Get photo file
    photo = update.message.photo[-1]  # Get highest resolution
    file = await photo.get_file()
    
    # Get caption if provided
    caption = update.message.caption or "Payment proof image"
    transaction_info = f"Photo: {file.file_id}\nCaption: {caption}"
    
    # Create verification request
    from bot.services.payment_service import PaymentVerificationService
    
    try:
        verification_id = await PaymentVerificationService.create_verification_request(
            user_id=user_id,
            amount=amount,
            transaction_info=transaction_info,
            submitted_by=user_id
        )
        
        message = f"""
✅ **ĐÃ NHẬN ẢNH XÁC NHẬN**

Mã xác nhận: `{verification_id}`

━━━━━━━━━━━━━━━━━━━━━
📸 **ẢNH NHẬN ĐƯỢC:**
━━━━━━━━━━━━━━━━━━━━━

Đã lưu ảnh chuyển khoản của bạn

━━━━━━━━━━━━━━━━━━━━━
⏱️ **TIẾP THEO:**
━━━━━━━━━━━━━━━━━━━━━

• Admin đang xác nhận thanh toán
• Thời gian xử lý: 15-30 phút (giờ hành chính)
• Ngoài giờ: Trong 2 giờ

━━━━━━━━━━━━━━━━━━━━━
🔔 **THÔNG BÁO:**
━━━━━━━━━━━━━━━━━━━━━

✅ Bạn sẽ nhận thông báo khi Premium được kích hoạt
💬 Mọi thắc mắc, liên hệ Admin

Cảm ơn bạn đã tin tưởng Freedom Wallet! 💎
"""
        
        keyboard = [
            [InlineKeyboardButton("💬 Liên hệ Admin", callback_data="contact_support")],
            [InlineKeyboardButton("🏠 Về trang chủ", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        logger.info(f"Payment verification (photo) created: {verification_id} for user {user_id}")
        
        # Notify admin about new payment verification (with photo)
        if settings.ADMIN_USER_ID:
            try:
                # Use HTML for safer parsing
                import html
                safe_username = html.escape(update.effective_user.username or 'N/A')
                safe_fullname = html.escape(update.effective_user.full_name or 'N/A')
                safe_caption = html.escape(caption)
                
                admin_message = f"""
🔔 <b>YÊU CẦU XÁC NHẬN THANH TOÁN MỚI</b> 📸

Mã: <code>{verification_id}</code>
User ID: <code>{user_id}</code>
Username: @{safe_username}
Tên: {safe_fullname}
Số tiền: {amount:,.0f} VND

📸 <b>Ảnh xác nhận:</b>
Đã gửi ảnh chuyển khoản
Caption: {safe_caption}

⏱️ Thời gian: {update.message.date.strftime('%d/%m/%Y %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━
💡 <b>Hành động:</b>

• Xem pending: /payment_pending
• Duyệt: /payment_approve {verification_id}
• Từ chối: /payment_reject {verification_id} [lý do]
"""
                
                # Add inline buttons for quick action
                keyboard = [
                    [
                        InlineKeyboardButton("✅ Duyệt", callback_data=f"admin_approve_{verification_id}"),
                        InlineKeyboardButton("❌ Từ chối", callback_data=f"admin_reject_{verification_id}")
                    ],
                    [InlineKeyboardButton("📋 Xem tất cả pending", callback_data="admin_list_pending")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                # Send admin message with photo
                await context.bot.send_photo(
                    chat_id=settings.ADMIN_USER_ID,
                    photo=file.file_id,
                    caption=admin_message,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
                logger.info(f"Admin notification (with photo) sent for {verification_id}")
            except Exception as notify_error:
                logger.error(f"Failed to notify admin: {notify_error}")
        
    except Exception as e:
        logger.error(f"Error creating payment verification from photo: {e}")
        await update.message.reply_text(
            "❌ Có lỗi xảy ra. Vui lòng thử lại hoặc liên hệ Admin.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("💬 Liên hệ Admin", callback_data="contact_support")
            ]])
        )


async def handle_admin_rejection_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle rejection reason from admin"""
    from bot.services.payment_service import PaymentVerificationService
    from bot.utils.database import get_db, PaymentVerification
    from bot.handlers.admin_payment import is_admin
    
    user_id = update.effective_user.id
    
    # Check if user is admin
    if not is_admin(user_id):
        return
    
    verification_id = context.user_data.get('rejecting_payment')
    reason = update.message.text
    
    if not verification_id:
        return
    
    # Clear the flag
    context.user_data['rejecting_payment'] = None
    
    try:
        # Reject payment
        success = await PaymentVerificationService.reject_payment(
            verification_id=verification_id,
            rejected_by=user_id,
            reason=reason
        )
        
        if success:
            # Get verification details
            db = next(get_db())
            ver_id = int(verification_id.replace("VER", ""))
            verification = db.query(PaymentVerification).filter(
                PaymentVerification.id == ver_id
            ).first()
            
            if verification:
                # Log to Google Sheets
                from bot.handlers.admin_callbacks import log_payment_to_sheets
                from bot.utils.database import User
                user = db.query(User).filter(User.id == verification.user_id).first()
                
                if user:
                    await log_payment_to_sheets(
                        verification_id=verification_id,
                        user_id=user.id,
                        username=user.username,
                        full_name=user.full_name,
                        amount=verification.amount,
                        status="REJECTED",
                        approved_by=user_id,
                        approved_at=verification.approved_at or datetime.now(),
                        notes=reason  # Pass rejection reason
                    )
                
                # Notify user
                safe_reason = html.escape(reason)
                try:
                    await context.bot.send_message(
                        chat_id=verification.user_id,
                        text=f"""
❌ <b>THANH TOÁN BỊ TỪ CHỐI</b>

Mã xác nhận: <code>{verification_id}</code>

━━━━━━━━━━━━━━━━━━━━━
📋 <b>LÝ DO:</b>
━━━━━━━━━━━━━━━━━━━━━

{safe_reason}

━━━━━━━━━━━━━━━━━━━━━
💡 <b>HƯỚNG DẪN:</b>
━━━━━━━━━━━━━━━━━━━━━

• Kiểm tra lại thông tin thanh toán
• Đảm bảo chuyển khoản đúng:
  - Số tiền: 999,000 VND
  - Nội dung: FW{verification.user_id} PREMIUM
• Gửi lại ảnh/thông tin xác nhận

💬 Cần hỗ trợ? Dùng /support để liên hệ Admin
""",
                        parse_mode="HTML"
                    )
                except Exception as notify_error:
                    logger.error(f"Failed to notify user {verification.user_id}: {notify_error}")
            
            db.close()
            
            # Confirm to admin
            safe_reason_admin = html.escape(reason)
            await update.message.reply_text(
                f"""
✅ <b>ĐÃ TỪ CHỐI</b>

Mã: <code>{verification_id}</code>
Lý do: {safe_reason_admin}

User đã nhận thông báo.
""",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                f"❌ Lỗi khi từ chối {verification_id}",
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Error in handle_admin_rejection_reason: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Có lỗi xảy ra. Vui lòng thử lại!",
            parse_mode="HTML"
        )


async def handle_web_email_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process email entered by user — find in sheet, show info, then ask to confirm."""
    import re
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    text = update.message.text.strip()

    if not re.match(r'^[\w\.\+\-]+@[\w\.-]+\.\w{2,}$', text):
        await update.message.reply_text(
            "📧 Đây không phải email hợp lệ. Vui lòng nhập lại:"
        )
        return

    searching_msg = await update.message.reply_text("🔍 Đang tìm kiếm...")

    try:
        from bot.utils.sheets_registration import find_user_in_sheet_by_email
        sheet_data = await find_user_in_sheet_by_email(text)
        await searching_msg.delete()

        if not sheet_data:
            await update.message.reply_text(
                f"❌ Không tìm thấy email *{text}* trong hệ thống.\n\n"
                "Vui lòng kiểm tra lại email, hoặc dùng /support để được hỗ trợ.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("↩️ Nhập lại email", callback_data="web_already_registered")
                ]])
            )
            context.user_data.pop('awaiting_web_email', None)
            return

        # Found — save temporarily and ask user to confirm
        context.user_data.pop('awaiting_web_email', None)
        context.user_data['pending_web_link'] = sheet_data

        name  = sheet_data.get("full_name") or "(chưa có tên)"
        email = sheet_data.get("email", text)
        phone = sheet_data.get("phone") or "(chưa có)"
        plan  = sheet_data.get("plan", "FREE")

        await update.message.reply_text(
            f"🔍 Tìm thấy thông tin sau trong hệ thống:\n\n"
            f"👤 *Họ & Tên:* {name}\n"
            f"📧 *Email:* `{email}`\n"
            f"📱 *Điện thoại:* {phone}\n"
            f"💎 *Gói:* {plan}\n\n"
            f"Bạn xác nhận đây là tài khoản của mình không?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Đúng, xác nhận", callback_data="web_confirm_yes")],
                [InlineKeyboardButton("❌ Không phải tôi", callback_data="web_confirm_no")],
            ])
        )

    except Exception as e:
        logger.error(f"handle_web_email_input error: {e}", exc_info=True)
        try:
            await searching_msg.delete()
        except Exception:
            pass
        await update.message.reply_text("😓 Có lỗi xảy ra, vui lòng thử lại sau.")
        context.user_data.pop('awaiting_web_email', None)
