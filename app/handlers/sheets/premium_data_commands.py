"""
Premium AI Commands - Use Google Sheets data
Commands that leverage user's financial data for analysis
"""
from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger
from app.services.sheets_reader import get_user_sheets_reader
from app.core.subscription import SubscriptionManager, SubscriptionTier
from app.utils.database import get_user_by_id
from app.services.analytics import Analytics


async def handle_balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /balance - Show balance summary from Google Sheets
    Premium/Trial only
    """
    user_id = update.effective_user.id
    user = await get_user_by_id(user_id)
    tier = SubscriptionManager.get_user_tier(user)
    
    # Check Premium
    if tier not in [SubscriptionTier.PREMIUM, SubscriptionTier.TRIAL]:
        await update.message.reply_text(
            "🔒 **Tính năng Premium**\n\n"
            "Xem số dư realtime từ Google Sheets chỉ dành cho Premium/Trial.\n\n"
            "🎁 Dùng thử 7 ngày FREE: /start"
        )
        return
    
    # Check if Sheets connected
    sheets = await get_user_sheets_reader(user_id)
    if not sheets:
        await update.message.reply_text(
            "📊 **Chưa kết nối Google Sheets**\n\n"
            "Để xem số dư tự động, hãy kết nối Sheets của bạn:\n"
            "/connectsheets"
        )
        return
    
    await update.message.reply_text("🔄 Đang đọc dữ liệu từ Google Sheets...")
    
    try:
        # Get balance
        jars = await sheets.get_balance_summary()
        total = await sheets.get_total_balance()
        
        if not jars or total is None:
            await update.message.reply_text(
                "❌ Không thể đọc dữ liệu!\n\n"
                "Kiểm tra:\n"
                "• Google Sheets có data chưa?\n"
                "• Cấu trúc sheet đúng format chưa?"
            )
            return
        
        # Format message
        message = f"""
💰 **SỐ DƯ HIỆN TẠI**

━━━━━━━━━━━━━━━━━━━━━
**📊 TỔNG TÀI SẢN**
━━━━━━━━━━━━━━━━━━━━━

{total:,.0f} VNĐ

━━━━━━━━━━━━━━━━━━━━━
**🏺 CHI TIẾT 6 HŨ**
━━━━━━━━━━━━━━━━━━━━━

"""
        
        # Add each jar
        for jar_name, amount in jars.items():
            percentage = (amount / total * 100) if total > 0 else 0
            bar = "â–ˆ" * int(percentage / 5)  # 20 bars max
            message += f"{jar_name}:\n{amount:,.0f} VNĐ ({percentage:.1f}%)\n{bar}\n\n"
        
        message += "📱 Update: Vừa xong\n🔄 Refresh: /balance"
        
        await update.message.reply_text(message, parse_mode="Markdown")
        
        # Track usage
        Analytics.track_event(user_id, 'balance_viewed', {
            'total_balance': total,
            'num_jars': len(jars)
        })
        
        logger.info(f"User {user_id} viewed balance: {total:,.0f}")
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Lỗi đọc dữ liệu!\n\n"
            f"Chi tiết: {str(e)}\n\n"
            f"Liên hệ /support nếu vấn đề tiếp diễn."
        )
        logger.error(f"Balance command error for user {user_id}: {e}")


async def handle_spending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /spending - Show monthly spending analysis
    Premium/Trial only
    """
    user_id = update.effective_user.id
    user = await get_user_by_id(user_id)
    tier = SubscriptionManager.get_user_tier(user)
    
    # Check Premium
    if tier not in [SubscriptionTier.PREMIUM, SubscriptionTier.TRIAL]:
        await update.message.reply_text(
            "🔒 **Tính năng Premium**\n\n"
            "Phân tích chi tiêu chỉ dành cho Premium/Trial.\n\n"
            "🎁 Dùng thử 7 ngày FREE: /start"
        )
        return
    
    # Check if Sheets connected
    sheets = await get_user_sheets_reader(user_id)
    if not sheets:
        await update.message.reply_text(
            "📊 **Chưa kết nối Google Sheets**\n\n"
            "Để phân tích chi tiêu, hãy kết nối Sheets:\n"
            "/connectsheets"
        )
        return
    
    await update.message.reply_text("📊 Đang phân tích chi tiêu tháng này...")
    
    try:
        from datetime import date
        today = date.today()
        
        # Get monthly spending
        spending = await sheets.get_monthly_spending(today.year, today.month)
        
        if not spending:
            await update.message.reply_text(
                "ℹ️ **Chưa có dữ liệu chi tiêu tháng này!**\n\n"
                "Hãy bắt đầu ghi chi tiêu vào Google Sheets."
            )
            return
        
        # Calculate total
        total_spending = sum(spending.values())
        
        # Sort by amount (descending)
        sorted_spending = sorted(spending.items(), key=lambda x: x[1], reverse=True)
        
        # Format message
        message = f"""
📊 **CHI TIÊU THÁNG {today.month}/{today.year}**

━━━━━━━━━━━━━━━━━━━━━
**💸 TỔNG CHI TIÊU**
━━━━━━━━━━━━━━━━━━━━━

{total_spending:,.0f} VNĐ

━━━━━━━━━━━━━━━━━━━━━
**📈 TOP 5 HẠNG MỤC**
━━━━━━━━━━━━━━━━━━━━━

"""
        
        # Add top 5 categories
        for i, (category, amount) in enumerate(sorted_spending[:5], 1):
            percentage = (amount / total_spending * 100) if total_spending > 0 else 0
            emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i-1]
            message += f"{emoji} **{category}**\n   {amount:,.0f} VNĐ ({percentage:.1f}%)\n\n"
        
        # Add insights
        message += "━━━━━━━━━━━━━━━━━━━━━\n"
        message += "💡 **INSIGHTS**\n"
        message += "━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        top_category = sorted_spending[0][0]
        top_amount = sorted_spending[0][1]
        top_pct = (top_amount / total_spending * 100)
        
        message += f"• Bạn chi nhiều nhất cho **{top_category}** ({top_pct:.0f}%)\n"
        message += f"• Trung bình: {total_spending / len(spending):,.0f} VNĐ/hạng mục\n"
        
        # Days left in month
        import calendar
        last_day = calendar.monthrange(today.year, today.month)[1]
        days_left = last_day - today.day
        
        if days_left > 0:
            daily_avg = total_spending / today.day
            projected = daily_avg * last_day
            message += f"• Dự kiến cuối tháng: {projected:,.0f} VNĐ\n"
        
        message += f"\n📅 Dữ liệu: {today.day}/{today.month}/{today.year}"
        
        await update.message.reply_text(message, parse_mode="Markdown")
        
        # Track usage
        Analytics.track_event(user_id, 'spending_analyzed', {
            'total_spending': total_spending,
            'num_categories': len(spending),
            'month': f"{today.year}-{today.month:02d}"
        })
        
        logger.info(f"User {user_id} analyzed spending: {total_spending:,.0f}")
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Lỗi phân tích!\n\n"
            f"Chi tiết: {str(e)}\n\n"
            f"Liên hệ /support nếu vấn đề tiếp diễn."
        )
        logger.error(f"Spending command error for user {user_id}: {e}")


