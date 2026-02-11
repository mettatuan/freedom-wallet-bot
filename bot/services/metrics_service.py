"""
Phase 2 Metrics Calculation Service
Calculates the 6 behavioral metrics for 60-day testing phase
NO optimization logic - observation only!
"""
from datetime import datetime, timedelta
from sqlalchemy import func, case, and_, or_
from loguru import logger
from bot.utils.database import get_db, User
from typing import Dict, Optional
import time


class MetricsCalculationService:
    """
    Calculate 6 Phase 2 metrics:
    - FREE: 30-day retention, transactions per user
    - VIP: Weekly active rate, natural Premium conversion
    - PREMIUM: AI usage, 90-day churn
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 600  # 10 minutes cache
    
    def get_all_metrics(self, force_refresh: bool = False) -> Dict:
        """
        Get all 6 metrics in one call
        Cached for 10 minutes unless force_refresh=True
        
        Returns:
            {
                'timestamp': datetime,
                'free': {...},
                'vip': {...},
                'premium': {...},
                'overall_status': 'HEALTHY' | 'WARNING' | 'CRITICAL'
            }
        """
        cache_key = 'all_metrics'
        
        # Check cache
        if not force_refresh and cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_duration:
                logger.info("📊 Returning cached metrics")
                return cached_data
        
        logger.info("📊 Calculating fresh metrics...")
        
        db = next(get_db())
        try:
            metrics = {
                'timestamp': datetime.utcnow(),
                'free': self._calculate_free_metrics(db),
                'vip': self._calculate_vip_metrics(db),
                'premium': self._calculate_premium_metrics(db),
            }
            
            # Calculate overall status
            metrics['overall_status'] = self._calculate_overall_status(metrics)
            
            # Cache results
            self.cache[cache_key] = (metrics, time.time())
            
            logger.info(f"✅ Metrics calculated: {metrics['overall_status']}")
            return metrics
            
        finally:
            db.close()
    
    def _calculate_free_metrics(self, db) -> Dict:
        """
        FREE Tier Metrics:
        1. 30-day retention ≥50%
        2. Transactions per user ≥10/month
        """
        # 1. 30-Day Retention
        # Users created 30+ days ago who were active in last 7 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        total_old_users = db.query(User).filter(
            User.created_at <= thirty_days_ago,
            User.is_free_unlocked == True
        ).count()
        
        active_old_users = db.query(User).filter(
            User.created_at <= thirty_days_ago,
            User.is_free_unlocked == True,
            User.last_active >= seven_days_ago
        ).count()
        
        retention_30day = (active_old_users / total_old_users * 100) if total_old_users > 0 else 0
        
        # 2. Transactions per User
        avg_transactions = db.query(
            func.avg(User.total_transactions)
        ).filter(
            User.is_free_unlocked == True,
            User.total_transactions > 0
        ).scalar() or 0
        
        # Supporting data
        total_free_users = db.query(User).filter(User.is_free_unlocked == True).count()
        active_7d = db.query(User).filter(
            User.is_free_unlocked == True,
            User.last_active >= seven_days_ago
        ).count()
        
        new_this_week = db.query(User).filter(
            User.is_free_unlocked == True,
            User.created_at >= seven_days_ago
        ).count()
        
        avg_referrals = db.query(
            func.avg(User.referral_count)
        ).filter(
            User.is_free_unlocked == True
        ).scalar() or 0
        
        return {
            'retention_30day': round(retention_30day, 1),
            'retention_target_met': retention_30day >= 50,
            'transactions_per_user': round(avg_transactions, 1),
            'transactions_target_met': avg_transactions >= 10,
            'total_users': total_free_users,
            'active_7d': active_7d,
            'new_this_week': new_this_week,
            'avg_referrals': round(avg_referrals, 1),
            'status': '🟢' if (retention_30day >= 50 and avg_transactions >= 10) else '🟡' if (retention_30day >= 45 or avg_transactions >= 9) else '🔴'
        }
    
    def _calculate_vip_metrics(self, db) -> Dict:
        """
        VIP Tier Metrics:
        3. Weekly active rate ≥70%
        4. Natural Premium conversion ~30% (25-35% OK)
        """
        # 3. Weekly Active Rate
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        total_vip = db.query(User).filter(
            User.vip_tier.isnot(None)
        ).count()
        
        active_vip = db.query(User).filter(
            User.vip_tier.isnot(None),
            User.last_active >= seven_days_ago
        ).count()
        
        weekly_active_pct = (active_vip / total_vip * 100) if total_vip > 0 else 0
        
        # 4. Natural Premium Conversion
        vip_with_premium = db.query(User).filter(
            User.vip_tier.isnot(None),
            User.subscription_tier == 'PREMIUM'
        ).count()
        
        premium_conversion_pct = (vip_with_premium / total_vip * 100) if total_vip > 0 else 0
        
        # VIP tier breakdown
        rising_star_count = db.query(User).filter(
            User.vip_tier == 'RISING_STAR'
        ).count()
        
        super_vip_count = db.query(User).filter(
            User.vip_tier == 'SUPER_VIP'
        ).count()
        
        legend_count = db.query(User).filter(
            User.vip_tier == 'LEGEND'
        ).count()
        
        avg_refs_per_vip = db.query(
            func.avg(User.referral_count)
        ).filter(
            User.vip_tier.isnot(None)
        ).scalar() or 0
        
        return {
            'weekly_active_pct': round(weekly_active_pct, 1),
            'weekly_active_target_met': weekly_active_pct >= 70,
            'premium_conversion_pct': round(premium_conversion_pct, 1),
            'premium_conversion_target_met': 25 <= premium_conversion_pct <= 35,
            'total_vip': total_vip,
            'active_vip': active_vip,
            'vip_with_premium': vip_with_premium,
            'rising_star_count': rising_star_count,
            'super_vip_count': super_vip_count,
            'legend_count': legend_count,
            'avg_refs_per_vip': round(avg_refs_per_vip, 1),
            'status': '🟢' if (weekly_active_pct >= 70 and 25 <= premium_conversion_pct <= 35) else '🟡' if (weekly_active_pct >= 63 or 20 <= premium_conversion_pct <= 40) else '🔴'
        }
    
    def _calculate_premium_metrics(self, db) -> Dict:
        """
        PREMIUM Tier Metrics:
        5. AI usage ≥10 msg/user
        6. 90-day churn <15%
        """
        # 5. AI Usage per User
        avg_ai_usage = db.query(
            func.avg(User.bot_chat_count)
        ).filter(
            User.subscription_tier.in_(['TRIAL', 'PREMIUM']),
            User.bot_chat_count > 0
        ).scalar() or 0
        
        # 6. 90-Day Churn
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        
        total_premium_90d = db.query(User).filter(
            User.premium_started_at <= ninety_days_ago,
            User.subscription_tier.in_(['TRIAL', 'PREMIUM'])
        ).count()
        
        churned_premium = db.query(User).filter(
            User.premium_started_at <= ninety_days_ago,
            User.subscription_tier.in_(['TRIAL', 'PREMIUM']),
            User.subscription_expires < datetime.utcnow()
        ).count()
        
        churn_90day_pct = (churned_premium / total_premium_90d * 100) if total_premium_90d > 0 else 0
        
        # Supporting data
        total_premium = db.query(User).filter(
            User.subscription_tier == 'PREMIUM'
        ).count()
        
        trial_users = db.query(User).filter(
            User.subscription_tier == 'TRIAL'
        ).count()
        
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        active_premium_7d = db.query(User).filter(
            User.subscription_tier.in_(['TRIAL', 'PREMIUM']),
            User.last_active >= seven_days_ago
        ).count()
        
        # Calculate avg subscription duration
        avg_sub_duration = db.query(
            func.avg(
                func.julianday(func.coalesce(User.subscription_expires, datetime.utcnow())) - 
                func.julianday(User.premium_started_at)
            )
        ).filter(
            User.premium_started_at.isnot(None)
        ).scalar() or 0
        
        return {
            'ai_usage_avg': round(avg_ai_usage, 1),
            'ai_usage_target_met': avg_ai_usage >= 10,
            'churn_90day_pct': round(churn_90day_pct, 1),
            'churn_target_met': churn_90day_pct < 15,
            'total_premium': total_premium,
            'trial_users': trial_users,
            'active_7d': active_premium_7d,
            'avg_sub_duration_days': round(avg_sub_duration, 0),
            'status': '🟢' if (avg_ai_usage >= 10 and churn_90day_pct < 15) else '🟡' if (avg_ai_usage >= 9 or churn_90day_pct < 17) else '🔴'
        }
    
    def _calculate_overall_status(self, metrics: Dict) -> str:
        """
        Overall health status:
        - HEALTHY: All 6 targets met
        - WARNING: 1-2 targets missed
        - CRITICAL: 3+ targets missed
        """
        targets_met = 0
        
        if metrics['free']['retention_target_met']:
            targets_met += 1
        if metrics['free']['transactions_target_met']:
            targets_met += 1
        if metrics['vip']['weekly_active_target_met']:
            targets_met += 1
        if metrics['vip']['premium_conversion_target_met']:
            targets_met += 1
        if metrics['premium']['ai_usage_target_met']:
            targets_met += 1
        if metrics['premium']['churn_target_met']:
            targets_met += 1
        
        if targets_met == 6:
            return 'HEALTHY'
        elif targets_met >= 4:
            return 'WARNING'
        else:
            return 'CRITICAL'
    
    def format_telegram_message(self, metrics: Dict) -> str:
        """
        Format metrics for Telegram display
        """
        m = metrics
        
        # Status emoji
        status_emoji = {
            'HEALTHY': '🟢',
            'WARNING': '🟡',
            'CRITICAL': '🔴'
        }
        
        # Status names in Vietnamese
        status_names = {
            'HEALTHY': 'TỐT',
            'WARNING': 'CẢNH BÁO',
            'CRITICAL': 'NGHIÊM TRỌNG'
        }
        
        message = f"""📊 <b>BẢNG THEO DÕI METRICS PHASE 2</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 Ngày: {m['timestamp'].strftime('%Y-%m-%d %H:%M')}
