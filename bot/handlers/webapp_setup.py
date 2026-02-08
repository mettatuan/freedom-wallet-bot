"""
Web App Setup Guide Handler - 3-step guide to create Freedom Wallet Web App
Based on Huong_dan_tao_wepapp.html

Must be completed BEFORE using the app
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from loguru import logger

# Web App Setup Guide Content - 3 Steps
WEBAPP_SETUP_STEPS = {
    0: {
        "title": "🚀 HƯỚNG DẪN TẠO WEB APP",
        "content": """
👋 **Chào mừng! Hãy bắt đầu tạo Freedom Wallet của bạn!**

━━━━━━━━━━━━━━━━━━━━━

**🎯 BẠN SẼ LÀM GÌ?**

Trong 10-15 phút tới, bạn sẽ:
1️⃣ Tạo bản sao Google Sheets Template
2️⃣ Mở Extensions → App Script
3️⃣ Deploy Web App của riêng bạn

━━━━━━━━━━━━━━━━━━━━━

**✅ SAU KHI HOÀN THÀNH:**
• Bạn có Web App cá nhân
• Chạy trên Google Sheets của bạn
• Dữ liệu 100% riêng tư
• Không cần biết code

━━━━━━━━━━━━━━━━━━━━━

**⏱ THỜI GIAN**: 10-15 phút
**📱 THIẾT BỊ**: Desktop/Laptop (khuyến nghị)
**🔗 CẦN**: Tài khoản Google

💡 *Làm chậm cũng hoàn toàn ổn. Có Group VIP hỗ trợ nếu cần!*
""",
        "image": None
    },
    
    1: {
        "title": "📋 BƯỚC 1: TẠO BẢN SAO TEMPLATE",
        "content": """
**👉 Mục tiêu: Copy Google Sheets Template về tài khoản của bạn**

━━━━━━━━━━━━━━━━━━━━━

**🔗 CÁCH LÀM:**

1️⃣ Click nút **"📑 Copy Template"** bên dưới
   → Hoặc dùng link này: 
   https://docs.google.com/spreadsheets/d/1dV-KAVxxtbrmp79RPKSfEygFOdamcvlTj6adlHKAq78/copy

2️⃣ Google Sheets sẽ mở → Hiện popup **"Make a copy"**

3️⃣ Đổi tên (nếu muốn):
   • Ví dụ: "Freedom Wallet - [Tên bạn]"
   • Hoặc giữ nguyên "Copy of Freedom Wallet v3.2"

4️⃣ Click nút **"Make a copy"**

━━━━━━━━━━━━━━━━━━━━━

**✅ KẾT QUẢ:**
• Bạn có 1 bản sao riêng trong Google Drive
• File này thuộc về BẠN (không ai khác xem được)

━━━━━━━━━━━━━━━━━━━━━

**❓ NẾU GẶP LỖI:**
• "You need access": Đảm bảo đã đăng nhập Google
• File không copy được: Thử trình duyệt khác (Chrome)
• Hỏi trong Group VIP nếu vẫn không được

💡 **Sau khi copy xong, không đóng tab này!** Chuyển sang Bước 2 ngay.
""",
        "image": None
    },
    
    2: {
        "title": "⚙️ BƯỚC 2: MỞ APP SCRIPT",
        "content": """
**👉 Mục tiêu: Truy cập code editor của Web App**

━━━━━━━━━━━━━━━━━━━━━

**🔗 CÁCH LÀM:**

1️⃣ Trong file Google Sheets vừa copy:
   → Nhìn lên menu trên cùng

2️⃣ Click **"Extensions"** (hoặc "Tiện ích mở rộng")

3️⃣ Chọn **"Apps Script"**

4️⃣ Tab mới mở ra → Đây là Code Editor
   • Bạn sẽ thấy file `Code.gs`
   • Có rất nhiều dòng code màu xanh/đỏ
   • **KHÔNG CẦN ĐỌC/SỬA GÌ CẢ!**

━━━━━━━━━━━━━━━━━━━━━

**✅ KẾT QUẢ:**
• Bạn đang ở Apps Script Editor
• Tab có URL dạng: `script.google.com/...`
• Sẵn sàng cho Bước 3 (Deploy)

━━━━━━━━━━━━━━━━━━━━━

**❓ NẾU KHÔNG THẤY "EXTENSIONS":**
• Thử refresh lại trang
• Hoặc nhấn `Alt + /` (Windows) hoặc `Option + /` (Mac)
• Gõ "Apps Script" vào search box

