"""
Auto-Fix Metrics Tracker — Thu thập và phân tích thống kê auto-fix.

Lưu trữ:
  - Số lần mỗi handler được gọi
  - Success rate của từng handler
  - Thời gian trung bình để fix
  - Lịch sử fixes trong 24h, 7 ngày, 30 ngày

Admin commands:
  /autofix_stats — Xem tổng quan auto-fix metrics
  /autofix_history — Xem lịch sử fixes gần đây
"""

import json
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

METRICS_FILE = Path("data/metrics/autofix_metrics.json")


class AutoFixMetrics:
    """Singleton metrics tracker."""
    
    def __init__(self):
        # {handler_name: {"attempts": int, "successes": int, "failures": int}}
        self.handler_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {
            "attempts": 0,
            "successes": 0,
            "failures": 0,
            "total_duration": 0.0,
        })
        
        # List of recent fixes: [{"timestamp": float, "handler": str, "success": bool, "duration": float}, ...]
        self.fix_history: List[Dict] = []
        
        self._load_from_disk()
    
    def _load_from_disk(self):
        """Load metrics from disk."""
        if not METRICS_FILE.exists():
            return
        
        try:
            with open(METRICS_FILE, 'r') as f:
                data = json.load(f)
                self.handler_stats = defaultdict(lambda: {
                    "attempts": 0,
                    "successes": 0,
                    "failures": 0,
                    "total_duration": 0.0,
                }, data.get("handler_stats", {}))
                self.fix_history = data.get("fix_history", [])
                
                # Clean old history (keep last 7 days)
                cutoff = time.time() - (7 * 24 * 3600)
                self.fix_history = [h for h in self.fix_history if h.get("timestamp", 0) > cutoff]
                
                logger.info(f"📊 Loaded auto-fix metrics: {len(self.handler_stats)} handlers, {len(self.fix_history)} history entries")
        except Exception as e:
            logger.error(f"Failed to load metrics: {e}")
    
    def _save_to_disk(self):
        """Save metrics to disk."""
        try:
            METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(METRICS_FILE, 'w') as f:
                json.dump({
                    "handler_stats": dict(self.handler_stats),
                    "fix_history": self.fix_history[-1000:],  # Keep last 1000 entries
                    "last_updated": time.time(),
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def record_attempt(self, handler_name: str, success: bool, duration: float):
        """Record an auto-fix attempt."""
        self.handler_stats[handler_name]["attempts"] += 1
        
        if success:
            self.handler_stats[handler_name]["successes"] += 1
        else:
            self.handler_stats[handler_name]["failures"] += 1
        
        self.handler_stats[handler_name]["total_duration"] += duration
        
        # Add to history
        self.fix_history.append({
            "timestamp": time.time(),
            "handler": handler_name,
            "success": success,
            "duration": duration,
        })
        
        # Save periodically (every 10 attempts)
        if sum(s["attempts"] for s in self.handler_stats.values()) % 10 == 0:
            self._save_to_disk()
    
    def get_success_rate(self, handler_name: str) -> float:
        """Get success rate (0-100) for a handler."""
        stats = self.handler_stats.get(handler_name)
        if not stats or stats["attempts"] == 0:
            return 0.0
        return (stats["successes"] / stats["attempts"]) * 100
    
    def get_avg_duration(self, handler_name: str) -> float:
        """Get average duration (seconds) for a handler."""
        stats = self.handler_stats.get(handler_name)
        if not stats or stats["attempts"] == 0:
            return 0.0
        return stats["total_duration"] / stats["attempts"]
    
    def get_recent_fixes(self, hours: int = 24) -> List[Dict]:
        """Get fixes in last N hours."""
        cutoff = time.time() - (hours * 3600)
        return [h for h in self.fix_history if h.get("timestamp", 0) > cutoff]
    
    def get_summary_report(self) -> str:
        """Generate summary report for admin."""
        if not self.handler_stats:
            return "📊 <b>Auto-Fix Metrics</b>\n\nChưa có dữ liệu."
        
        lines = ["📊 <b>AUTO-FIX METRICS</b>\n"]
        
        # Overall stats
        total_attempts = sum(s["attempts"] for s in self.handler_stats.values())
        total_successes = sum(s["successes"] for s in self.handler_stats.values())
        overall_success_rate = (total_successes / total_attempts * 100) if total_attempts > 0 else 0
        
        lines.append(f"<b>Tổng quan:</b>")
        lines.append(f"  • Tổng lần fix: {total_attempts}")
        lines.append(f"  • Thành công: {total_successes} ({overall_success_rate:.1f}%)")
        lines.append(f"  • Thất bại: {total_attempts - total_successes}")
        
        # Recent activity
        recent_1h = len(self.get_recent_fixes(1))
        recent_24h = len(self.get_recent_fixes(24))
        lines.append(f"\n<b>Hoạt động gần đây:</b>")
        lines.append(f"  • 1 giờ qua: {recent_1h} fixes")
        lines.append(f"  • 24 giờ qua: {recent_24h} fixes")
        
        # Per-handler breakdown
        lines.append(f"\n<b>Chi tiết theo handler:</b>")
        
        sorted_handlers = sorted(
            self.handler_stats.items(),
            key=lambda x: x[1]["attempts"],
            reverse=True
        )
        
        for handler_name, stats in sorted_handlers[:10]:  # Top 10
            success_rate = self.get_success_rate(handler_name)
            avg_duration = self.get_avg_duration(handler_name)
            
            # Shorten handler name
            short_name = handler_name.replace("fix_", "").replace("_", " ").title()
            
            lines.append(
                f"\n  <b>{short_name}</b>\n"
                f"    Attempts: {stats['attempts']} | "
                f"Success: {success_rate:.1f}% | "
                f"Avg: {avg_duration:.2f}s"
            )
        
        return "\n".join(lines)
    
    def get_history_report(self, limit: int = 20) -> str:
        """Generate history report for admin."""
        if not self.fix_history:
            return "📜 <b>Auto-Fix History</b>\n\nChưa có lịch sử."
        
        lines = ["📜 <b>AUTO-FIX HISTORY</b>\n"]
        
        recent = sorted(self.fix_history, key=lambda x: x["timestamp"], reverse=True)[:limit]
        
        for entry in recent:
            timestamp = datetime.fromtimestamp(entry["timestamp"]).strftime("%H:%M:%S")
            handler = entry["handler"].replace("fix_", "").replace("_", " ").title()
            status = "✅" if entry["success"] else "❌"
            duration = entry["duration"]
            
            lines.append(
                f"{timestamp} | {status} <b>{handler}</b> ({duration:.2f}s)"
            )
        
        return "\n".join(lines)


# Singleton instance
_metrics: Optional[AutoFixMetrics] = None


def get_metrics() -> AutoFixMetrics:
    """Get singleton metrics instance."""
    global _metrics
    if _metrics is None:
        _metrics = AutoFixMetrics()
    return _metrics