⏱️ Cập nhật: Thủ công

━━━━━━━━━━━━━━━━━━━━━━━━━━
🎁 <b>GIAI ĐOẠN FREE</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
Tỷ lệ giữ chân 30 ngày: <b>{m['free']['retention_30day']}%</b> {m['free']['status']} (Mục tiêu: ≥50%)
Giao dịch/User: <b>{m['free']['transactions_per_user']}</b> {m['free']['status']} (Mục tiêu: ≥10)

Tổng user FREE: {m['free']['total_users']}
Hoạt động (7 ngày): {m['free']['active_7d']} ({round(m['free']['active_7d']/m['free']['total_users']*100 if m['free']['total_users'] > 0 else 0, 0):.0f}%)
Mới tuần này: {m['free']['new_this_week']}

━━━━━━━━━━━━━━━━━━━━━━━━━━
⭐ <b>GIAI ĐOẠN VIP (Tầng Danh Tính)</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
Hoạt động hàng tuần: <b>{m['vip']['weekly_active_pct']}%</b> {m['vip']['status']} (Mục tiêu: ≥70%)
Chuyển Premium tự nhiên: <b>{m['vip']['premium_conversion_pct']}%</b> {m['vip']['status']} (Mục tiêu: ~30%)

Tổng user VIP: {m['vip']['total_vip']}
├─ Ngôi Sao Mới (10+): {m['vip']['rising_star_count']}
├─ Siêu VIP (50+): {m['vip']['super_vip_count']}
└─ Huyền Thoại (100+): {m['vip']['legend_count']}

