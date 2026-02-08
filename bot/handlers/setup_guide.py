"""
Setup Guide Handler - Step-by-step Web App setup guide
Based on BROCHURE_Huong_dan_su_dung.html

Provides interactive 8-step tutorial for Freedom Wallet usage
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from loguru import logger

# Setup Guide Content - 8 Steps
SETUP_GUIDE_STEPS = {
    0: {
        "title": "📘 BƯỚC 2: HƯỚNG DẪN SỬ DỤNG",
        "content": """
🎉 **Tuyệt vời! Bạn đã hoàn thành Bước 1!**

━━━━━━━━━━━━━━━━━━━━━

**📍 BẠN ĐANG Ở ĐÂU?**

✅ Bước 1: Tạo Web App (hoàn thành)
➡️ **BƯỚC 2: Học cách sử dụng** (bạn đang ở đây)

━━━━━━━━━━━━━━━━━━━━━

**🎯 BƯỚC 2 - BẠN SẼ HỌC GÌ?**

Trong **8 phần** sau, bạn sẽ làm chủ Freedom Wallet:

1️⃣ Cài đặt & làm sạch dữ liệu
2️⃣ Thêm tài khoản (Accounts)
3️⃣ Ghi chép giao dịch (Transactions)
4️⃣ Quản lý danh mục (Categories)
5️⃣ Quản lý khoản nợ (Debts)
6️⃣ Ghi nhận tài sản (Assets)
7️⃣ Theo dõi đầu tư (Investments)
8️⃣ 6 Hũ Tiền - Trái tim Freedom Wallet

━━━━━━━━━━━━━━━━━━━━━

⏱ **Thời gian**: 15-20 phút
🎯 **Mục tiêu**: Hiểu & sử dụng thành thạo

💡 *Có thể xem lại bất kỳ lúc nào bằng /huongdan*
""",
        "image": None
    },
    
    1: {
        "title": "🟦 BƯỚC 1 – BẮT ĐẦU (SETUP BAN ĐẦU)",
        "content": """
**👉 Mục tiêu: Chuẩn bị app "trắng", đúng với tài chính thực tế của bạn.**

━━━━━━━━━━━━━━━━━━━━━

**📋 THAO TÁC:**

1️⃣ Vào **Cài đặt** (Settings)
2️⃣ Chọn **Xóa dữ liệu mẫu** (nếu là lần đầu dùng)
3️⃣ Đổi **mật khẩu** (nếu cần) để bảo mật

━━━━━━━━━━━━━━━━━━━━━

**✅ KẾT QUẢ:**
• App sẵn sàng cho dữ liệu thật
• An toàn & cá nhân hóa

━━━━━━━━━━━━━━━━━━━━━

**💡 Nguyên tắc:**
*"Dữ liệu càng thật → Quyết định tài chính càng đúng"*
""",
        "image": None
    },
    
    2: {
        "title": "🟦 BƯỚC 2 – TÀI KHOẢN (ACCOUNTS)",
        "content": """
**👉 Mục tiêu: Biết tiền của bạn đang nằm ở đâu.**

━━━━━━━━━━━━━━━━━━━━━

**📌 VÍ DỤ TÀI KHOẢN:**
• Tiền mặt
• Tài khoản ngân hàng (VCB, TCB, MB...)
• Ví điện tử (Momo, ZaloPay, VNPay...)

━━━━━━━━━━━━━━━━━━━━━

**📋 THAO TÁC:**
➕ Thêm tài khoản mới
✏️ Sửa số dư ban đầu
🗑️ Xóa tài khoản không dùng

━━━━━━━━━━━━━━━━━━━━━

**✅ KẾT QUẢ:**
• Tổng tiền hiển thị chính xác
• Là nền tảng cho mọi báo cáo sau này

━━━━━━━━━━━━━━━━━━━━━

**💡 Lưu ý:**
Số dư ban đầu phải khớp với số dư thực tế để tracking chính xác!
""",
        "image": None
    },
    
    3: {
        "title": "🟦 BƯỚC 3 – GIAO DỊCH (TRANSACTIONS)",
        "content": """
**👉 Mục tiêu: Kiểm soát dòng tiền vào – ra mỗi ngày.**

