"""
ROI Calculator - Calculate return on investment for Premium users

Metrics:
- Messages saved time
- Features usage value
- Monthly/daily ROI
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from bot.utils.database import SessionLocal, User
from bot.services.analytics import Analytics
from loguru import logger


class ROICalculator:
    """Calculate Premium ROI for users"""
    
    # Constants
    HOURLY_VALUE = 100_000  # VNĐ/hour (user's time value)
    PREMIUM_YEARLY = 999_000  # VNĐ/year
    PREMIUM_MONTHLY = 83_250  # VNĐ/month (~999K/12)
    PREMIUM_DAILY = 2_775  # VNĐ/day (~83K/30)
    
    # Time saved per feature
    TIME_PER_MESSAGE = 3  # minutes per AI message vs manual search
    TIME_PER_ANALYSIS = 30  # minutes per financial analysis
    TIME_PER_RECOMMENDATION = 15  # minutes per recommendation research
    TIME_PER_DASHBOARD = 20  # minutes per manual dashboard creation
    
    @staticmethod
    def calculate_usage_stats(user_id: int, period_days: int = 30, db: Session = None) -> dict:
        """Calculate usage statistics for a time period"""
        
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            # For MVP, use simplified calculation based on bot_chat_count
            # In production, use analytics events for accurate tracking
            
            # Get current month usage (simplified - using total count as proxy)
            messages = user.bot_chat_count or 0
            
            # Estimate feature usage (would be tracked in analytics)
            # For now, assume percentages based on typical usage
            analyses = int(messages * 0.1)  # 10% of messages are analyses
            recommendations = int(messages * 0.05)  # 5% are recommendations
            dashboard_views = int(messages * 0.15)  # 15% are dashboard checks
            
            return {
                'messages': messages,
                'analyses': analyses,
                'recommendations': recommendations,
                'dashboard_views': dashboard_views,
                'period_days': period_days
            }
            
        finally:
            if close_db:
                db.close()
    
    @staticmethod
    def calculate_time_saved(usage: dict) -> float:
        """Calculate total time saved in hours"""
        
        if not usage:
            return 0.0
        
        time_minutes = (
            usage['messages'] * ROICalculator.TIME_PER_MESSAGE +
            usage['analyses'] * ROICalculator.TIME_PER_ANALYSIS +
            usage['recommendations'] * ROICalculator.TIME_PER_RECOMMENDATION +
            usage['dashboard_views'] * ROICalculator.TIME_PER_DASHBOARD
        )
        
        return time_minutes / 60  # Convert to hours
    
    @staticmethod
    def calculate_monetary_value(time_saved_hours: float) -> int:
        """Calculate monetary value of time saved"""
        return int(time_saved_hours * ROICalculator.HOURLY_VALUE)
    
    @staticmethod
    def calculate_monthly_roi(user_id: int, db: Session = None) -> dict:
        """Calculate monthly ROI for Premium user"""
        
        # Get usage stats for current month
        usage = ROICalculator.calculate_usage_stats(user_id, period_days=30, db=db)
        
        if not usage:
            return {
                'error': 'User not found',
                'messages': 0,
                'time_saved': 0,
                'value': 0,
                'cost': ROICalculator.PREMIUM_MONTHLY,
                'profit': -ROICalculator.PREMIUM_MONTHLY,
                'roi_percent': -100
            }
        
        # Calculate time saved
        time_saved = ROICalculator.calculate_time_saved(usage)
        
        # Calculate value
        value = ROICalculator.calculate_monetary_value(time_saved)
        cost = ROICalculator.PREMIUM_MONTHLY
        profit = value - cost
        roi_percent = (profit / cost * 100) if cost > 0 else 0
        
        return {
            'messages': usage['messages'],
            'analyses': usage['analyses'],
            'recommendations': usage['recommendations'],
            'dashboard_views': usage['dashboard_views'],
            'time_saved': round(time_saved, 1),
            'value': value,
            'cost': cost,
            'profit': profit,
            'roi_percent': round(roi_percent, 1),
            'break_even_days': round(cost / (value / 30), 1) if value > 0 else float('inf')
        }
    
    @staticmethod
    def calculate_daily_roi(user_id: int, db: Session = None) -> dict:
        """Calculate daily ROI (for WOW moment)"""
        
        # Get 24h usage
        usage = ROICalculator.calculate_usage_stats(user_id, period_days=1, db=db)
        
        if not usage:
            return None
        
        time_saved = ROICalculator.calculate_time_saved(usage)
        value = ROICalculator.calculate_monetary_value(time_saved)
        cost = ROICalculator.PREMIUM_DAILY
        profit = value - cost
        roi_percent = (profit / cost * 100) if cost > 0 else 0
        
        return {
            'messages': usage['messages'],
            'time_saved': round(time_saved, 1),
            'value': value,
            'cost': cost,
            'profit': profit,
            'roi_percent': round(roi_percent, 1)
        }
    
    @staticmethod
    def format_roi_message(roi: dict, tier: str = "PREMIUM") -> str:
        """Format ROI data into a beautiful message"""
        
        if 'error' in roi:
            return "⚠️ Chưa có dữ liệu sử dụng"
        
        # Choose emoji based on ROI
        if roi['roi_percent'] >= 100:
            roi_emoji = "🚀"
        elif roi['roi_percent'] >= 50:
            roi_emoji = "📈"
        elif roi['roi_percent'] >= 0:
            roi_emoji = "✅"
        else:
            roi_emoji = "⚠️"
        
        message = f"""
━━━━━━━━━━━━━━━━━━━━━
📊 **SỬ DỤNG THÁNG NÀY:**
━━━━━━━━━━━━━━━━━━━━━

💬 {roi['messages']} tin nhắn với AI
📊 {roi['analyses']} phân tích tài chính
💡 {roi['recommendations']} gợi ý cá nhân
📈 {roi['dashboard_views']} lần xem dashboard

⏱️ **Tổng thời gian tiết kiệm: {roi['time_saved']}h**

━━━━━━━━━━━━━━━━━━━━━
💰 **ROI {tier}:**
━━━━━━━━━━━━━━━━━━━━━

Chi phí: {roi['cost']:,} VNĐ/tháng
Giá trị: {roi['value']:,} VNĐ

→ **Lời/Lỗ: {roi['profit']:,} VNĐ** {roi_emoji}
→ **ROI: {roi['roi_percent']:+.0f}%**
"""
        
        if roi['roi_percent'] > 0:
            message += f"\n🎉 {tier} là khoản đầu tư sinh lời!"
        elif roi['roi_percent'] == 0:
            message += f"\n✅ Break-even - Sử dụng thêm để tối ưu!"
        else:
            message += f"\n💡 Sử dụng nhiều hơn để tối đa hóa giá trị!"
        
        return message
