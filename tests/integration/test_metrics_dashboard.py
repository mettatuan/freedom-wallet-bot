"""
Test Phase 2 Metrics Dashboard
Tests metrics calculation and Telegram formatting
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from bot.services.metrics_service import metrics_service
from loguru import logger


def test_metrics_calculation():
    """Test: Calculate all 6 metrics"""
    logger.info("━━━ TEST 1: Metrics Calculation ━━━")
    
    try:
        # Calculate metrics
        metrics = metrics_service.get_all_metrics(force_refresh=True)
        
        # Verify structure
        assert 'timestamp' in metrics, "Missing timestamp"
        assert 'free' in metrics, "Missing FREE metrics"
        assert 'vip' in metrics, "Missing VIP metrics"
        assert 'premium' in metrics, "Missing PREMIUM metrics"
        assert 'overall_status' in metrics, "Missing overall status"
        
        # Verify FREE metrics
        free = metrics['free']
        assert 'retention_30day' in free, "Missing FREE retention"
        assert 'transactions_per_user' in free, "Missing FREE transactions"
        assert 'status' in free, "Missing FREE status"
        
        # Verify VIP metrics
        vip = metrics['vip']
        assert 'weekly_active_pct' in vip, "Missing VIP weekly active"
        assert 'premium_conversion_pct' in vip, "Missing VIP conversion"
        assert 'status' in vip, "Missing VIP status"
        
        # Verify PREMIUM metrics
        premium = metrics['premium']
        assert 'ai_usage_avg' in premium, "Missing PREMIUM AI usage"
        assert 'churn_90day_pct' in premium, "Missing PREMIUM churn"
        assert 'status' in premium, "Missing PREMIUM status"
        
        # Display results
        logger.info("✅ All metrics calculated successfully")
        logger.info(f"📊 FREE: Retention={free['retention_30day']}%, Trans={free['transactions_per_user']}")
        logger.info(f"⭐ VIP: Active={vip['weekly_active_pct']}%, Premium={vip['premium_conversion_pct']}%")
        logger.info(f"💎 PREMIUM: AI={premium['ai_usage_avg']} msg, Churn={premium['churn_90day_pct']}%")
        logger.info(f"📈 Overall: {metrics['overall_status']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False


def test_telegram_formatting():
    """Test: Format message for Telegram"""
    logger.info("━━━ TEST 2: Telegram Formatting ━━━")
    
    try:
        # Get metrics
        metrics = metrics_service.get_all_metrics()
        
        # Format for Telegram
        message = metrics_service.format_telegram_message(metrics)
        
        # Verify message structure
        assert "PHASE 2 METRICS DASHBOARD" in message, "Missing title"
        assert "FREE TIER" in message, "Missing FREE section"
        assert "VIP TIER" in message, "Missing VIP section"
        assert "PREMIUM TIER" in message, "Missing PREMIUM section"
        assert "OVERALL STATUS" in message, "Missing overall status"
        assert "REMEMBER" in message, "Missing reminder section"
        
        # Verify no placeholder values
        assert "{" not in message or "}" not in message, "Unfilled placeholders found"
        
        # Display formatted message
        logger.info("✅ Message formatted successfully")
        logger.info(f"\n{message}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False


def test_cache_mechanism():
    """Test: Verify caching works"""
    logger.info("━━━ TEST 3: Cache Mechanism ━━━")
    
    try:
        import time
        
        # Clear cache
        metrics_service.cache.clear()
        
        # First call - should calculate
        start = time.time()
        metrics1 = metrics_service.get_all_metrics(force_refresh=True)
        first_duration = time.time() - start
        logger.info(f"First call: {first_duration:.3f}s (calculated)")
        
        # Second call - should use cache
        start = time.time()
        metrics2 = metrics_service.get_all_metrics()
        second_duration = time.time() - start
        logger.info(f"Second call: {second_duration:.3f}s (cached)")
        
        # Verify cache is faster
        assert second_duration < first_duration, "Cache not working (second call slower)"
        assert metrics1['timestamp'] == metrics2['timestamp'], "Different timestamps (cache miss)"
        
        # Force refresh
        start = time.time()
        metrics3 = metrics_service.get_all_metrics(force_refresh=True)
        third_duration = time.time() - start
        logger.info(f"Third call (force): {third_duration:.3f}s (recalculated)")
        
        # Verify forced refresh worked
        assert metrics3['timestamp'] != metrics1['timestamp'], "Force refresh failed"
        
        logger.info("✅ Cache mechanism working correctly")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False


def test_target_validation():
    """Test: Verify target met logic"""
    logger.info("━━━ TEST 4: Target Validation ━━━")
    
    try:
        metrics = metrics_service.get_all_metrics()
        
        # Check FREE targets
        free = metrics['free']
        logger.info(f"FREE Retention: {free['retention_30day']}% (Target: ≥50%) - {'✅' if free['retention_target_met'] else '❌'}")
        logger.info(f"FREE Trans: {free['transactions_per_user']} (Target: ≥10) - {'✅' if free['transactions_target_met'] else '❌'}")
        
        # Check VIP targets
        vip = metrics['vip']
        logger.info(f"VIP Active: {vip['weekly_active_pct']}% (Target: ≥70%) - {'✅' if vip['weekly_active_target_met'] else '❌'}")
        logger.info(f"VIP Conv: {vip['premium_conversion_pct']}% (Target: 25-35%) - {'✅' if vip['premium_conversion_target_met'] else '❌'}")
        
        # Check PREMIUM targets
        premium = metrics['premium']
        logger.info(f"PREMIUM AI: {premium['ai_usage_avg']} msg (Target: ≥10) - {'✅' if premium['ai_usage_target_met'] else '❌'}")
        logger.info(f"PREMIUM Churn: {premium['churn_90day_pct']}% (Target: <15%) - {'✅' if premium['churn_target_met'] else '❌'}")
        
        # Verify logic consistency
        targets_met = sum([
            free['retention_target_met'],
            free['transactions_target_met'],
            vip['weekly_active_target_met'],
            vip['premium_conversion_target_met'],
            premium['ai_usage_target_met'],
            premium['churn_target_met']
        ])
        
        expected_status = 'HEALTHY' if targets_met == 6 else 'WARNING' if targets_met >= 4 else 'CRITICAL'
        actual_status = metrics['overall_status']
        
        assert actual_status == expected_status, f"Status mismatch: expected {expected_status}, got {actual_status}"
        
        logger.info(f"✅ Overall Status: {actual_status} ({targets_met}/6 targets met)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False


def main():
    """Run all tests"""
    logger.info("\n" + "="*60)
    logger.info("📊 PHASE 2 METRICS DASHBOARD TEST SUITE")
    logger.info("="*60 + "\n")
    
    results = []
    
    # Test 1: Metrics Calculation
    results.append(("Metrics Calculation", test_metrics_calculation()))
    
    # Test 2: Telegram Formatting
    results.append(("Telegram Formatting", test_telegram_formatting()))
    
    # Test 3: Cache Mechanism
    results.append(("Cache Mechanism", test_cache_mechanism()))
    
    # Test 4: Target Validation
    results.append(("Target Validation", test_target_validation()))
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("📊 TEST SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"[TEST] {name}: {status}")
    
    logger.info("="*60)
    logger.info(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        logger.info("✅ ALL METRICS DASHBOARD TESTS PASSED!")
        logger.info("\n🚀 Next Steps:")
        logger.info("1. Setup Google Sheets with structure from PHASE2_DASHBOARD_DESIGN.md")
        logger.info("2. Test /admin_metrics command in Telegram")
        logger.info("3. Set up daily automatic updates (8 AM)")
        logger.info("4. Deploy on Feb 24 and start 60-day observation")
    else:
        logger.error(f"❌ {total - passed} test(s) failed")
        logger.error("Please fix issues before deployment")
    
    logger.info("="*60 + "\n")


if __name__ == "__main__":
    main()
