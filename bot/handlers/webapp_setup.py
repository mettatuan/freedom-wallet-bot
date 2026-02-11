"""
Web App Setup Guide Handler - 3-step guide to create Freedom Wallet Web App
Based on Huong_dan_tao_wepapp.html

Must be completed BEFORE using the app
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from loguru import logger
import os

# Web App Setup Guide Content - 3 Steps
WEBAPP_SETUP_STEPS = {
    0: {
        "title": "🚀 BƯỚC 1: TẠO WEB APP",
        "content": """
👋 **Chào mừng! Hãy bắt đầu thiết lập Freedom Wallet!**

━━━━━━━━━━━━━━━━━━━━━

**📍 BẠN ĐANG Ở ĐÂU?**

➡️ **BƯỚC 1: Tạo Web App** (bạn đang ở đây)
    → Bước 2: Học cách sử dụng

━━━━━━━━━━━━━━━━━━━━━

**🎯 BƯỚC 1 - BẠN SẼ LÀM GÌ?**

Trong 10-15 phút tới:
1️⃣ Tạo bản sao Google Sheets Template
2️⃣ Mở Extensions → App Script
3️⃣ Deploy Web App của riêng bạn

━━━━━━━━━━━━━━━━━━━━━

**✅ SAU KHI HOÀN THÀNH:**
• Web App cá nhân (chạy trên Google Sheets của bạn)
• Dữ liệu 100% riêng tư
• Truy cập mọi lúc, mọi thiết bị
• Không cần biết code

━━━━━━━━━━━━━━━━━━━━━

**⏱ THỜI GIAN**: 10-15 phút
**📱 THIẾT BỊ**: Desktop/Laptop (khuyến nghị)
**🔗 CẦN**: Tài khoản Google

💡 *Làm chậm cũng ổn. Có Group VIP hỗ trợ nếu cần!*
""",
        "image": None
    },
    
    1: {
        "title": "📋 BƯỚC 1: TẠO BẢN SAO TEMPLATE",
        "content": """
**� CÁCH LÀM:**

1️⃣ Click **"📑 Copy Template"** bên dưới

2️⃣ Popup "Make a copy" hiện ra

3️⃣ Đổi tên (hoặc giữ nguyên) → Click **"Make a copy"**

━━━━━━━━━━━━━━━

**✅ KẾT QUẢ:**
• Bản sao riêng trong Google Drive
• File thuộc về BẠN (100% riêng tư)

━━━━━━━━━━━━━━━

**❓ LỖI:**
• "You need access" → Đăng nhập Google
• Không copy được → Thử Chrome
• Cần trợ giúp → Group VIP

💡 **Sau khi copy xong, không đóng tab! Chuyển sang Bước 2 ngay.**
""",
        "image": "docs/make-copy.png"
    },
    
    2: {
        "title": "⚙️ BƯỚC 2: MỞ APP SCRIPT",
        "content": """
**� CÁCH LÀM:**

1️⃣ Trong file Sheets vừa copy → Menu trên cùng

2️⃣ Click **"Extensions"** (Tiện ích mở rộng)

3️⃣ Chọn **"Apps Script"**

4️⃣ Tab mới mở → Code Editor
   • Thấy file `Code.gs` với nhiều code
   • **KHÔNG CẦN ĐỌC/SỬA GÌ!**

━━━━━━━━━━━━━━━

**✅ KẾT QUẢ:**
• Đang ở Apps Script Editor
• URL dạng: `script.google.com/...`
• Sẵn sàng Deploy (Bước 3)

━━━━━━━━━━━━━━━

**❓ Không thấy Extensions?**
• Refresh trang
• Hoặc nhấn `Alt + /` → gõ "Apps Script"

💡 **Đừng sợ code! Bạn không cần động vào gì cả.**
""",
        "image": "docs/app-script.png"
    },
    
    3: {
        "title": "🚀 BƯỚC 3: DEPLOY WEB APP",
        "content": """
**� CÁCH LÀM:**

1️⃣ Apps Script Editor → Click **"Deploy"** (góc phải) → **"New deployment"**

2️⃣ Click ⚙️ → Chọn **"Web app"**

3️⃣ Cấu hình:
• **Execute as**: **"Me"**
• **Who has access**: **"Anyone"**

4️⃣ Click **"Deploy"**

5️⃣ Authorize:
→ **"Authorize access"**
→ Chọn tài khoản
→ **"Advanced"** → **"Go to... (unsafe)"** → **"Allow"**

6️⃣ Copy Web App URL → **LƯU LẠI!**

━━━━━━━━━━━━━━━

**✅ KẾT QUẢ:**
• Có Web App URL riêng
• Truy cập mọi thiết bị
• Freedom Wallet CỦA BẠN!

🎉 **Nhấn nút "Tiếp theo" để học cách sử dụng!**
""",
        "image": "docs/deploy-app.png"
    },
    
    4: {
        "title": "✅ HOÀN THÀNH: TẠO WEB APP!",
        "content": """
🎉 **XUẤT SẮC! Đã tạo xong Freedom Wallet Web App!**

━━━━━━━━━━━━━━━

**✅ HOÀN THÀNH:**
• Google Sheets Template riêng
• Web App cá nhân
• URL truy cập mọi lúc

