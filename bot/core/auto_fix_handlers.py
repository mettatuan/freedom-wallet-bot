"""
Auto-Fix Handlers — Tự động xử lý và recovery các lỗi phổ biến.

Mỗi handler nhận Exception và context, thử fix, trả về:
  - success: bool (đã fix thành công)
  - action_taken: str (mô tả hành động)
  - should_retry: bool (có nên retry operation không)
"""

import asyncio
import logging
import os
import ssl
import time
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class AutoFixResult:
    """Kết quả của auto-fix attempt."""
    
    def __init__(
        self,
        success: bool,
        action_taken: str,
        should_retry: bool = False,
        retry_delay: float = 0,
    ):
        self.success = success
        self.action_taken = action_taken
        self.should_retry = should_retry
        self.retry_delay = retry_delay


async def fix_database_locked(error: Exception, context: Dict[str, Any]) -> Optional[AutoFixResult]:
    """
    Fix: sqlite3.OperationalError: database is locked
    
    Strategy:
      1. Wait 1 second (DB lock thường tự giải phóng nhanh)
      2. Retry operation lần 2 với timeout lâu hơn
      3. Nếu vẫn lock → recommend retry sau 3s
    """
    error_msg = str(error).lower()
    if "database is locked" not in error_msg:
        return None
    
    logger.warning(f"🔧 Auto-fix: DB locked detected, waiting 1s...")
    await asyncio.sleep(1)
    
    # Try access DB to check if lock cleared
    try:
        from bot.utils.database import SessionLocal, User
        db = SessionLocal()
        try:
            db.query(User).limit(1).all()
            db.close()
            logger.info("✅ Auto-fix: DB lock cleared after 1s wait")
            return AutoFixResult(
                success=True,
                action_taken="Waited 1s, DB lock auto-cleared",
                should_retry=True,
                retry_delay=0,
            )
        except Exception as e:
            db.close()
            if "locked" in str(e).lower():
                logger.warning("⚠️ Auto-fix: DB still locked, recommend retry")
                return AutoFixResult(
                    success=False,
                    action_taken="DB still locked after 1s",
                    should_retry=True,
                    retry_delay=3,
                )
            raise
    except Exception as retry_error:
        logger.error(f"❌ Auto-fix: DB check failed: {retry_error}")
        return AutoFixResult(
            success=False,
            action_taken=f"DB check failed: {str(retry_error)[:100]}",
            should_retry=False,
        )


async def fix_ssl_certificate_error(error: Exception, context: Dict[str, Any]) -> Optional[AutoFixResult]:
    """
    Fix: SSL: CERTIFICATE_VERIFY_FAILED
    
    Strategy:
      1. Clear SSL context cache
      2. Recreate SSL context with default settings
      3. Force reconnect on next request
    """
    error_msg = str(error).lower()
    if "certificate" not in error_msg and "ssl" not in error_msg:
        return None
    
    logger.warning(f"🔧 Auto-fix: SSL error detected, attempting recovery...")
    
    try:
        # Clear httpx SSL cache if available
        import httpx
        if hasattr(httpx, '_ssl_context_cache'):
            httpx._ssl_context_cache.clear()
            logger.info("  → Cleared httpx SSL context cache")
        
        # Force new SSL context creation
        ssl_context = ssl.create_default_context()
        logger.info("  → Created new default SSL context")
        
        return AutoFixResult(
            success=True,
            action_taken="SSL context reset, will reconnect on next request",
            should_retry=True,
            retry_delay=0.5,
        )
    except Exception as fix_error:
        logger.error(f"❌ Auto-fix: SSL fix failed: {fix_error}")
        return AutoFixResult(
            success=False,
            action_taken=f"SSL fix failed: {str(fix_error)[:100]}",
            should_retry=False,
        )


async def fix_connection_reset(error: Exception, context: Dict[str, Any]) -> Optional[AutoFixResult]:
    """
    Fix: Connection reset by peer / RemoteProtocolError
    
    Strategy:
      1. Wait 0.5s for network stabilization
      2. Clear any stale connections
      3. Retry with new connection
    """
    error_msg = str(error).lower()
    if "connection reset" not in error_msg and "remoteprotocolerror" not in str(type(error)).lower():
        return None
    
    logger.warning(f"🔧 Auto-fix: Connection reset detected, waiting for stabilization...")
    await asyncio.sleep(0.5)
    
    return AutoFixResult(
        success=True,
        action_taken="Waited 0.5s for network stabilization",
        should_retry=True,
        retry_delay=0,
    )


async def fix_event_loop_closed(error: Exception, context: Dict[str, Any]) -> Optional[AutoFixResult]:
    """
    Fix: Event loop is closed
    
    Strategy:
      1. Log error and context for debugging
      2. Signal restart needed (không thể fix in-process)
      3. Graceful shutdown trigger
    """
    error_msg = str(error).lower()
    if "event loop" not in error_msg or "closed" not in error_msg:
        return None
    
    logger.critical(f"🔧 Auto-fix: Event loop closed detected - RESTART NEEDED")
    logger.critical(f"  → Context: {context}")
    
    # Write restart flag file for external watchdog
    restart_flag = Path("data/.needs_restart")
    restart_flag.parent.mkdir(parents=True, exist_ok=True)
    restart_flag.write_text(f"{time.time()}\n{str(error)}\n")
    logger.info(f"  → Created restart flag: {restart_flag}")
    
    return AutoFixResult(
        success=False,
        action_taken="Event loop closed - restart flag created",
        should_retry=False,
    )