━━━━━━━━━━━━━━━━━━━━━

**📊 3 LOẠI GIAO DỊCH:**
💰 **Thu nhập** (Income) – Tiền vào
💸 **Chi tiêu** (Expense) – Tiền ra
🔁 **Chuyển tiền** (Transfer) – Nội bộ giữa các tài khoản

━━━━━━━━━━━━━━━━━━━━━

**📝 MỖI GIAO DỊCH GỒM:**
• Ngày (Date)
• Số tiền (Amount)
• Tài khoản (Account)
• Danh mục (Category)
• Ghi chú (Note)

━━━━━━━━━━━━━━━━━━━━━

**✅ KẾT QUẢ:**
• Biết tiền đi đâu, về đâu
• Chấm dứt "không hiểu vì sao hết tiền"

━━━━━━━━━━━━━━━━━━━━━

**💡 Habit vàng:**
Ghi chép NGAY sau mỗi giao dịch (trong 5 phút)
""",
        "image": None
    },
    
    4: {
        "title": "🟦 BƯỚC 4 – DANH MỤC (CATEGORIES)",
        "content": """
**👉 Mục tiêu: Hiểu thói quen chi tiêu của bạn.**

━━━━━━━━━━━━━━━━━━━━━

**📂 VÍ DỤ DANH MỤC:**

**Chi tiêu (Expenses):**
• 🍜 Ăn uống
• 🏠 Nhà ở
• 🎓 Giáo dục
• 🎉 Giải trí
• 🚗 Di chuyển
• 👨‍⚕️ Sức khỏe

**Thu nhập (Income):**
• 💼 Lương
• 💰 Kinh doanh
• 🎁 Quà tặng

━━━━━━━━━━━━━━━━━━━━━

**📋 THAO TÁC:**
• Thêm / sửa / xóa danh mục
• Gán danh mục cho giao dịch

━━━━━━━━━━━━━━━━━━━━━

**✅ KẾT QUẢ:**
• Báo cáo chi tiêu rõ ràng
• Nhận diện "lỗ hổng tài chính"
""",
        "image": None
    },
    
    5: {
        "title": "🟦 BƯỚC 5 – KHOẢN NỢ (DEBTS)",
        "content": """
**👉 Mục tiêu: Không né tránh – chủ động làm chủ nợ.**

━━━━━━━━━━━━━━━━━━━━━

**💳 CÓ THỂ QUẢN LÝ:**
• Nợ vay ngân hàng
• Trả góp (xe, nhà, điện thoại...)
• Nợ cá nhân (bạn bè, gia đình)
• Thẻ tín dụng

━━━━━━━━━━━━━━━━━━━━━

**📊 THEO DÕI:**
• Số tiền gốc
• Lãi suất
• Tiến độ trả nợ
• Thời hạn còn lại

━━━━━━━━━━━━━━━━━━━━━

**✅ KẾT QUẢ:**
• Biết chính xác mình đang nợ bao nhiêu
• Có chiến lược thoát nợ rõ ràng
• Giảm stress về tài chính

━━━━━━━━━━━━━━━━━━━━━

**💡 Mindset:**
*"Nợ không phải kẻ thù – việc không biết mình nợ bao nhiêu mới là kẻ thù"*
""",
        "image": None
    },
    
    6: {
        "title": "🟦 BƯỚC 6 – TÀI SẢN (ASSETS)",
        "content": """
**👉 Mục tiêu: Nhìn thấy giá trị ròng thực sự của bạn.**

━━━━━━━━━━━━━━━━━━━━━

**🏠 VÍ DỤ TÀI SẢN:**
• Nhà đất
• Xe (ô tô, xe máy)
• Trang sức, vàng
• Đồ điện tử giá trị cao
• Tài sản khác (tranh, đồ cổ...)

━━━━━━━━━━━━━━━━━━━━━

**📊 THEO DÕI:**
• Giá trị mua ban đầu
• Giá trị hiện tại
• Tăng / giảm theo thời gian
• Ghi chú & hình ảnh

━━━━━━━━━━━━━━━━━━━━━

