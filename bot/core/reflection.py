"""
Reflection Engine - Financial Assistant Core
Generate personalized weekly insights and recommendations
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from bot.utils.database import Transaction, User, get_db
from bot.core.awareness import compute_weekly_spend, detect_streak
from bot.core.behavioral import analyze_spending_by_category, detect_spending_personas, analyze_spending_velocity


def generate_weekly_insight(user_id: int, db: Session = None) -> Dict[str, any]:
    """
    Generate personalized weekly insight with actionable recommendations.
    
    Components:
    1. Celebration (streaks, wins)
    2. Top spending categories
    3. Behavioral insights
    4. Gentle nudges (if needed)
    5. Actionable tips
    
    Args:
        user_id: Telegram user ID
        db: Database session
    
    Returns:
        Structured insight dictionary
    """
    close_db = False
    if db is None:
        db = next(get_db())
        close_db = True
    
    try:
        # Get user name
        user = db.query(User).filter(User.id == user_id).first()
        user_name = user.first_name if user else "bạn"
        
        # Get metrics
        week_spend = compute_weekly_spend(user_id, db=db)
        streak_info = detect_streak(user_id, db=db)
        categories = analyze_spending_by_category(user_id, days=7, db=db)
        personas = detect_spending_personas(user_id, db=db)
        velocity = analyze_spending_velocity(user_id, db=db)
        
        # Build insight components
        insight = {
            'user_name': user_name,
            'week_spend': week_spend,
            'streak': streak_info,
            'top_categories': categories[:3],
            'personas': personas,
            'velocity': velocity,
            'celebrations': _generate_celebrations(streak_info, week_spend),
            'nudges': _generate_nudges(user_id, streak_info, velocity, db),
            'tips': _generate_tips(categories, personas, velocity),
            'tone': _personalize_tone(streak_info, velocity),
            'timestamp': datetime.utcnow()
        }
        
        return insight
    finally:
        if close_db:
            db.close()


def _generate_celebrations(streak_info: Dict, week_spend: Dict) -> List[str]:
    """Generate celebration messages for wins and achievements."""
    celebrations = []
    
    # Streak celebrations
    if streak_info['current_streak'] >= 7:
        celebrations.append(f"🔥 Streak {streak_info['current_streak']} ngày! Kiên định quá!")
    elif streak_info['current_streak'] >= 3:
        celebrations.append(f"⭐ {streak_info['current_streak']} ngày liên tục! Tuyệt vời!")
    
    # Record streak
    if streak_info['current_streak'] == streak_info['longest_streak'] and streak_info['current_streak'] > 0:
        celebrations.append("🏆 Phá kỷ lục streak của bạn!")
    
    # Spending control (if spending decreased)
    if week_spend['expense'] > 0:  # Has spending data
        celebrations.append("💪 Bạn đang kiểm soát tài chính tốt đấy!")
    
    return celebrations if celebrations else ["✨ Tuần mới, cơ hội mới!"]


def _generate_nudges(user_id: int, streak_info: Dict, velocity: Dict, db: Session) -> List[str]:
    """Generate gentle nudges for improvement areas."""
    nudges = []
    
    # Streak nudge (if streak broken or low)
    if streak_info['current_streak'] == 0:
        nudges.append("📝 Ghi lại giao dịch hôm nay để bắt đầu streak mới nhé!")
    elif streak_info['current_streak'] < streak_info['longest_streak']:
        nudges.append(f"🎯 Kỷ lục của bạn là {streak_info['longest_streak']} ngày. Thử phá kỷ lục nhé!")
    
    # Missing days nudge
    last_tx = db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).order_by(Transaction.created_at.desc()).first()
    
    if last_tx:
        days_since = (datetime.utcnow() - last_tx.created_at).days
        if days_since >= 2:
            nudges.append(f"⏰ {days_since} ngày chưa ghi giao dịch. Hôm nay có chi gì không?")
    
    # Spending velocity nudge
    if velocity['trend'] == 'increasing':
        nudges.append("📊 Chi tiêu đang tăng. Cùng xem lại danh mục chi nào nhé?")
    
    return nudges


def _generate_tips(categories: List[Dict], personas: List[str], velocity: Dict) -> List[str]:
    """Generate actionable tips based on behavior."""
    tips = []
    
    # Category-specific tips
    if categories:
        top_cat = categories[0]
        
        if top_cat['category'] == 'Ăn uống':
            tips.append("💡 Tip: Chuẩn bị đồ ăn sẵn có thể giảm chi phí Ăn uống 30-40%")
        elif top_cat['category'] == 'Di chuyển':
            tips.append("💡 Tip: Thử đi xe bus hoặc xe đạp để tiết kiệm chi phí Di chuyển")
        elif top_cat['category'] == 'Mua sắm':
            tips.append("💡 Tip: Áp dụng rule 24h: Chờ 24h trước khi mua hàng online")
        elif top_cat['category'] == 'Giải trí':
            tips.append("💡 Tip: Tìm các hoạt động giải trí miễn phí như công viên, thư viện")
    
    # Persona-specific tips
    if "☕ Coffee Addict" in personas:
        tips.append("☕ Tip: Pha cà phê tại nhà có thể giảm chi phí 70%")
    elif "🚗 Grab Rider" in personas:
        tips.append("🚗 Tip: Đặt xe trước hoặc đi chung để tiết kiệm 20-30%")
    
    # Velocity-based tips
    if velocity['trend'] == 'increasing':
        tips.append("📈 Tip: Đặt ngân sách tuần để kiểm soát chi tiêu tốt hơn")
    
    return tips[:2]  # Max 2 tips to avoid overwhelming


def _personalize_tone(streak_info: Dict, velocity: Dict) -> str:
    """
    Determine personalized tone based on user behavior.
    
    Tones:
    - encouraging: For users with good streaks
    - supportive: For users struggling
    - celebratory: For users hitting milestones
    - neutral: Default
    """
    if streak_info['current_streak'] >= 7:
        return "celebratory"
    elif streak_info['current_streak'] >= 3:
        return "encouraging"
    elif velocity['trend'] == 'decreasing':
        return "encouraging"
    elif streak_info['current_streak'] == 0:
        return "supportive"
    else:
        return "neutral"


def format_weekly_insight_message(insight: Dict[str, any]) -> str:
    """
    Format weekly insight into user-friendly message.
    
    Args:
        insight: Weekly insight from generate_weekly_insight()
    
    Returns:
        Formatted message string with personalized tone
    """
    from bot.core.nlp import format_vnd
    
    user_name = insight['user_name']
    tone = insight['tone']
    celebrations = insight['celebrations']
    week_spend = insight['week_spend']
    top_categories = insight['top_categories']
    nudges = insight['nudges']
    tips = insight['tips']
    
    # Greeting based on tone
    greetings = {
        'celebratory': f"🎉 Chào {user_name}! Tuần qua tuyệt vời!",
        'encouraging': f"⭐ Chào {user_name}! Tuần qua bạn làm tốt lắm!",
        'supportive': f"💙 Chào {user_name}! Cùng nhìn lại tuần qua nhé",
        'neutral': f"📊 Chào {user_name}! Báo cáo tuần này đây"
    }
    
    message = f"{greetings.get(tone, greetings['neutral'])}\n\n"
    
    # Celebrations
    if celebrations:
        for celebration in celebrations[:2]:  # Max 2
            message += f"{celebration}\n"
        message += "\n"
    
    # Week summary
    message += f"<b>📈 Tuần này (7 ngày):</b>\n"
    message += f"📤 Chi: {format_vnd(week_spend['expense'])}\n"
    message += f"📥 Thu: {format_vnd(week_spend['income'])}\n"
    message += f"💵 Còn lại: {format_vnd(week_spend['net'])}\n\n"
    
    # Top categories
    if top_categories:
        message += f"<b>Top 3 danh mục chi:</b>\n"
        for i, cat in enumerate(top_categories, 1):
            message += f"{i}. {cat['category']}: {format_vnd(cat['total'])} ({cat['percentage']}%)\n"
        message += "\n"
    
    # Nudges
    if nudges:
        message += f"<b>💭 Gợi ý:</b>\n"
        for nudge in nudges[:2]:  # Max 2
            message += f"{nudge}\n"
        message += "\n"
    
    # Tips
    if tips:
        message += f"<b>🎯 Tips hữu ích:</b>\n"
        for tip in tips:
            message += f"{tip}\n"
    
    return message


def should_send_weekly_insight(user_id: int, db: Session = None) -> bool:
    """
    Check if user should receive weekly insight.
    
    Criteria:
    - At least 7 days since registration
    - At least 5 transactions in last 7 days
    - Not sent insight in last 6 days
    
    Args:
        user_id: Telegram user ID
        db: Database session
    
    Returns:
        True if should send insight
    """
    close_db = False
    if db is None:
        db = next(get_db())
        close_db = True
    
    try:
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # Check registration date (at least 7 days)
        if user.created_at:
            days_since_registration = (datetime.utcnow() - user.created_at).days
            if days_since_registration < 7:
                return False
        
        # Check transaction count (last 7 days)
        week_start = datetime.utcnow() - timedelta(days=7)
        tx_count = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.created_at >= week_start
        ).count()
        
        if tx_count < 5:
            return False
        
        # Check last insight sent (at least 6 days ago)
        if user.last_insight_sent:
            days_since_last = (datetime.utcnow() - user.last_insight_sent).days
            if days_since_last < 6:
                return False
        
        return True
        
    finally:
        if close_db:
            db.close()


def mark_insight_sent(user_id: int, db: Session = None) -> bool:
    """
    Mark that weekly insight was sent to user.
    
    Args:
        user_id: Telegram user ID
        db: Database session
    
    Returns:
        True if successful
    """
    close_db = False
    if db is None:
        db = next(get_db())
        close_db = True
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.last_insight_sent = datetime.utcnow()
            db.commit()
            return True
        return False
    finally:
        if close_db:
            db.close()
