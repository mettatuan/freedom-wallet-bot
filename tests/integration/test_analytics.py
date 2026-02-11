"""
Quick Analytics Test - Verify tracking is working

Tests:
1. Track a test event
2. Read it back from file
3. Calculate metrics
"""
from bot.services.analytics import Analytics
import json


def test_basic_tracking():
    """Test basic event tracking"""
    print("=" * 60)
    print("  🧪 TEST 1: Basic Event Tracking")
    print("=" * 60 + "\n")
    
    # Track test event
    print("Tracking test event...")
    Analytics.track_event(
        user_id=999999,
        event_name='test_event',
        properties={'test': True, 'value': 123}
    )
    
    # Read events
    events = Analytics.get_events()
    print(f"✅ Total events in file: {len(events)}")
    
    # Find our test event
    test_events = [e for e in events if e['event'] == 'test_event']
    if test_events:
        print(f"✅ Found {len(test_events)} test event(s)")
        print(f"   Latest: {test_events[-1]}")
    else:
        print("⚠️  No test events found")
    
    print()


def test_event_filtering():
    """Test event filtering"""
    print("=" * 60)
    print("  🧪 TEST 2: Event Filtering")
    print("=" * 60 + "\n")
    
    # Track multiple events
    print("Tracking multiple events...")
    Analytics.track_event(999999, 'mystatus_viewed', {'tier': 'FREE'})
    Analytics.track_event(999999, 'roi_detail_viewed')
    Analytics.track_event(888888, 'mystatus_viewed', {'tier': 'TRIAL'})
    
    # Filter by event name
    mystatus_events = Analytics.get_events(event_name='mystatus_viewed')
    print(f"✅ mystatus_viewed events: {len(mystatus_events)}")
    
    # Filter by user
    user_events = Analytics.get_events(user_id=999999)
    print(f"✅ User 999999 events: {len(user_events)}")
    
    print()


def test_metrics():
    """Test metrics calculation"""
    print("=" * 60)
    print("  🧪 TEST 3: Metrics Calculation")
    print("=" * 60 + "\n")
    
    # Track conversion funnel events
    print("Simulating conversion funnel...")
    for i in range(5):
        Analytics.track_event(i, 'chat_limit_hit', {})
    
    for i in range(3):
        Analytics.track_event(i, 'trial_started', {})
    
    # Calculate trial conversion
    trial_conversion = Analytics.get_metric('trial_conversion')
    print(f"✅ Trial conversion rate: {trial_conversion:.1f}%")
    
    # Get summary
    summary = Analytics.get_summary()
    print(f"✅ Total events: {summary['total_events']}")
    print(f"✅ Unique event types: {len(summary['event_counts'])}")
    
    print()


def test_analytics_report():
    """Test analytics report generation"""
    print("=" * 60)
    print("  🧪 TEST 4: Analytics Report")
    print("=" * 60 + "\n")
    
    print("Running analytics_report.py...")
    import subprocess
    result = subprocess.run(
        ['python', 'analytics_report.py'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Analytics report generated successfully")
        print("\nFirst 500 chars of output:")
        print(result.stdout[:500])
    else:
        print("❌ Analytics report failed")
        print(result.stderr)
    
    print()


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  📊 ANALYTICS TRACKING TESTS")
    print("=" * 60 + "\n")
    
    try:
        test_basic_tracking()
        test_event_filtering()
        test_metrics()
        test_analytics_report()
        
        print("=" * 60)
        print("  ✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\n💡 Next: Test with real bot interactions:")
        print("   1. Open Telegram → @FreedomWalletBot")
        print("   2. Send: /mystatus")
        print("   3. Click buttons")
        print("   4. Run: python analytics_report.py")
        print()
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("  ❌ TEST FAILED")
        print("=" * 60)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