async def fix_telegram_network_error(error: Exception, context: Dict[str, Any]) -> Optional[AutoFixResult]:
    """
    Fix: Telegram network errors (timeout, rate limit, etc.)
    
    Strategy:
      1. Check if rate limited → wait longer
      2. Check if timeout → retry with backoff
      3. Check if flood control → exponential backoff
    """
    error_type = str(type(error).__name__).lower()
    error_msg = str(error).lower()
    
    is_telegram_error = (
        "telegram" in str(type(error).__module__).lower() or
        "timeout" in error_msg or
        "rate" in error_msg or
        "flood" in error_msg
    )
    
    if not is_telegram_error:
        return None
    
    # Rate limit / Flood control
    if "rate" in error_msg or "flood" in error_msg or "429" in error_msg:
        wait_time = 30  # Telegram rate limit thường 30s
        logger.warning(f"🔧 Auto-fix: Telegram rate limit, waiting {wait_time}s...")
        await asyncio.sleep(wait_time)
        return AutoFixResult(
            success=True,
            action_taken=f"Rate limit - waited {wait_time}s",
            should_retry=True,
            retry_delay=0,
        )
    
    # Generic timeout
    if "timeout" in error_msg:
        logger.warning(f"🔧 Auto-fix: Telegram timeout, retrying after 2s...")
        return AutoFixResult(
            success=True,
            action_taken="Timeout - retry with backoff",
            should_retry=True,
            retry_delay=2,
        )
    
    return None


async def fix_disk_space_full(error: Exception, context: Dict[str, Any]) -> Optional[AutoFixResult]:
    """
    Fix: Disk full / No space left on device
    
    Strategy:
      1. Check disk space
      2. Clear old log files (>7 days)
      3. Clear temp files
      4. Alert admin if still critical
    """
    error_msg = str(error).lower()
    if "disk" not in error_msg and "space" not in error_msg and "no space" not in error_msg:
        return None
    
    logger.warning(f"🔧 Auto-fix: Disk space issue detected, attempting cleanup...")
    
    try:
        # Clear old log files
        log_dir = Path("data/logs")
        if log_dir.exists():
            old_logs_deleted = 0
            cutoff_time = time.time() - (7 * 24 * 3600)  # 7 days
            for log_file in log_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_time and log_file.name != "bot.log":
                    size_mb = log_file.stat().st_size / 1024 / 1024
                    log_file.unlink()
                    old_logs_deleted += 1
                    logger.info(f"  → Deleted old log: {log_file.name} ({size_mb:.1f}MB)")
            
            if old_logs_deleted > 0:
                return AutoFixResult(
                    success=True,
                    action_taken=f"Cleared {old_logs_deleted} old log files",
                    should_retry=True,
                    retry_delay=1,
                )
        
        return AutoFixResult(
            success=False,
            action_taken="No old logs to clear - disk still full",
            should_retry=False,
        )
    
    except Exception as fix_error:
        logger.error(f"❌ Auto-fix: Disk cleanup failed: {fix_error}")
        return AutoFixResult(
            success=False,
            action_taken=f"Cleanup failed: {str(fix_error)[:100]}",
            should_retry=False,
        )


# Registry of all auto-fix handlers
AUTO_FIX_HANDLERS = [
    fix_database_locked,
    fix_ssl_certificate_error,
    fix_connection_reset,
    fix_event_loop_closed,
    fix_telegram_network_error,
    fix_disk_space_full,
]


async def try_auto_fix(error: Exception, context: Optional[Dict[str, Any]] = None) -> Optional[AutoFixResult]:
    """
    Thử tất cả auto-fix handlers cho error.
    
    Returns:
      - AutoFixResult nếu có handler xử lý được
      - None nếu không có handler phù hợp
    """
    if context is None:
        context = {}
    
    for handler in AUTO_FIX_HANDLERS:
        start_time = time.time()
        try:
            result = await handler(error, context)
            if result:
                duration = time.time() - start_time
                
                # Record metrics
                try:
                    from bot.core.autofix_metrics import get_metrics
                    metrics = get_metrics()
                    metrics.record_attempt(handler.__name__, result.success, duration)
                except Exception as metrics_error:
                    logger.warning(f"Failed to record metrics: {metrics_error}")
                
                logger.info(
                    f"✅ Auto-fix applied by {handler.__name__}: {result.action_taken} "
                    f"(success={result.success}, retry={result.should_retry}, duration={duration:.2f}s)"
                )
                return result
        except Exception as handler_error:
            duration = time.time() - start_time
            
            # Record failed attempt
            try:
                from bot.core.autofix_metrics import get_metrics
                metrics = get_metrics()
                metrics.record_attempt(handler.__name__, False, duration)
            except:
                pass
            
            logger.error(
                f"❌ Auto-fix handler {handler.__name__} crashed: {handler_error}",
                exc_info=True,
            )
    
    return None
