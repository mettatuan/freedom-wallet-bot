"""
7-Day Nurture Campaign Messages

Messages for NURTURE_7_DAY program (new registered users with 0-1 referrals).
Used by: app.services.program_manager, app.handlers.engagement.daily_nurture
"""

NURTURE_MESSAGES = {
    1: {
        "title": "📅 DAY 1 – VÌ SAO CẦN QUẢN LÝ TÀI CHÍNH?",
        "content": (
            "❓ **Bạn có biết?**\n\n"
            "**90% người đi làm** không biết tiền của mình đang đi đâu mỗi tháng\n\n"
            "Quản lý tài chính **không phải** để tiết kiệm cực khổ, mà để:\n"
            "✓ **An tâm hơn**\n"
            "✓ **Chủ động hơn**\n"
            "✓ **Không bị tiền chi phối cảm xúc**\n\n"
            "👉 Freedom Wallet giúp bạn nhìn thấy **toàn bộ bức tranh tài chính**"
        ),
        "delay_hours": 24  # Gửi sau 24h đăng ký
    },
    2: {
        "title": "📅 DAY 2 – CÁI GIÁ CỦA VIỆC KHÔNG QUẢN LÝ TIỀN",
        "content": (
            "💥 **Không quản lý tài chính dẫn đến:**\n\n"
            "❌ Làm nhiều nhưng không dư\n"
            "❌ Có tiền vẫn lo\n"
            "❌ Không dám đầu tư dài hạn\n\n"
            "👉 **Quản lý tiền = kiểm soát cuộc sống**\n\n"
            "🔗 Chia sẻ để mở khóa bộ công cụ trọn đời"
        ),
        "delay_hours": 48
    },
    3: {
        "title": "📅 DAY 3 – 6 HŨ TIỀN & 5 CẤP BẬC TÀI CHÍNH",
        "content": (
            "🧠 **Freedom Wallet áp dụng:**\n\n"
            "💰 **6 Hũ Tiền:** phân bổ dòng tiền khoa học\n"
            "• 55% Chi tiêu thiết yếu (NEC)\n"
            "• 10% Tự do tài chính (FFA)\n"
            "• 10% Giáo dục (EDU)\n"
            "• 10% Tiết kiệm dài hạn (LTSS)\n"
            "• 10% Hưởng thụ (PLAY)\n"
            "• 5% Cho đi (GIVE)\n\n"
            "📊 **5 Cấp Bậc Tài Chính:** biết bạn đang ở đâu & đi về đâu\n\n"
            "👉 Không học lý thuyết suông – **áp dụng ngay**"
        ),
        "delay_hours": 72
    },
    4: {
        "title": "📅 DAY 4 – VÌ SAO CHÚNG TÔI TẶNG QUÀ?",
        "content": (
            "🎁 **Vì chúng tôi tin rằng:**\n\n"
            "✅ Người dùng tốt nhất → là người **giới thiệu người tốt**\n"
            "✅ Chia sẻ giá trị → tạo **cộng đồng chất lượng**\n"
            "✅ Giúp nhau → cùng **tiến bộ**\n\n"
            "👉 **Bạn giúp 2 người – bạn nhận hệ thống trọn đời**\n\n"
            "Đơn giản vậy thôi! 💙"
        ),
        "delay_hours": 96
    },
    5: {
        "title": "📅 DAY 5 – NHẮC NHẸ + TẠO CẤP BÁCH",
        "content": (
            "⏳ **Bộ quà chỉ dành cho người hoàn thành đủ 2 lượt giới thiệu**\n\n"
            "Hàng ngàn người đã nhận được:\n"
            "✅ Google Sheet Template\n"
            "✅ Apps Script tự động hóa\n"
            "✅ Hướng dẫn đầy đủ\n"
            "✅ Hỗ trợ 1-1\n\n"
            "👉 **Chỉ còn thiếu bạn!**"
        ),
        "delay_hours": 120
    }
}