async def handle_analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /analyze - AI-powered financial analysis
    Premium only (not Trial)
    """
    user_id = update.effective_user.id
    user = await get_user_by_id(user_id)
    tier = SubscriptionManager.get_user_tier(user)
    
    # Check Premium (not Trial - this is premium-only feature)
    if tier != SubscriptionTier.PREMIUM:
        await update.message.reply_text(
            "🔒 **Tính năng Premium Exclusive**\n\n"
            "AI Financial Analysis chỉ dành cho gói Premium.\n\n"
            "💎 Nâng cấp Premium: /upgrade"
        )
        return
    
    # Check if Sheets connected
    sheets = await get_user_sheets_reader(user_id)
    if not sheets:
        await update.message.reply_text(
            "📊 **Chưa kết nối Google Sheets**\n\n"
            "AI cần data để phân tích. Hãy kết nối Sheets:\n"
            "/connectsheets"
        )
        return
    
    await update.message.reply_text("🤖 AI đang phân tích dữ liệu của bạn...")
    
    try:
        # Get all data
        jars = await sheets.get_balance_summary()
        total = await sheets.get_total_balance()
        spending = await sheets.get_monthly_spending()
        transactions = await sheets.get_recent_transactions(limit=20)
        
        # TODO: Call OpenAI GPT-4 with data for analysis
        # For now, basic analysis
        
        from datetime import date
        today = date.today()
        
        message = f"""
🤖 **AI FINANCIAL ANALYSIS**

━━━━━━━━━━━━━━━━━━━━━
**📊 TỔNG QUAN**
━━━━━━━━━━━━━━━━━━━━━

💰 Tổng tài sản: {total:,.0f} VNĐ
💸 Chi tiêu tháng {today.month}: {sum(spending.values()) if spending else 0:,.0f} VNĐ
📝 Giao dịch: {len(transactions)} giao dịch gần nhất

━━━━━━━━━━━━━━━━━━━━━
**💡 INSIGHTS**
━━━━━━━━━━━━━━━━━━━━━

"""
        
        # Analyze jar distribution
        if jars:
            max_jar = max(jars.items(), key=lambda x: x[1])
            min_jar = min(jars.items(), key=lambda x: x[1])
            
            message += f"• Hũ lớn nhất: **{max_jar[0]}** ({max_jar[1]:,.0f} VNĐ)\n"
            message += f"• Hũ nhỏ nhất: **{min_jar[0]}** ({min_jar[1]:,.0f} VNĐ)\n"
        
        # Spending pattern
        if spending:
            top_cat = max(spending.items(), key=lambda x: x[1])
            message += f"• Chi nhiều nhất: **{top_cat[0]}**\n"
        
        message += f"\n━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"**🎯 KHUYẾN NGHỊ**\n"
        message += f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Simple recommendations
        message += "• Tiếp tục theo dõi chi tiêu hàng ngày\n"
        message += "• Cân bằng distribution giữa 6 hũ\n"
        message += "• Tối ưu các hạng mục chi lớn\n"
        
        message += f"\n📅 Phân tích: {today.day}/{today.month}/{today.year}"
        
        await update.message.reply_text(message, parse_mode="Markdown")
        
        # Track usage
        Analytics.track_event(user_id, 'ai_analysis_used', {
            'total_balance': total,
            'num_transactions': len(transactions)
        })
        
        logger.info(f"User {user_id} used AI analysis")
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Lỗi phân tích!\n\n"
            f"Chi tiết: {str(e)}\n\n"
            f"Liên hệ /support nếu vấn đề tiếp diễn."
        )
        logger.error(f"Analyze command error for user {user_id}: {e}")


# Register commands
def register_premium_data_commands(application):
    """Register Premium commands that use Sheets data"""
    from telegram.ext import CommandHandler
    
    application.add_handler(CommandHandler('balance', handle_balance_command))
    application.add_handler(CommandHandler('spending', handle_spending_command))
    application.add_handler(CommandHandler('analyze', handle_analyze_command))
    
    logger.info("✅ Premium data commands registered")

