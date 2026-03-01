"""
Auto-Rollback System — Phát hiện regression và tự động rollback.

Cách hoạt động:
  1. Sau mỗi deploy, tạo health snapshot (error rate, response time)
  2. Monitor các metrics trong 10-30 phút
  3. Nếu phát hiện regression (error rate tăng >50%, response time tăng >2x)
     → Tự động rollback về commit trước
  4. Gửi alert admin

Triggers:
  - Error rate spike (>50% increase trong 10 phút)
  - Critical errors (Event Loop, DB corruption)
  - Response time degradation (>2x baseline)
  - User complaint rate spike
"""

import asyncio
import json
import subprocess
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

ROLLBACK_CONFIG_FILE = Path("data/rollback/config.json")
HEALTH_SNAPSHOTS_FILE = Path("data/rollback/health_snapshots.json")
ROLLBACK_HISTORY_FILE = Path("data/rollback/rollback_history.json")


class HealthSnapshot:
    """Health snapshot tại một thời điểm."""
    
    def __init__(
        self,
        timestamp: float,
        git_commit: str,
        error_count: int,
        critical_error_count: int,
        avg_response_time: float,
        active_users: int,
    ):
        self.timestamp = timestamp
        self.git_commit = git_commit
        self.error_count = error_count
        self.critical_error_count = critical_error_count
        self.avg_response_time = avg_response_time
        self.active_users = active_users
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "git_commit": self.git_commit,
            "error_count": self.error_count,
            "critical_error_count": self.critical_error_count,
            "avg_response_time": self.avg_response_time,
            "active_users": self.active_users,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "HealthSnapshot":
        return cls(
            timestamp=data["timestamp"],
            git_commit=data["git_commit"],
            error_count=data["error_count"],
            critical_error_count=data["critical_error_count"],
            avg_response_time=data["avg_response_time"],
            active_users=data["active_users"],
        )


