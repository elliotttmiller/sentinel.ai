#!/usr/bin/env python3
"""
Test script for Sentry Integration
"""

import asyncio
import json
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_sentry_availability():
    """Test if Sentry is available and can be imported"""
    try:
        logger.info("[TEST] Testing Sentry availability...")
        
        from src.utils.sentry_integration import SentryIntegration, initialize_sentry
        
        # Test initialization
        sentry = initialize_sentry(environment="test")
        
        if sentry.initialized:
            logger.success("[PASS] Sentry initialized successfully")
            return True
        else:
            logger.warning("[WARN] Sentry not available (no DSN configured)")
            return False
            
    except ImportError as e:
        logger.error(f"[FAIL] Sentry SDK not installed: {e}")
        return False
    except Exception as e:
        logger.error(f"[FAIL] Sentry availability test failed: {e}")
        return False

async def test_error_capture():
    """Test error capture functionality"""
    try:
        logger.info("[TEST] Testing error capture...")
        
        from src.utils.sentry_integration import get_sentry, capture_error
        
        sentry = get_sentry()
        if not sentry or not sentry.initialized:
            logger.warning("[WARN] Skipping error capture test - Sentry not available")
            return True
        
        # Test error capture
        test_error = ValueError("Test error for Sentry integration")
        capture_error(test_error, {
            "test": True,
            "component": "test_sentry_integration"
        })
        
        logger.success("[PASS] Error capture test completed")
        return True
        
    except Exception as e:
        logger.error(f"[FAIL] Error capture test failed: {e}")
        return False

async def test_performance_tracking():
    """Test performance tracking functionality"""
    try:
        logger.info("[TEST] Testing performance tracking...")
        
        from src.utils.sentry_integration import get_sentry, start_transaction
        
        sentry = get_sentry()
        if not sentry or not sentry.initialized:
            logger.warning("[WARN] Skipping performance tracking test - Sentry not available")
            return True
        
        # Test transaction tracking
        transaction = start_transaction("test_performance", "test")
        if transaction:
            # Simulate some work
            await asyncio.sleep(0.1)
            transaction.finish()
            logger.success("[PASS] Performance tracking test completed")
        else:
            logger.warning("[WARN] Transaction tracking not available")
        
        return True
        
    except Exception as e:
        logger.error(f"[FAIL] Performance tracking test failed: {e}")
        return False

async def test_learning_insights():
    """Test learning insights functionality"""
    try:
        logger.info("[TEST] Testing learning insights...")
        
        from src.utils.sentry_integration import get_sentry
        
        sentry = get_sentry()
        if not sentry or not sentry.initialized:
            logger.warning("[WARN] Skipping learning insights test - Sentry not available")
            return True
        
        # Add some test insights
        sentry.add_learning_insight({
            "type": "error_pattern",
            "pattern": "test_pattern",
            "frequency": 1,
            "suggested_fix": "test_fix"
        })
        
        # Get insights
        insights = sentry.get_error_insights()
        logger.info(f"[INFO] Learning insights: {json.dumps(insights, indent=2)}")
        
        logger.success("[PASS] Learning insights test completed")
        return True
        
    except Exception as e:
        logger.error(f"[FAIL] Learning insights test failed: {e}")
        return False

async def test_engine_integration():
    """Test Sentry integration with Cognitive Forge Engine"""
    try:
        logger.info("[TEST] Testing engine integration...")
        
        from src.core.cognitive_forge_engine import CognitiveForgeEngine
        
        # Initialize engine (this should initialize Sentry)
        engine = CognitiveForgeEngine()
        
        # Check if Sentry was initialized
        if hasattr(engine, 'sentry') and engine.sentry:
            logger.success("[PASS] Engine Sentry integration working")
            return True
        else:
            logger.warning("[WARN] Engine Sentry integration not available")
            return False
        
    except Exception as e:
        logger.error(f"[FAIL] Engine integration test failed: {e}")
        return False

async def main():
    """Run all Sentry integration tests"""
    logger.info("="*60)
    logger.info("SENTRY INTEGRATION TEST SUITE")
    logger.info("="*60)
    
    tests = [
        ("Sentry Availability", test_sentry_availability),
        ("Error Capture", test_error_capture),
        ("Performance Tracking", test_performance_tracking),
        ("Learning Insights", test_learning_insights),
        ("Engine Integration", test_engine_integration),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n[RUNNING] {test_name}")
        try:
            result = await test_func()
            results[test_name] = "PASS" if result else "FAIL"
        except Exception as e:
            logger.error(f"[ERROR] {test_name} failed with exception: {e}")
            results[test_name] = "ERROR"
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for result in results.values() if result == "PASS")
    total = len(results)
    
    for test_name, result in results.items():
        status_emoji = "[PASS]" if result == "PASS" else "[FAIL]" if result == "FAIL" else "[ERROR]"
        logger.info(f"{status_emoji} {test_name}: {result}")
    
    logger.info(f"\n[SUMMARY] {passed}/{total} tests passed")
    
    if passed == total:
        logger.success("[SUCCESS] All Sentry integration tests passed!")
    else:
        logger.warning(f"[WARNING] {total - passed} tests failed")
    
    # Provide setup instructions if Sentry is not available
    if "Sentry Availability" in results and results["Sentry Availability"] != "PASS":
        logger.info("\n" + "="*60)
        logger.info("SENTRY SETUP INSTRUCTIONS")
        logger.info("="*60)
        logger.info("1. Install Sentry SDK: pip install sentry-sdk")
        logger.info("2. Get your Sentry DSN from https://sentry.io")
        logger.info("3. Add SENTRY_DSN=your_dsn_here to your .env file")
        logger.info("4. Restart the application")

if __name__ == "__main__":
    asyncio.run(main()) 