💡 **Lưu ý**: Đừng sợ code! Bạn không cần động vào gì cả.
""",
        "image": None
    },
    
    3: {
        "title": "🚀 BƯỚC 3: DEPLOY WEB APP",
        "content": """
**👉 Mục tiêu: Tạo Web App link để sử dụng trên điện thoại/máy tính**

━━━━━━━━━━━━━━━━━━━━━

**🔗 CÁCH LÀM:**

1️⃣ Trong Apps Script Editor:
   → Nhìn góc trên bên phải
   → Click nút **"Deploy"** (màu xanh)
   → Chọn **"New deployment"**

2️⃣ Popup hiện ra:
   → Click icon ⚙️ (settings/gear) bên cạnh "Select type"
   → Chọn **"Web app"**

3️⃣ Cấu hình deployment:
   • **Description**: "Freedom Wallet v1" (hoặc để trống)
   • **Execute as**: **"Me"** (quan trọng!)
   • **Who has access**: **"Anyone"** hoặc "Anyone with Google account"

4️⃣ Click **"Deploy"**

5️⃣ Google sẽ yêu cầu permission:
   → Click **"Authorize access"**
   → Chọn tài khoản Google của bạn
   → Click **"Advanced"** → **"Go to [Project name] (unsafe)"**
   → Click **"Allow"**

6️⃣ Nhận Web App URL:
   → Copy link dạng: `https://script.google.com/macros/s/.../exec`
   → **LƯU LINK NÀY LẠI!** (bookmark hoặc save vào Note)

━━━━━━━━━━━━━━━━━━━━━

**✅ KẾT QUẢ:**
• Bạn có Web App URL riêng
• Mở link này trên bất kỳ thiết bị nào
• Đây là Freedom Wallet CỦA BẠN!

━━━━━━━━━━━━━━━━━━━━━

**🎉 CHÚC MỪNG!**
Bạn đã hoàn thành setup! 

**🔜 BƯỚC TIẾP THEO:**
→ Nhấn nút **"📘 Hướng dẫn sử dụng"** để học cách dùng app
→ Hoặc bắt đầu ghi chép giao dịch đầu tiên ngay!
""",
        "image": None
    },
    
    4: {
        "title": "✅ HOÀN THÀNH SETUP!",
        "content": """
🎉 **CHÚC MỪNG BẠN ĐÃ TẠO XONG WEB APP!**

━━━━━━━━━━━━━━━━━━━━━

**🎯 BẠN ĐÃ CÓ:**
✅ Google Sheets Template riêng
✅ Web App URL cá nhân
✅ Quyền truy cập 100% của bạn

━━━━━━━━━━━━━━━━━━━━━

**💡 MẸO SỬ DỤNG:**

📱 **Trên điện thoại:**
• Thêm Web App URL vào Home Screen
• iOS: Safari → Share → Add to Home Screen
• Android: Chrome → Menu → Add to Home screen

💻 **Trên máy tính:**
• Bookmark Web App URL
• Hoặc pin tab trong Chrome

━━━━━━━━━━━━━━━━━━━━━

**🔜 BƯỚC TIẾP THEO:**

1️⃣ **Xem hướng dẫn sử dụng** (8 bước chi tiết)
   → Learn: Tài khoản, giao dịch, danh mục, 6 Hũ Tiền...

2️⃣ **Bắt đầu ghi chép** 
   → Mở Web App → Thêm tài khoản đầu tiên
   → Ghi 1 giao dịch test

3️⃣ **Tham gia Group VIP**
   → Hỏi đáp, chia sẻ kinh nghiệm
   → Tips & tricks từ cộng đồng

━━━━━━━━━━━━━━━━━━━━━

**🎁 BONUS:**
Mời thêm bạn bè → Unlock tính năng Premium!
""",
        "image": None
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
                url="https://docs.google.com/spreadsheets/d/1dV-KAVxxtbrmp79RPKSfEygFOdamcvlTj6adlHKAq78/copy"
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
            InlineKeyboardButton("📘 Hướng dẫn sử dụng", callback_data="guide_step_0")
        ])
        buttons.append([
            InlineKeyboardButton("👥 Tham gia Group VIP", url="https://t.me/freedomwalletapp")
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
        
        # Edit existing message if this is a callback query
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=message_text,
                parse_mode="Markdown",
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
            await update.callback_query.answer()
        else:
            # Send new message if this is a command
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