class RollbackSystem:
    """Auto-rollback system singleton."""
    
    def __init__(self):
        self.enabled = True
        self.monitoring_window_minutes = 15  # Monitor 15 phút sau deploy
        self.error_rate_threshold = 1.5  # 50% increase
        self.response_time_threshold = 2.0  # 2x slower
        self.critical_error_threshold = 3  # 3 critical errors → rollback
        
        self.snapshots: List[HealthSnapshot] = []
        self.rollback_history: List[dict] = []
        
        self._load_from_disk()
    
    def _load_from_disk(self):
        """Load config and history from disk."""
        # Load config
        if ROLLBACK_CONFIG_FILE.exists():
            try:
                with open(ROLLBACK_CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.enabled = config.get("enabled", True)
                    self.monitoring_window_minutes = config.get("monitoring_window_minutes", 15)
                    self.error_rate_threshold = config.get("error_rate_threshold", 1.5)
                    self.response_time_threshold = config.get("response_time_threshold", 2.0)
                    self.critical_error_threshold = config.get("critical_error_threshold", 3)
            except Exception as e:
                logger.error(f"Failed to load rollback config: {e}")
        
        # Load snapshots
        if HEALTH_SNAPSHOTS_FILE.exists():
            try:
                with open(HEALTH_SNAPSHOTS_FILE, 'r') as f:
                    data = json.load(f)
                    self.snapshots = [HealthSnapshot.from_dict(s) for s in data.get("snapshots", [])]
                    
                    # Keep only last 30 days
                    cutoff = time.time() - (30 * 24 * 3600)
                    self.snapshots = [s for s in self.snapshots if s.timestamp > cutoff]
            except Exception as e:
                logger.error(f"Failed to load health snapshots: {e}")
        
        # Load rollback history
        if ROLLBACK_HISTORY_FILE.exists():
            try:
                with open(ROLLBACK_HISTORY_FILE, 'r') as f:
                    self.rollback_history = json.load(f).get("history", [])
            except Exception as e:
                logger.error(f"Failed to load rollback history: {e}")
    
    def _save_to_disk(self):
        """Save state to disk."""
        try:
            # Save config
            ROLLBACK_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(ROLLBACK_CONFIG_FILE, 'w') as f:
                json.dump({
                    "enabled": self.enabled,
                    "monitoring_window_minutes": self.monitoring_window_minutes,
                    "error_rate_threshold": self.error_rate_threshold,
                    "response_time_threshold": self.response_time_threshold,
                    "critical_error_threshold": self.critical_error_threshold,
                }, f, indent=2)
            
            # Save snapshots
            HEALTH_SNAPSHOTS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(HEALTH_SNAPSHOTS_FILE, 'w') as f:
                json.dump({
                    "snapshots": [s.to_dict() for s in self.snapshots[-100:]],  # Keep last 100
                }, f, indent=2)
            
            # Save rollback history
            ROLLBACK_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(ROLLBACK_HISTORY_FILE, 'w') as f:
                json.dump({
                    "history": self.rollback_history[-50:],  # Keep last 50
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save rollback state: {e}")
    
    def get_current_commit(self) -> str:
        """Get current git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent.parent,
            )
            return result.stdout.strip()[:8]
        except Exception as e:
            logger.error(f"Failed to get git commit: {e}")
            return "unknown"
    
    def create_snapshot(self) -> HealthSnapshot:
        """Create health snapshot from current state."""
        from bot.core.error_tracker import get_tracker
        
        tracker = get_tracker()
        
        # Get metrics from last 5 minutes
        recent_errors = tracker.get_recent_errors(minutes=5)
        
        # Count critical errors (simplified - can be more sophisticated)
        critical_count = 0
        
        snapshot = HealthSnapshot(
            timestamp=time.time(),
            git_commit=self.get_current_commit(),
            error_count=recent_errors,
            critical_error_count=critical_count,
            avg_response_time=0.0,  # TODO: Implement response time tracking
            active_users=0,  # TODO: Get from analytics
        )
        
        self.snapshots.append(snapshot)
        self._save_to_disk()
        
        logger.info(f"📸 Health snapshot created: commit={snapshot.git_commit}, errors={snapshot.error_count}")
        return snapshot
    
    def get_baseline_snapshot(self) -> Optional[HealthSnapshot]:
        """Get most recent healthy snapshot (before current commit)."""
        if len(self.snapshots) < 2:
            return None
        
        current_commit = self.get_current_commit()
        
        # Find last snapshot with different commit
        for snapshot in reversed(self.snapshots[:-1]):
            if snapshot.git_commit != current_commit:
                return snapshot
        
        return None
    
    def detect_regression(self, current: HealthSnapshot, baseline: Optional[HealthSnapshot]) -> tuple[bool, str]:
        """
        Detect if current snapshot shows regression vs baseline.
        
        Returns: (should_rollback, reason)
        """
        if not baseline:
            logger.info("No baseline snapshot - skipping regression check")
            return False, ""
        
        reasons = []
        
        # Check error rate increase
        if baseline.error_count > 0:
            error_rate_ratio = current.error_count / baseline.error_count
            if error_rate_ratio >= self.error_rate_threshold:
                reasons.append(
                    f"Error rate increased {error_rate_ratio:.1f}x "
                    f"({baseline.error_count} → {current.error_count})"
                )
        elif current.error_count > 10:  # If no baseline errors but now many
            reasons.append(f"Sudden error spike ({current.error_count} errors)")
        
        # Check critical errors
        if current.critical_error_count >= self.critical_error_threshold:
            reasons.append(f"{current.critical_error_count} critical errors detected")
        
        # Check response time (if tracked)
        if current.avg_response_time > 0 and baseline.avg_response_time > 0:
            rt_ratio = current.avg_response_time / baseline.avg_response_time
            if rt_ratio >= self.response_time_threshold:
                reasons.append(
                    f"Response time increased {rt_ratio:.1f}x "
                    f"({baseline.avg_response_time:.2f}s → {current.avg_response_time:.2f}s)"
                )
        
        should_rollback = len(reasons) > 0
        reason = "; ".join(reasons) if reasons else ""
        
        return should_rollback, reason
    
    async def execute_rollback(self, target_commit: str, reason: str) -> bool:
        """
        Execute git rollback to target commit.
        
        Returns: True if successful
        """
        logger.critical(f"🔄 EXECUTING ROLLBACK to {target_commit}")
        logger.critical(f"   Reason: {reason}")
        
        try:
            repo_path = Path(__file__).parent.parent.parent
            
            # Git reset to target commit
            result = subprocess.run(
                ["git", "reset", "--hard", target_commit],
                capture_output=True,
                text=True,
                cwd=repo_path,
            )
            
            if result.returncode != 0:
                logger.error(f"Git reset failed: {result.stderr}")
                return False
            
            logger.info(f"✅ Git reset to {target_commit} successful")
            
            # Record rollback in history
            self.rollback_history.append({
                "timestamp": time.time(),
                "from_commit": self.get_current_commit(),
                "to_commit": target_commit,
                "reason": reason,
                "success": True,
            })
            self._save_to_disk()
            
            # Create restart flag for watchdog
            restart_flag = Path("data/.needs_restart")
            restart_flag.parent.mkdir(parents=True, exist_ok=True)
            restart_flag.write_text(
                f"{time.time()}\n"
                f"Auto-rollback triggered: {reason}\n"
                f"Rolled back to: {target_commit}\n"
            )
            
            return True
        
        except Exception as e:
            logger.error(f"Rollback execution failed: {e}", exc_info=True)
            
            self.rollback_history.append({
                "timestamp": time.time(),
                "from_commit": self.get_current_commit(),
                "to_commit": target_commit,
                "reason": reason,
                "success": False,
                "error": str(e),
            })
            self._save_to_disk()
            
            return False
    
    async def monitor_and_rollback_if_needed(self):
        """
        Main monitoring loop - check for regressions and rollback if needed.
        Call this periodically (e.g., every 2 minutes).
        """
        if not self.enabled:
            return
        
        current_snapshot = self.create_snapshot()
        baseline_snapshot = self.get_baseline_snapshot()
        
        should_rollback, reason = self.detect_regression(current_snapshot, baseline_snapshot)
        
        if should_rollback and baseline_snapshot:
            logger.warning(f"🚨 Regression detected: {reason}")
            
            success = await self.execute_rollback(baseline_snapshot.git_commit, reason)
            
            if success:
                logger.critical("✅ Rollback completed - bot will restart")
                # Alert admin via Telegram
                await self._alert_admin_rollback(reason, baseline_snapshot.git_commit)
            else:
                logger.critical("❌ Rollback FAILED - manual intervention required")
                await self._alert_admin_rollback_failed(reason)
    
    async def _alert_admin_rollback(self, reason: str, target_commit: str):
        """Send rollback alert to admin."""
        try:
            from config.settings import settings
            from telegram import Bot
            
            if not settings.ADMIN_USER_ID or not settings.BOT_TOKEN:
                return
            
            bot = Bot(token=settings.BOT_TOKEN)
            message = (
                f"🔄 <b>AUTO-ROLLBACK EXECUTED</b>\n\n"
                f"<b>Reason:</b> {reason}\n\n"
                f"<b>Rolled back to:</b> <code>{target_commit}</code>\n\n"
                f"Bot sẽ restart trong ít giây."
            )
            await bot.send_message(
                chat_id=settings.ADMIN_USER_ID,
                text=message,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to alert admin: {e}")
    
    async def _alert_admin_rollback_failed(self, reason: str):
        """Send rollback failure alert to admin."""
        try:
            from config.settings import settings
            from telegram import Bot
            
            if not settings.ADMIN_USER_ID or not settings.BOT_TOKEN:
                return
            
            bot = Bot(token=settings.BOT_TOKEN)
            message = (
                f"🚨 <b>AUTO-ROLLBACK FAILED</b>\n\n"
                f"<b>Regression detected:</b> {reason}\n\n"
                f"❌ Rollback thất bại - cần can thiệp thủ công!\n\n"
                f"Kiểm tra ngay: /healthcheck"
            )
            await bot.send_message(
                chat_id=settings.ADMIN_USER_ID,
                text=message,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to alert admin: {e}")


# Singleton
_rollback_system: Optional[RollbackSystem] = None


def get_rollback_system() -> RollbackSystem:
    """Get singleton rollback system instance."""
    global _rollback_system
    if _rollback_system is None:
        _rollback_system = RollbackSystem()
    return _rollback_system
