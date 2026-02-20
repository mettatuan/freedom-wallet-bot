"""
Behavioral Engine - Financial Assistant Core
Analyze spending patterns and detect behavioral personas
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from bot.utils.database import Transaction, get_db


def analyze_spending_by_category(user_id: int, days: int = 30, db: Session = None) -> List[Dict[str, any]]:
    """
    Analyze spending breakdown by category.
    
    Args:
        user_id: Telegram user ID
        days: Number of days to analyze (default: 30)
        db: Database session
    
    Returns:
        List of category spending data, sorted by amount
    """
    close_db = False
    if db is None:
        db = next(get_db())
        close_db = True
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    try:
        # Group expenses by category
        category_totals = db.query(
            Transaction.category,
            func.sum(Transaction.amount).label('total'),
            func.count(Transaction.id).label('count')
        ).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == 'expense',
                Transaction.created_at >= start_date
            )
        ).group_by(Transaction.category).all()
        
        # Format results
        results = []
        total_expense = 0
        
        for cat, total, count in category_totals:
            total_expense += abs(total)
        
        for cat, total, count in category_totals:
            percentage = (abs(total) / total_expense * 100) if total_expense > 0 else 0
            results.append({
                'category': cat,
                'total': abs(total),
                'count': count,
                'percentage': round(percentage, 1),
                'avg_per_transaction': abs(total) // count if count > 0 else 0
            })
        
        # Sort by total (descending)
        results.sort(key=lambda x: x['total'], reverse=True)
        
        return results
    finally:
        if close_db:
            db.close()


def analyze_spending_by_time(user_id: int, days: int = 30, db: Session = None) -> Dict[str, any]:
    """
    Analyze spending patterns by time (hour, day of week).
    
    Args:
        user_id: Telegram user ID
        days: Number of days to analyze
        db: Database session
    
    Returns:
        Dictionary with hourly and daily patterns
    """
    close_db = False
    if db is None:
        db = next(get_db())
        close_db = True
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    try:
        # Get all expense transactions
        transactions = db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == 'expense',
                Transaction.created_at >= start_date
            )
        ).all()
        
        # Analyze by hour
        hourly_pattern = defaultdict(lambda: {'total': 0, 'count': 0})
        daily_pattern = defaultdict(lambda: {'total': 0, 'count': 0})
        
        for tx in transactions:
            hour = tx.created_at.hour
            day = tx.created_at.strftime('%A')  # Monday, Tuesday, etc.
            
            hourly_pattern[hour]['total'] += abs(tx.amount)
            hourly_pattern[hour]['count'] += 1
            
            daily_pattern[day]['total'] += abs(tx.amount)
            daily_pattern[day]['count'] += 1
        
        # Find peak hours and days
        peak_hour = max(hourly_pattern.items(), key=lambda x: x[1]['total'])[0] if hourly_pattern else None
        peak_day = max(daily_pattern.items(), key=lambda x: x[1]['total'])[0] if daily_pattern else None
        
        return {
            'hourly': dict(hourly_pattern),
            'daily': dict(daily_pattern),
            'peak_hour': peak_hour,
            'peak_day': peak_day
        }
    finally:
        if close_db:
            db.close()


def detect_spending_personas(user_id: int, db: Session = None) -> List[str]:
    """
    Detect behavioral spending personas based on patterns.
    
    Personas:
    - "Coffee Addict" - Frequent coffee/drink purchases
    - "Foodie" - High spending on food & dining
    - "Weekend Spender" - Most spending on weekends
    - "Lunchtime Leaker" - Spending peaks around lunch (11am-2pm)
    - "Night Owl" - Late-night transactions (after 10pm)
    - "Grab Rider" - Frequent transport expenses
    - "Online Shopper" - Frequent shopping transactions
    
    Args:
        user_id: Telegram user ID
        db: Database session
    
    Returns:
        List of detected persona strings
    """
    close_db = False
    if db is None:
        db = next(get_db())
        close_db = True
    
    personas = []
    
    try:
        # Get 30-day spending analysis
        categories = analyze_spending_by_category(user_id, days=30, db=db)
        time_patterns = analyze_spending_by_time(user_id, days=30, db=db)
        
        # Check for Coffee Addict (Ăn uống > 30% and high frequency)
        food_cat = next((c for c in categories if c['category'] == 'Ăn uống'), None)
        if food_cat and food_cat['percentage'] > 30 and food_cat['count'] > 20:
            personas.append("☕ Coffee Addict")
        
        # Check for Foodie (Ăn uống is top category)
        if categories and categories[0]['category'] == 'Ăn uống':
            personas.append("🍜 Foodie")
        
        # Check for Weekend Spender
        daily = time_patterns['daily']
        weekend_total = daily.get('Saturday', {}).get('total', 0) + daily.get('Sunday', {}).get('total', 0)
        weekday_total = sum(daily.get(day, {}).get('total', 0) for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
        
        if weekend_total > weekday_total * 0.4:  # Weekend spending > 40% of weekday
            personas.append("🎉 Weekend Spender")
        
        # Check for Lunchtime Leaker
        hourly = time_patterns['hourly']
        lunch_hours = [11, 12, 13]
        lunch_total = sum(hourly.get(h, {}).get('total', 0) for h in lunch_hours)
        total_spend = sum(h['total'] for h in hourly.values())
        
        if lunch_total > total_spend * 0.4:
            personas.append("🌮 Lunchtime Leaker")
        
        # Check for Night Owl
        night_hours = [22, 23, 0, 1, 2]
        night_count = sum(hourly.get(h, {}).get('count', 0) for h in night_hours)
        
        if night_count > 5:
            personas.append("🦉 Night Owl")
        
        # Check for Grab Rider
        transport_cat = next((c for c in categories if c['category'] == 'Di chuyển'), None)
        if transport_cat and transport_cat['percentage'] > 20:
            personas.append("🚗 Grab Rider")
        
        # Check for Online Shopper
        shopping_cat = next((c for c in categories if c['category'] == 'Mua sắm'), None)
        if shopping_cat and shopping_cat['count'] > 10:
            personas.append("🛒 Online Shopper")
        
        return personas if personas else ["✨ Balanced Spender"]
    finally:
        if close_db:
            db.close()


def analyze_spending_velocity(user_id: int, db: Session = None) -> Dict[str, any]:
    """
    Analyze spending velocity (rate of spending over time).
    
    Compares recent spending (last 7 days) to baseline (last 30 days).
    
    Args:
        user_id: Telegram user ID
        db: Database session
    
    Returns:
        Velocity metrics and trend
    """
    close_db = False
    if db is None:
        db = next(get_db())
        close_db = True
    
    try:
        # Last 7 days average
        week_start = datetime.utcnow() - timedelta(days=7)
        week_total = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == 'expense',
                Transaction.created_at >= week_start
            )
        ).scalar() or 0
        
        week_avg = abs(week_total) / 7
        
        # Last 30 days average
        month_start = datetime.utcnow() - timedelta(days=30)
        month_total = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == 'expense',
                Transaction.created_at >= month_start
            )
        ).scalar() or 0
        
        month_avg = abs(month_total) / 30
        
        # Calculate velocity
        if month_avg > 0:
            velocity_ratio = week_avg / month_avg
            
            if velocity_ratio > 1.5:
                trend = "increasing"
                trend_emoji = "📈"
                trend_message = "Chi tiêu đang tăng nhanh"
            elif velocity_ratio < 0.7:
                trend = "decreasing"
                trend_emoji = "📉"
                trend_message = "Chi tiêu đang giảm"
            else:
                trend = "stable"
                trend_emoji = "➡️"
                trend_message = "Chi tiêu ổn định"
        else:
            velocity_ratio = 1.0
            trend = "stable"
            trend_emoji = "➡️"
            trend_message = "Chưa đủ dữ liệu"
        
        return {
            'week_avg_daily': int(week_avg),
            'month_avg_daily': int(month_avg),
            'velocity_ratio': round(velocity_ratio, 2),
            'trend': trend,
            'trend_emoji': trend_emoji,
            'trend_message': trend_message
        }
    finally:
        if close_db:
            db.close()


def get_behavioral_snapshot(user_id: int, db: Session = None) -> Dict[str, any]:
    """
    Get complete behavioral analysis snapshot.
    
    Args:
        user_id: Telegram user ID
        db: Database session
    
    Returns:
        Complete behavioral snapshot
    """
    close_db = False
    if db is None:
        db = next(get_db())
        close_db = True
    
    try:
        snapshot = {
            'categories': analyze_spending_by_category(user_id, days=30, db=db),
            'time_patterns': analyze_spending_by_time(user_id, days=30, db=db),
            'personas': detect_spending_personas(user_id, db=db),
            'velocity': analyze_spending_velocity(user_id, db=db),
            'timestamp': datetime.utcnow()
        }
        
        return snapshot
    finally:
        if close_db:
            db.close()


def format_behavioral_message(snapshot: Dict[str, any]) -> str:
    """
    Format behavioral snapshot into user-friendly message.
    
    Args:
        snapshot: Behavioral snapshot from get_behavioral_snapshot()
    
    Returns:
        Formatted message string
    """
    from bot.core.nlp import format_vnd
    
    categories = snapshot['categories']
    personas = snapshot['personas']
    velocity = snapshot['velocity']
    
    message = f"🧠 <b>Phân tích hành vi chi tiêu</b>\n\n"
    
    # Top 3 categories
    if categories:
        message += f"<b>Top 3 danh mục:</b>\n"
        for i, cat in enumerate(categories[:3], 1):
            message += f"{i}. {cat['category']}: {format_vnd(cat['total'])} ({cat['percentage']}%)\n"
        message += "\n"
    
    # Personas
    if personas:
        message += f"<b>Tính cách chi tiêu:</b>\n"
        for persona in personas[:3]:  # Max 3
            message += f"• {persona}\n"
        message += "\n"
    
    # Velocity trend
    message += f"<b>Xu hướng:</b>\n"
    message += f"{velocity['trend_emoji']} {velocity['trend_message']}\n"
    message += f"7 ngày: {format_vnd(velocity['week_avg_daily'])}/ngày\n"
    message += f"30 ngày: {format_vnd(velocity['month_avg_daily'])}/ngày\n"
    
    return message