━━━━━━━━━━━━━━━

**💡 MẸO:**

📱 **Điện thoại:** Thêm vào Home Screen
• iOS: Safari → Share → Add to Home Screen
• Android: Chrome → Menu → Add to Home screen

💻 **Máy tính:** Bookmark (Ctrl+D)

━━━━━━━━━━━━━━━

**🚀 TIẾP THEO: HỌC CÁCH DÙNG**

Trong Bước 2:
• Quản lý tài khoản & giao dịch
• Áp dụng 6 Hũ Tiền
• Đạt tự do tài chính

⏱ 15-20 phút

👉 **Nhấn nút bên dưới!**
""",
        "image": "docs/use-deploy-app.png"
    }
}


def get_webapp_setup_keyboard(current_step: int) -> InlineKeyboardMarkup:
    """Generate navigation keyboard for webapp setup guide"""
    buttons = []
    
    # Special handling for step 1 - add Copy Template button
    if current_step == 1:
        buttons.append([
            InlineKeyboardButton(
                "📑 Copy Template", 
                url=f"https://docs.google.com/spreadsheets/d/{os.getenv('TEMPLATE_SPREADSHEET_ID', '1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg')}/copy"
            )
        ])
    
    # Navigation row
    nav_row = []
    if current_step > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Quay lại", callback_data=f"webapp_step_{current_step-1}"))
    
    if current_step < 4:
        nav_row.append(InlineKeyboardButton("Tiếp theo ➡️", callback_data=f"webapp_step_{current_step+1}"))
    
    if nav_row:
        buttons.append(nav_row)
    
    # Menu row
    menu_row = []
    if current_step != 0:
        menu_row.append(InlineKeyboardButton("📱 Menu", callback_data="webapp_step_0"))
    
    # Step 4 (completion) - add special buttons
    if current_step == 4:
        buttons.append([
            InlineKeyboardButton("📘 Tiếp theo: Hướng dẫn sử dụng ➡️", callback_data="guide_step_0")
        ])
        buttons.append([
            InlineKeyboardButton("💬 Cần trợ giúp?", url="https://t.me/freedomwalletapp")
        ])
    else:
        # Help row (for steps 0-3)
        if menu_row:
            buttons.append(menu_row)
        buttons.append([
            InlineKeyboardButton("💬 Cần trợ giúp?", url="https://t.me/freedomwalletapp")
        ])
    
    return InlineKeyboardMarkup(buttons)


async def send_webapp_setup_step(update: Update, context: ContextTypes.DEFAULT_TYPE, step: int):
    """Send a specific webapp setup step"""
    try:
        if step not in WEBAPP_SETUP_STEPS:
            await update.callback_query.answer("❌ Bước không hợp lệ!")
            return
        
        step_data = WEBAPP_SETUP_STEPS[step]
        keyboard = get_webapp_setup_keyboard(step)
        
        message_text = f"{step_data['title']}\n\n{step_data['content']}"
        
        # Handle image + text combination
        if step_data.get('image'):
            # If there's an image, we need to delete old message and send new photo message
            if update.callback_query:
                # Delete the old message
                await update.callback_query.message.delete()
                
                # Send new photo message
                with open(step_data['image'], 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=photo,
                        caption=message_text,
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
                await update.callback_query.answer()
            else:
                # Command: send photo directly
                with open(step_data['image'], 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=message_text,
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
        else:
            # No image, just text
            if update.callback_query:
                # Check if previous message was a photo
                if update.callback_query.message.photo:
                    # Previous was photo, need to delete and send new text message
                    await update.callback_query.message.delete()
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=message_text,
                        parse_mode="Markdown",
                        reply_markup=keyboard,
                        disable_web_page_preview=True
                    )
                    await update.callback_query.answer()
                else:
                    # Previous was text, can edit
                    await update.callback_query.edit_message_text(
                        text=message_text,
                        parse_mode="Markdown",
                        reply_markup=keyboard,
                        disable_web_page_preview=True
                    )
                    await update.callback_query.answer()
            else:
                await update.message.reply_text(
                    text=message_text,
                    parse_mode="Markdown",
                    reply_markup=keyboard,
                    disable_web_page_preview=True
                )
        
        logger.info(f"Sent webapp setup step {step} to user {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error sending webapp setup step {step}: {e}")
        if update.callback_query:
            await update.callback_query.answer("❌ Có lỗi xảy ra!")


async def taoweb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /taoweb command"""
    await send_webapp_setup_step(update, context, step=0)


async def webapp_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle webapp setup navigation callbacks"""
    query = update.callback_query
    callback_data = query.data
    
    try:
        if callback_data.startswith("webapp_step_"):
            step = int(callback_data.split("_")[-1])
            await send_webapp_setup_step(update, context, step)
        
    except Exception as e:
        logger.error(f"Error in webapp callback handler: {e}")
        await query.answer("❌ Có lỗi xảy ra!")


def register_webapp_setup_handlers(application):
    """Register all webapp setup handlers"""
    application.add_handler(CommandHandler("taoweb", taoweb_command))
    application.add_handler(CallbackQueryHandler(webapp_callback_handler, pattern="^webapp_"))
    
    logger.info("✅ Web App setup handlers registered")
