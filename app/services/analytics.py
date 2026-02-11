"""
Analytics Tracking - Simple event logging for metrics
Tracks: chat_limit_hit, trial_started, menu clicks, etc.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from loguru import logger


class Analytics:
    """Simple analytics tracker using JSON file logging"""
    
    ANALYTICS_DIR = Path("data/analytics")
    ANALYTICS_FILE = ANALYTICS_DIR / "events.jsonl"
    
    @staticmethod
    def init():
        """Initialize analytics directory"""
        Analytics.ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
        
        if not Analytics.ANALYTICS_FILE.exists():
            Analytics.ANALYTICS_FILE.touch()
            logger.info(f"Created analytics file: {Analytics.ANALYTICS_FILE}")
    
    @staticmethod
    def track_event(user_id: int, event_name: str, properties: Optional[Dict] = None):
        """
        Track an analytics event
        
        Args:
            user_id: User ID
            event_name: Event name (e.g., 'chat_limit_hit')
            properties: Optional event properties
        
        Events to track:
        
        RETENTION EVENTS:
        - chat_limit_hit: FREE user hits 5 msg limit
        - trial_started: User starts trial
        - wow_moment_sent: 24h WOW moment sent
        - wow_moment_viewed: User clicked WOW moment notification
        - wow_moment_dismissed: User dismissed without action
        - trial_reminder_sent: Day-6 reminder sent
        - trial_reminder_viewed: User opened reminder
        - trial_reminder_upgrade_clicked: User clicked upgrade from reminder
        
        ROI DASHBOARD EVENTS:
        - mystatus_viewed: User opened /mystatus
        - roi_detail_viewed: User clicked "Xem ROI chi tiáº¿t"
        - optimization_tips_viewed: User clicked "Tá»‘i Æ°u sá»­ dá»¥ng"
        - upgrade_from_status_clicked: User clicked upgrade from /mystatus
        
        MENU EVENTS:
        - premium_menu_opened: User opened Premium menu
        - menu_expense_clicked: User clicked "Ghi chi tiÃªu"
        - menu_summary_clicked: User clicked "TÃ¬nh hÃ¬nh"
        - menu_analysis_clicked: User clicked "PhÃ¢n tÃ­ch"
        - menu_recommendation_clicked: User clicked "Gá»£i Ã½"
        - menu_setup_clicked: User clicked "Setup"
        - menu_support_clicked: User clicked "Há»— trá»£"
        
        GENERAL:
        - message_sent: User sends message
        """
        Analytics.init()
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'event': event_name,
            'properties': properties or {}
        }
        
        try:
            with open(Analytics.ANALYTICS_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event, ensure_ascii=False) + '\n')
            
            logger.debug(f"Analytics: {event_name} for user {user_id}")
        
        except Exception as e:
            logger.error(f"Failed to track event {event_name}: {e}")
    
    @staticmethod
    def get_events(event_name: Optional[str] = None, user_id: Optional[int] = None) -> list:
        """
        Get tracked events (for analysis)
        
        Args:
            event_name: Filter by event name
            user_id: Filter by user ID
        
        Returns:
            List of events
        """
        if not Analytics.ANALYTICS_FILE.exists():
            return []
        
        events = []
        
        try:
            with open(Analytics.ANALYTICS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        event = json.loads(line)
                        
                        # Apply filters
                        if event_name and event.get('event') != event_name:
                            continue
                        
                        if user_id and event.get('user_id') != user_id:
                            continue
                        
                        events.append(event)
        
        except Exception as e:
            logger.error(f"Failed to read events: {e}")
        
        return events
    
    @staticmethod
    def get_metric(metric_name: str) -> float:
        """
        Calculate key metrics
        
        Metrics:
        - trial_conversion: % of chat_limit_hit â†’ trial_started
        - premium_dau: Daily active Premium users
        - recommendation_ctr: % Premium users clicking "Gá»£i Ã½"
        """
        events = Analytics.get_events()
        
        if metric_name == 'trial_conversion':
            # Calculate: trial_started / chat_limit_hit
            limit_hits = len([e for e in events if e['event'] == 'chat_limit_hit'])
            trial_starts = len([e for e in events if e['event'] == 'trial_started'])
            
            if limit_hits == 0:
                return 0.0
            
            return (trial_starts / limit_hits) * 100
        
        elif metric_name == 'recommendation_ctr':
            # Calculate: recommendation_clicked / premium_users
            # This is simplified - real version would track unique users
            menu_opens = len([e for e in events if e['event'] == 'premium_menu_opened'])
            rec_clicks = len([e for e in events if e['event'] == 'recommendation_clicked'])
            
            if menu_opens == 0:
                return 0.0
            
            return (rec_clicks / menu_opens) * 100
        
        return 0.0
    
    @staticmethod
    def get_summary() -> Dict:
        """Get analytics summary"""
        events = Analytics.get_events()
        
        # Count event types
        event_counts = {}
        for event in events:
            event_name = event['event']
            event_counts[event_name] = event_counts.get(event_name, 0) + 1
        
        # Calculate key metrics
        trial_conversion = Analytics.get_metric('trial_conversion')
        recommendation_ctr = Analytics.get_metric('recommendation_ctr')
        
        return {
            'total_events': len(events),
            'event_counts': event_counts,
            'metrics': {
                'trial_conversion': f"{trial_conversion:.1f}%",
                'recommendation_ctr': f"{recommendation_ctr:.1f}%"
            }
        }


# Initialize on import
Analytics.init()