**✅ KẾT QUẢ:**
• Biết bạn "giàu" hay "nghèo" thật sự
• Không nhầm lẫn giữa thu nhập và tài sản
• Tính được **Net Worth** (Tài sản ròng)

━━━━━━━━━━━━━━━━━━━━━

**💡 Công thức:**
*Net Worth = Tài sản - Nợ*
""",
        "image": None
    },
    
    7: {
        "title": "🟦 BƯỚC 7 – ĐẦU TƯ (INVESTMENTS)",
        "content": """
**👉 Mục tiêu: Để tiền làm việc cho bạn.**

━━━━━━━━━━━━━━━━━━━━━

**📈 CÓ THỂ THEO DÕI:**
• Chứng khoán (Cổ phiếu, Quỹ đầu tư)
• Vàng
• Bất động sản cho thuê
• Kinh doanh (startup, side business)
• Tiền mã hóa (Bitcoin, Ethereum...)
• Các khoản đầu tư khác

━━━━━━━━━━━━━━━━━━━━━

**📊 XEM ĐƯỢC:**
• Vốn đầu tư
• Giá trị hiện tại
• Lãi / lỗ
• Tỷ suất sinh lời (ROI)

━━━━━━━━━━━━━━━━━━━━━

**✅ KẾT QUẢ:**
• Đầu tư có kỷ luật
• Quyết định dựa trên số liệu, không cảm xúc
• Theo dõi performance của portfolio

━━━━━━━━━━━━━━━━━━━━━

**💡 Lưu ý:**
Đây chỉ là công cụ tracking – không phải tư vấn đầu tư!
""",
        "image": None
    },
    
    8: {
        "title": "🟦 BƯỚC 8 – 6 HŨ TIỀN (Trái tim Freedom Wallet)",
        "content": """
**👉 Mục tiêu: Phân bổ tiền cân bằng – bền vững – tự do.**

━━━━━━━━━━━━━━━━━━━━━

**🎯 6 HŨ TIÊU CHUẨN:**

1️⃣ **🏠 Chi tiêu thiết yếu** (55%)
   → Ăn uống, nhà ở, điện nước

2️⃣ **🎉 Hưởng thụ** (10%)
   → Cafe, shopping, giải trí

3️⃣ **🎓 Giáo dục** (10%)
   → Sách, khóa học, phát triển bản thân

4️⃣ **💰 Tiết kiệm dài hạn** (10%)
   → Mua nhà, xe, tài sản lớn

5️⃣ **💼 Đầu tư** (10%)
   → Chứng khoán, BĐS, kinh doanh

6️⃣ **❤️ Cho đi** (5%)
   → Từ thiện, giúp đỡ người khác

━━━━━━━━━━━━━━━━━━━━━

**⚙️ CÁCH DÙNG:**
• Mỗi khoản thu → tự động phân bổ
• Theo dõi số dư từng hũ
• Chi tiêu đúng từ hũ tương ứng

━━━━━━━━━━━━━━━━━━━━━

**✅ KẾT QUẢ:**
• Tiêu tiền không tội lỗi
• Vừa sống tốt – vừa giàu lên
• Đạt tự do tài chính bền vững
""",
        "image": None
    },
    
    9: {
        "title": "🎯 KẾT LUẬN – CÁCH DÙNG TỐI ƯU",
        "content": """
**🏆 NGUYÊN TẮC VÀNG KHI DÙNG FREEDOM WALLET:**

━━━━━━━━━━━━━━━━━━━━━

1️⃣ **Ghi chép HÀNG NGÀY**
   → Mỗi giao dịch phải được ghi lại

2️⃣ **Xem báo cáo HÀNG TUẦN**
   → Kiểm tra chi tiêu, điều chỉnh kịp thời

3️⃣ **Đánh giá tài chính MỖI THÁNG**
   → Xem tổng quan, so sánh với tháng trước

4️⃣ **Điều chỉnh mục tiêu MỖI QUÝ**
   → Thay đổi % 6 hũ nếu cần

5️⃣ **Kiên trì ÍT NHẤT 90 NGÀY**
   → Đủ để hình thành thói quen

━━━━━━━━━━━━━━━━━━━━━

**🌱 Câu nói cuối:**

*"Tự do tài chính không đến từ may mắn*
*– mà đến từ hệ thống."*

