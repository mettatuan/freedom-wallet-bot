"""
Google Sheets Sync - Financial Assistant Core
Auto-sync transactions to user's Google Sheets
"""
from datetime import datetime
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
import requests
from loguru import logger

from bot.utils.database import Transaction, User, get_db


async def sync_transaction_to_sheets(transaction_id: int, user_id: int, db: Session = None) -> bool:
    """
    Sync a single transaction to user's Google Sheets.
    
    Flow:
    1. Get user's webhook_url
    2. Format transaction data
    3. POST to webhook
    4. Update synced_to_sheets flag
    
    Args:
        transaction_id: Transaction ID to sync
        user_id: User ID
        db: Database session
    
    Returns:
        True if sync successful, False otherwise
    """
    close_db = False
    if db is None:
        db = next(get_db())
        close_db = True
    
    try:
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.webhook_url:
            logger.warning(f"User {user_id} has no webhook_url configured")
            return False
        
        # Get transaction
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            logger.error(f"Transaction {transaction_id} not found")
            return False
        
        # Format data for Google Sheets
        # Expected format: {date, amount, category, description, type}
        payload = {
            'action': 'add_transaction',
            'data': {
                'date': transaction.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'amount': abs(transaction.amount),  # Send positive amount
                'category': transaction.category,
                'description': transaction.description,
                'type': transaction.transaction_type,
                'user_id': user_id
            }
        }
        
        # Send to Google Apps Script webhook
        try:
            response = requests.post(
                user.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                # Update sync status
                transaction.synced_to_sheets = True
                transaction.synced_at = datetime.utcnow()
                
                # Update user's last sync time
                user.sheets_last_sync = datetime.utcnow()
                
                db.commit()
                
                logger.info(f"✅ Transaction {transaction_id} synced to Sheets for user {user_id}")
                return True
            else:
                logger.error(f"❌ Sheets sync failed: HTTP {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Sheets sync request failed: {e}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error syncing transaction {transaction_id}: {e}")
        return False
    finally:
        if close_db:
            db.close()


async def sync_all_pending_transactions(user_id: int, db: Session = None) -> Dict[str, int]:
    """
    Sync all unsynced transactions for a user.
    
    Args:
        user_id: User ID
        db: Database session
    
    Returns:
        Dictionary with sync stats {success: int, failed: int, total: int}
    """
    close_db = False
    if db is None:
        db = next(get_db())
        close_db = True
    
    try:
        # Get all unsynced transactions
        pending = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.synced_to_sheets == False
        ).all()
        
        stats = {
            'success': 0,
            'failed': 0,
            'total': len(pending)
        }
        
        for tx in pending:
            success = await sync_transaction_to_sheets(tx.id, user_id, db)
            if success:
                stats['success'] += 1
            else:
                stats['failed'] += 1
        
        logger.info(f"📊 Bulk sync for user {user_id}: {stats['success']}/{stats['total']} successful")
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error in bulk sync for user {user_id}: {e}")
        return {'success': 0, 'failed': 0, 'total': 0}
    finally:
        if close_db:
            db.close()


async def get_sync_status(user_id: int, db: Session = None) -> Dict[str, any]:
    """
    Get sync status for a user.
    
    Args:
        user_id: User ID
        db: Database session
    
    Returns:
        Dictionary with sync status
    """
    close_db = False
    if db is None:
        db = next(get_db())
        close_db = True
    
    try:
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        
        # Count transactions
        total_tx = db.query(Transaction).filter(Transaction.user_id == user_id).count()
        synced_tx = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.synced_to_sheets == True
        ).count()
        pending_tx = total_tx - synced_tx
        
        status = {
            'has_webhook': bool(user and user.webhook_url),
            'webhook_url': user.webhook_url if user else None,
            'last_sync': user.sheets_last_sync if user else None,
            'total_transactions': total_tx,
            'synced_transactions': synced_tx,
            'pending_transactions': pending_tx,
            'sync_percentage': round((synced_tx / total_tx * 100) if total_tx > 0 else 0, 1)
        }
        
        return status
        
    except Exception as e:
        logger.error(f"❌ Error getting sync status for user {user_id}: {e}")
        return {
            'has_webhook': False,
            'total_transactions': 0,
            'synced_transactions': 0,
            'pending_transactions': 0,
            'sync_percentage': 0
        }
    finally:
        if close_db:
            db.close()


def format_sync_status_message(status: Dict[str, any]) -> str:
    """
    Format sync status into user-friendly message.
    
    Args:
        status: Sync status from get_sync_status()
    
    Returns:
        Formatted message string
    """
    if not status['has_webhook']:
        return (
            "⚠️ <b>Google Sheets chưa kết nối</b>\n\n"
            "Bạn cần kết nối Google Sheets để tự động đồng bộ giao dịch.\n\n"
            "Nhấn '🔗 Kết nối Drive' để bắt đầu."
        )
    
    message = "📊 <b>Trạng thái đồng bộ Google Sheets</b>\n\n"
    message += f"📝 Tổng giao dịch: {status['total_transactions']}\n"
    message += f"✅ Đã đồng bộ: {status['synced_transactions']}\n"
    message += f"⏳ Chờ đồng bộ: {status['pending_transactions']}\n"
    message += f"📈 Tiến độ: {status['sync_percentage']}%\n\n"
    
    if status['last_sync']:
        last_sync_str = status['last_sync'].strftime('%d/%m/%Y %H:%M')
        message += f"⏰ Lần đồng bộ cuối: {last_sync_str}"
    else:
        message += "ℹ️ Chưa có lần đồng bộ nào"
    
    if status['pending_transactions'] > 0:
        message += f"\n\n💡 Có {status['pending_transactions']} giao dịch chưa đồng bộ. Nhấn 'Đồng bộ ngay' để cập nhật."
    
    return message
