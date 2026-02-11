"""
Analytics Report - Query and display analytics insights

Usage: python analytics_report.py
"""
import sys
import io

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from bot.services.analytics import Analytics
from datetime import datetime, timedelta
import json


def print_section(title):
    """Print section header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def get_conversion_rates():
    """Calculate conversion rates"""
    events = Analytics.get_events()
    
    # Trial conversion: trial_started / chat_limit_hit
    limit_hits = len([e for e in events if e['event'] == 'chat_limit_hit'])
    trial_starts = len([e for e in events if e['event'] == 'trial_started'])
    trial_conversion = (trial_starts / limit_hits * 100) if limit_hits > 0 else 0
    
    # WOW moment engagement
    wow_sent = len([e for e in events if e['event'] == 'wow_moment_sent'])
    wow_viewed = len([e for e in events if e['event'] == 'wow_moment_viewed'])
    wow_dismissed = len([e for e in events if e['event'] == 'wow_moment_dismissed'])
    wow_engagement = (wow_viewed / wow_sent * 100) if wow_sent > 0 else 0
    
    # Trial reminder effectiveness
    reminder_sent = len([e for e in events if e['event'] == 'trial_reminder_sent'])
    reminder_viewed = len([e for e in events if e['event'] == 'trial_reminder_viewed'])
    reminder_upgrade = len([e for e in events if e['event'] == 'trial_reminder_upgrade_clicked'])
    reminder_ctr = (reminder_upgrade / reminder_sent * 100) if reminder_sent > 0 else 0
    
    # ROI dashboard engagement
    mystatus_views = len([e for e in events if e['event'] == 'mystatus_viewed'])
    roi_detail_views = len([e for e in events if e['event'] == 'roi_detail_viewed'])
    optimization_views = len([e for e in events if e['event'] == 'optimization_tips_viewed'])
    
    # Upgrade clicks
    upgrade_clicks = len([e for e in events if e['event'] == 'upgrade_from_status_clicked'])
    
    return {
        'trial_conversion': trial_conversion,
        'trial_starts': trial_starts,
        'limit_hits': limit_hits,
        'wow_sent': wow_sent,
        'wow_engagement': wow_engagement,
        'reminder_sent': reminder_sent,
        'reminder_ctr': reminder_ctr,
        'mystatus_views': mystatus_views,
        'roi_detail_views': roi_detail_views,
        'optimization_views': optimization_views,
        'upgrade_clicks': upgrade_clicks
    }


def get_top_users():
    """Get most active users"""
    events = Analytics.get_events()
    
    user_activity = {}
    for event in events:
        user_id = event['user_id']
        user_activity[user_id] = user_activity.get(user_id, 0) + 1
    
    # Sort by activity
    top_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return top_users


def get_recent_events(hours=24):
    """Get events from last N hours"""
    events = Analytics.get_events()
    
    cutoff = datetime.now() - timedelta(hours=hours)
    recent = []
    
    for event in events:
        event_time = datetime.fromisoformat(event['timestamp'])
        if event_time >= cutoff:
            recent.append(event)
    
    return recent


def main():
    """Generate analytics report"""
    
    print_section("📊 FREEDOM WALLET BOT - ANALYTICS REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Summary
    print_section("📈 SUMMARY")
    summary = Analytics.get_summary()
    print(f"Total Events: {summary['total_events']}")
    print(f"\nEvent Counts:")
    for event_name, count in sorted(summary['event_counts'].items()):
        print(f"  • {event_name}: {count}")
    
    # Conversion rates
    print_section("🎯 CONVERSION RATES")
    rates = get_conversion_rates()
    
    print(f"Trial Conversion: {rates['trial_conversion']:.1f}%")
    print(f"  └─ Limit Hits: {rates['limit_hits']}")
    print(f"  └─ Trial Starts: {rates['trial_starts']}")
    
    print(f"\nWOW Moment Engagement: {rates['wow_engagement']:.1f}%")
    print(f"  └─ Sent: {rates['wow_sent']}")
    
    print(f"\nTrial Reminder CTR: {rates['reminder_ctr']:.1f}%")
    print(f"  └─ Sent: {rates['reminder_sent']}")
    
    print(f"\n/mystatus Views: {rates['mystatus_views']}")
    print(f"  └─ ROI Detail: {rates['roi_detail_views']}")
    print(f"  └─ Optimization: {rates['optimization_views']}")
    
    print(f"\nUpgrade Clicks: {rates['upgrade_clicks']}")
    
    # Top users
    print_section("👥 TOP 10 ACTIVE USERS")
    top_users = get_top_users()
    for i, (user_id, count) in enumerate(top_users, 1):
        print(f"{i:2d}. User {user_id}: {count} events")
    
    # Recent activity
    print_section("🕐 LAST 24 HOURS")
    recent = get_recent_events(24)
    print(f"Events in last 24h: {len(recent)}")
    
    if recent:
        print("\nRecent events:")
        for event in recent[-10:]:  # Last 10 events
            timestamp = datetime.fromisoformat(event['timestamp']).strftime('%H:%M:%S')
            print(f"  [{timestamp}] User {event['user_id']}: {event['event']}")
    
    # Insights
    print_section("💡 INSIGHTS")
    
    if rates['trial_conversion'] < 30:
        print("⚠️  Trial conversion is low (<30%). Consider:")
        print("   • Stronger CTA messaging")
        print("   • Better value proposition")
        print("   • Social proof (testimonials)")
    
    if rates['wow_engagement'] < 50 and rates['wow_sent'] > 0:
        print("⚠️  WOW moment engagement is low. Consider:")
        print("   • More compelling copy")
        print("   • Visual improvements")
        print("   • Better timing (not exactly 24h?)")
    
    if rates['reminder_ctr'] < 20 and rates['reminder_sent'] > 0:
        print("⚠️  Trial reminder CTR is low. Consider:")
        print("   • Urgency improvements")
        print("   • Better incentives")
        print("   • Risk reversal (money-back guarantee?)")
    
    if rates['mystatus_views'] > 0:
        roi_rate = (rates['roi_detail_views'] / rates['mystatus_views'] * 100)
        if roi_rate > 30:
            print(f"✅ Good ROI detail engagement ({roi_rate:.0f}%)")
        else:
            print(f"⚠️  Low ROI detail clicks ({roi_rate:.0f}%). Make button more prominent?")
    
    print("\n" + "=" * 60)
    print("Report Complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