━━━━━━━━━━━━━━━━━━━━━

🎉 **Chúc bạn thành công trên hành trình tự do tài chính!**
""",
        "image": None
    }
}


def get_setup_guide_keyboard(current_step: int) -> InlineKeyboardMarkup:
    """Generate navigation keyboard for setup guide"""
    buttons = []
    
    # Navigation row
    nav_row = []
    if current_step > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Quay lại", callback_data=f"guide_step_{current_step-1}"))
    
    if current_step < 9:
        nav_row.append(InlineKeyboardButton("Tiếp theo ➡️", callback_data=f"guide_step_{current_step+1}"))
    
    if nav_row:
        buttons.append(nav_row)
    
    # Jump to specific sections (only show on step 0)
    if current_step == 0:
        buttons.append([
            InlineKeyboardButton("📋 Bước 1-4", callback_data="guide_step_1"),
            InlineKeyboardButton("📊 Bước 5-8", callback_data="guide_step_5")
        ])
    
    # Menu row
    menu_row = []
    if current_step != 0:
        menu_row.append(InlineKeyboardButton("📘 Menu", callback_data="guide_step_0"))
    
    if current_step == 9:
        menu_row.append(InlineKeyboardButton("✅ Hoàn thành", callback_data="guide_complete"))
    
    if menu_row:
        buttons.append(menu_row)
    
    # Help row (always available)
    buttons.append([
        InlineKeyboardButton("💬 Cần trợ giúp?", url="https://t.me/freedomwalletapp")
    ])
    
    return InlineKeyboardMarkup(buttons)


async def send_guide_step(update: Update, context: ContextTypes.DEFAULT_TYPE, step: int):
    """Send a specific guide step"""
    try:
        if step not in SETUP_GUIDE_STEPS:
            await update.callback_query.answer("❌ Bước không hợp lệ!")
            return
        
        guide_data = SETUP_GUIDE_STEPS[step]
        keyboard = get_setup_guide_keyboard(step)
        
        message_text = f"{guide_data['title']}\n\n{guide_data['content']}"
        
        # Edit existing message if this is a callback query
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=message_text,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            await update.callback_query.answer()
        else:
            # Send new message if this is a command
            await update.message.reply_text(
                text=message_text,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        
        logger.info(f"Sent guide step {step} to user {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error sending guide step {step}: {e}")
        if update.callback_query:
            await update.callback_query.answer("❌ Có lỗi xảy ra!")


async def huongdan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /huongdan command"""
    await send_guide_step(update, context, step=0)


async def guide_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle guide navigation callbacks"""
    query = update.callback_query
    callback_data = query.data
    
    try:
        if callback_data.startswith("guide_step_"):
            step = int(callback_data.split("_")[-1])
            await send_guide_step(update, context, step)
        
        elif callback_data == "guide_complete":
            await query.edit_message_text(
                text="✅ **Hoàn thành hướng dẫn!**\n\n"
                     "Bạn đã hoàn thành 8 bước hướng dẫn Freedom Wallet.\n\n"
                     "🎯 **Bước tiếp theo:**\n"
                     "1. Mở Web App của bạn\n"
                     "2. Bắt đầu ghi chép giao dịch đầu tiên\n"
                     "3. Thiết lập 6 Hũ Tiền\n\n"
                     "💬 Cần hỗ trợ? → /help hoặc vào Group VIP\n\n"
                     "🔄 Xem lại hướng dẫn? → /huongdan",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("📖 Xem lại hướng dẫn", callback_data="guide_step_0")
                ], [
                    InlineKeyboardButton("👥 Tham gia Group VIP", url="https://t.me/freedomwalletapp")
                ]])
            )
            await query.answer("🎉 Chúc mừng bạn!")
        
    except Exception as e:
        logger.error(f"Error in guide callback handler: {e}")
        await query.answer("❌ Có lỗi xảy ra!")


def register_setup_guide_handlers(application):
    """Register all setup guide handlers"""
    application.add_handler(CommandHandler("huongdan", huongdan_command))
    application.add_handler(CallbackQueryHandler(guide_callback_handler, pattern="^guide_"))
    
    logger.info("✅ Setup guide handlers registered")
