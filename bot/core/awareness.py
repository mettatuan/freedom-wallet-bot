"""
Awareness Engine - Financial Assistant Core
Real-time financial awareness metrics and anomaly detection
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from bot.utils.database import Transaction, User, get_db


def compute_balance(user_id: int, db: Session = None) -> int:
    """
    Calculate current balance from all transactions.
    
    Balance = Total Income + Total Expenses (expenses are negative)
    
    Args:
        user_id: Telegram user ID
        db: Database session (optional, will create if not provided)
    
    Returns:
        Current balance in VND
    """
    close_db = False
    if db is None:
        db = next(get_db())
        close_db = True
    
    try:
        # Sum all transactions (expenses are negative, income is positive)
        total = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id
        ).scalar() or 0
        
        return int(total)
    finally:
        if close_db:
            db.close()


def compute_daily_spend(user_id: int, date: datetime = None, db: Session = None) -> Dict[str, int]:
    """
    Calculate daily spending totals.
    
    Args:
        user_id: Telegram user ID
        date: Date to calculate (default: today)
        db: Database session
    
    Returns:
        Dictionary with income, expense, net totals
    """
    close_db = False
    if db is None:
        db = next(get_db())
        close_db = True
    
    if date is None:
        date = datetime.utcnow()
    
    # Get start and end of day
    start_of_day = datetime(date.year, date.month, date.day, 0, 0, 0)
    end_of_day = start_of_day + timedelta(days=1)
    
    try:
        # Income today
        income = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == 'income',
                Transaction.created_at >= start_of_day,
                Transaction.created_at < end_of_day
            )
        ).scalar() or 0
        
        # Expenses today (negative values)
        expense = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == 'expense',
                Transaction.created_at >= start_of_day,
                Transaction.created_at < end_of_day
            )
        ).scalar() or 0
        
        return {
            'income': int(income),
            'expense': int(abs(expense)),
            'net': int(income + expense)  # expense is negative
        }
    finally:
        if close_db:
            db.close()


def compute_weekly_spend(user_id: int, db: Session = None) -> Dict[str, int]:
    """
    Calculate weekly spending totals (last 7 days).
    
    Args:
        user_id: Telegram user ID
        db: Database session
    
    Returns:
        Dictionary with income, expense, net totals
    """
    close_db = False
    if db is None:
        db = next(get_db())
        close_db = True
    
    # Last 7 days
    start_date = datetime.utcnow() - timedelta(days=7)
    
    try:
        # Income this week
        income = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == 'income',
                Transaction.created_at >= start_date
            )
        ).scalar() or 0
        
        # Expenses this week
        expense = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == 'expense',
                Transaction.created_at >= start_date
            )
        ).scalar() or 0
        
        return {
            'income': int(income),
            'expense': int(abs(expense)),
            'net': int(income + expense)
        }
    finally:
        if close_db:
            db.close()


def detect_streak(user_id: int, db: Session = None) -> Dict[str, int]:
    """
    Detect consecutive days with transactions.
    
    Args:
        user_id: Telegram user ID
        db: Database session
    
    Returns:
        Dictionary with current_streak, longest_streak
    """
    close_db = False
    if db is None:
        db = next(get_db())
        close_db = True
    
    try:
        # Get all transaction dates (distinct days)
        transactions = db.query(
            func.date(Transaction.created_at).label('date')
        ).filter(
            Transaction.user_id == user_id
        ).group_by(
            func.date(Transaction.created_at)
        ).order_by(
            func.date(Transaction.created_at).desc()
        ).all()
        
        if not transactions:
            return {'current_streak': 0, 'longest_streak': 0}
        
        # Convert to list of dates
        dates = [t.date for t in transactions]
        
        # Calculate current streak (from today backwards)
        today = datetime.utcnow().date()
        current_streak = 0
        
        # Check if today or yesterday has transaction
        if dates[0] == today or dates[0] == today - timedelta(days=1):
            current_streak = 1
            check_date = dates[0] - timedelta(days=1)
            
            for date in dates[1:]:
                if date == check_date:
                    current_streak += 1
                    check_date = date - timedelta(days=1)
                else:
                    break
        
        # Calculate longest streak
        longest_streak = 0
        temp_streak = 1
        
        for i in range(1, len(dates)):
            if dates[i] == dates[i-1] - timedelta(days=1):
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 1
        
        longest_streak = max(longest_streak, temp_streak)
        
        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak
        }
    finally:
        if close_db:
            db.close()


def detect_anomalies(user_id: int, db: Session = None) -> List[Dict[str, any]]:
    """
    Detect spending anomalies and patterns.
    
    Anomalies:
    - Overspending: Daily spending > 2x average daily spend
    - Missing days: No transaction for 3+ consecutive days
    - Large transaction: Single transaction > 50% of weekly average
    
    Args:
        user_id: Telegram user ID
        db: Database session
    
    Returns:
        List of anomaly dictionaries
    """
    close_db = False
    if db is None:
        db = next(get_db())
        close_db = True
    
    anomalies = []
    
    try:
        # Get average daily spend (last 30 days)
        start_date = datetime.utcnow() - timedelta(days=30)
        
        total_expense = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == 'expense',
                Transaction.created_at >= start_date
            )
        ).scalar() or 0
        
        avg_daily_spend = abs(total_expense) / 30 if total_expense else 0
        
        # Check today's spending
        today_spend = compute_daily_spend(user_id, db=db)['expense']
        
        if avg_daily_spend > 0 and today_spend > avg_daily_spend * 2:
            anomalies.append({
                'type': 'overspending',
                'severity': 'high',
                'message': f'Chi tiêu hôm nay ({today_spend:,}đ) cao gấp đôi trung bình ({int(avg_daily_spend):,}đ)',
                'value': today_spend,
                'threshold': int(avg_daily_spend * 2)
            })
        
        # Check for missing days (no transaction in last 3 days)
        last_transaction = db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).order_by(Transaction.created_at.desc()).first()
        
        if last_transaction:
            days_since_last = (datetime.utcnow() - last_transaction.created_at).days
            
            if days_since_last >= 3:
                anomalies.append({
                    'type': 'missing_days',
                    'severity': 'medium',
                    'message': f'{days_since_last} ngày chưa ghi giao dịch',
                    'value': days_since_last,
                    'threshold': 3
                })
        
        # Check for large transactions (last 7 days)
        weekly_avg = compute_weekly_spend(user_id, db=db)['expense'] / 7
        
        recent_large = db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == 'expense',
                Transaction.created_at >= datetime.utcnow() - timedelta(days=7),
                Transaction.amount < -(weekly_avg * 0.5)  # Negative, so use <
            )
        ).all()
        
        for tx in recent_large:
            anomalies.append({
                'type': 'large_transaction',
                'severity': 'medium',
                'message': f'Giao dịch lớn: {abs(tx.amount):,}đ ({tx.category})',
                'value': abs(tx.amount),
                'threshold': int(weekly_avg * 0.5),
                'transaction': {
                    'id': tx.id,
                    'amount': tx.amount,
                    'category': tx.category,
                    'description': tx.description,
                    'date': tx.created_at
                }
            })
        
        return anomalies
        
    finally:
        if close_db:
            db.close()


def get_awareness_snapshot(user_id: int, db: Session = None) -> Dict[str, any]:
    """
    Get complete awareness snapshot for a user.
    
    Returns all awareness metrics in one call:
    - Current balance
    - Today's spend
    - Weekly spend
    - Streak info
    - Anomalies
    
    Args:
        user_id: Telegram user ID
        db: Database session
    
    Returns:
        Complete awareness snapshot dictionary
    """
    close_db = False
    if db is None:
        db = next(get_db())
        close_db = True
    
    try:
        snapshot = {
            'balance': compute_balance(user_id, db),
            'today': compute_daily_spend(user_id, db=db),
            'week': compute_weekly_spend(user_id, db=db),
            'streak': detect_streak(user_id, db=db),
            'anomalies': detect_anomalies(user_id, db=db),
            'timestamp': datetime.utcnow()
        }
        
        return snapshot
    finally:
        if close_db:
            db.close()


def format_awareness_message(snapshot: Dict[str, any]) -> str:
    """
    Format awareness snapshot into user-friendly message.
    
    Args:
        snapshot: Awareness snapshot from get_awareness_snapshot()
    
    Returns:
        Formatted message string
    """
    from bot.core.nlp import format_vnd
    
    balance = snapshot['balance']
    today = snapshot['today']
    week = snapshot['week']
    streak = snapshot['streak']
    anomalies = snapshot['anomalies']
    
    # Balance emoji
    balance_emoji = "💰" if balance >= 0 else "⚠️"
    
    # Streak emoji
    streak_emoji = "🔥" if streak['current_streak'] >= 7 else "⭐"
    
    message = f"📊 <b>Tổng quan tài chính</b>\n\n"
    message += f"{balance_emoji} Số dư: {format_vnd(balance)}\n\n"
    
    message += f"<b>Hôm nay:</b>\n"
    message += f"📥 Thu: {format_vnd(today['income'])}\n"
    message += f"📤 Chi: {format_vnd(today['expense'])}\n"
    message += f"💵 Còn lại: {format_vnd(today['net'])}\n\n"
    
    message += f"<b>Tuần này (7 ngày):</b>\n"
    message += f"📥 Thu: {format_vnd(week['income'])}\n"
    message += f"📤 Chi: {format_vnd(week['expense'])}\n"
    message += f"💵 Còn lại: {format_vnd(week['net'])}\n\n"
    
    if streak['current_streak'] > 0:
        message += f"{streak_emoji} Streak: {streak['current_streak']} ngày"
        if streak['longest_streak'] > streak['current_streak']:
            message += f" (Kỷ lục: {streak['longest_streak']} ngày)"
        message += "\n\n"
    
    # Show anomalies
    if anomalies:
        message += f"⚠️ <b>Cảnh báo:</b>\n"
        for anomaly in anomalies[:3]:  # Show max 3 anomalies
            message += f"• {anomaly['message']}\n"
    
    return message