Hoạt động (7 ngày): {m['vip']['active_vip']}/{m['vip']['total_vip']}

━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 <b>GIAI ĐOẠN PREMIUM (Chế Độ Mạnh)</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
Sử dụng AI: <b>{m['premium']['ai_usage_avg']} tin nhắn</b> {m['premium']['status']} (Mục tiêu: ≥10)
Rời bỏ 90 ngày: <b>{m['premium']['churn_90day_pct']}%</b> {m['premium']['status']} (Mục tiêu: &lt;15%)

Tổng Premium: {m['premium']['total_premium']}
User dùng thử: {m['premium']['trial_users']}
Hoạt động (7 ngày): {m['premium']['active_7d']}/{m['premium']['total_premium'] + m['premium']['trial_users']} ({round(m['premium']['active_7d']/(m['premium']['total_premium'] + m['premium']['trial_users'])*100 if (m['premium']['total_premium'] + m['premium']['trial_users']) > 0 else 0, 0):.0f}%)

━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 <b>TÌNH TRẠNG TỔNG QUÁT: {status_emoji[m['overall_status']]} {status_names[m['overall_status']]}</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        if m['overall_status'] == 'HEALTHY':
            message += "Tất cả 6 metrics đạt mục tiêu ✅\n"
        elif m['overall_status'] == 'WARNING':
            message += "1-2 metrics dưới mục tiêu ⚠️\n"
        else:
            message += "3+ metrics dưới mục tiêu 🚨\n"
        
        message += f"""
🔗 <b>Dashboard đầy đủ:</b>
https://docs.google.com/spreadsheets/d/1-fruHaSlCKIOpIfU5Qrkns0ze3bx3E-mKUgQ5fUF-Hg/edit

⚠️ <b>LƯU Ý:</b>
• Theo dõi, đừng tối ưu
• Ghi chép, đừng sửa
• Quan sát, đừng can thiệp
• Đợi đủ 60 ngày trước khi thay đổi

━━━━━━━━━━━━━━━━━━━━━━━━━━
Cập nhật tự động tiếp: Ngày mai 8:00 sáng
"""
        
        return message


# Create singleton instance
metrics_service = MetricsCalculationService()
