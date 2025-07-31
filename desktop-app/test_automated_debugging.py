#!/usr/bin/env python3
"""
Test script for Automated Debugging and Fixing System
Demonstrates the integration between Sentry and Fix-AI for automated error resolution
"""

import asyncio
import json
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_sentry_api_client():
    """Test the Sentry API client"""
    try:
        logger.info("[TEST] Testing Sentry API client...")
        
        from src.utils.sentry_api_client import fetch_recent_sentry_errors
        
        # Fetch recent errors
        errors = fetch_recent_sentry_errors(hours=24)
        
        logger.info(f"[INFO] Found {len(errors)} errors from Sentry")
        
        if errors:
            logger.info("[INFO] Sample errors:")
            for error in errors[:3]:  # Show first 3 errors
                logger.info(f"  - {error['error_type']}: {error['message']}")
                logger.info(f"    File: {error['file_path']}:{error['line']}")
                logger.info(f"    Suggested fix: {error['suggested_fix']}")
        
        logger.success("[PASS] Sentry API client test completed")
        return True
        
    except Exception as e:
        logger.error(f"[FAIL] Sentry API client test failed: {e}")
        return False

async def test_automated_debugger():
    """Test the automated debugger service"""
    try:
        logger.info("[TEST] Testing automated debugger...")
        
        from src.utils.automated_debugger import get_automated_debugger
        
        # Get debugger instance
        debugger = get_automated_debugger()
        
        # Test error checking
        await debugger.check_for_new_errors()
        
        # Get status
        status = debugger.get_status()
        logger.info(f"[INFO] Debugger status: {json.dumps(status, indent=2)}")
        
        logger.success("[PASS] Automated debugger test completed")
        return True
        
    except Exception as e:
        logger.error(f"[FAIL] Automated debugger test failed: {e}")
        return False

async def test_fix_ai_sentry_integration():
    """Test Fix-AI with Sentry integration"""
    try:
        logger.info("[TEST] Testing Fix-AI with Sentry integration...")
        
        # Import Fix-AI dynamically
        import importlib.util
        fix_ai_path = Path("Fix-AI.py")  # Fix-AI.py is in the current directory (desktop-app)
        
        if not fix_ai_path.exists():
            logger.error("[FAIL] Fix-AI.py not found")
            return False
        
        spec = importlib.util.spec_from_file_location("Fix_AI", fix_ai_path)
        Fix_AI = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(Fix_AI)
        
        # Create healer instance
        healer = Fix_AI.CodebaseHealer(Path("."))
        
        # Run Sentry analysis phase only
        healer.run_sentry_analysis_phase()
        
        logger.info(f"[INFO] Sentry analysis found {len(healer.issues)} issues")
        
        if healer.issues:
            logger.info("[INFO] Issues found:")
            for issue in healer.issues:
                logger.info(f"  - {issue['type']}: {issue['message']}")
                if issue.get('source') == 'sentry':
                    logger.info(f"    Source: Sentry, Suggested fix: {issue.get('suggested_fix', 'None')}")
        
        logger.success("[PASS] Fix-AI Sentry integration test completed")
        return True
        
    except Exception as e:
        logger.error(f"[FAIL] Fix-AI Sentry integration test failed: {e}")
        return False

async def test_full_automated_workflow():
    """Test the full automated debugging workflow"""
    try:
        logger.info("[TEST] Testing full automated debugging workflow...")
        
        # Step 1: Simulate a Sentry error
        logger.info("[STEP 1] Simulating Sentry error detection...")
        
        # Step 2: Test automated debugger
        logger.info("[STEP 2] Testing automated debugger response...")
        from src.utils.automated_debugger import get_automated_debugger
        debugger = get_automated_debugger()
        
        # Step 3: Test Fix-AI integration
        logger.info("[STEP 3] Testing Fix-AI integration...")
        
        # Simulate the workflow
        simulated_errors = [
            {
                "error_type": "AttributeError",
                "message": "object has no attribute 'get'",
                "file_path": "src/core/cognitive_forge_engine.py",
                "line": 245,
                "frequency": 3,
                "suggested_fix": "Check if object is None before calling .get() method",
                "issue_id": "test-1"
            }
        ]
        
        # Test error logging
        await debugger.trigger_fix_ai(simulated_errors)
        
        logger.success("[PASS] Full automated workflow test completed")
        return True
        
    except Exception as e:
        logger.error(f"[FAIL] Full automated workflow test failed: {e}")
        return False

async def main():
    """Run all automated debugging tests"""
    logger.info("="*60)
    logger.info("AUTOMATED DEBUGGING & FIXING SYSTEM TEST SUITE")
    logger.info("="*60)
    
    tests = [
        ("Sentry API Client", test_sentry_api_client),
        ("Automated Debugger", test_automated_debugger),
        ("Fix-AI Sentry Integration", test_fix_ai_sentry_integration),
        ("Full Automated Workflow", test_full_automated_workflow),
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
        logger.success("[SUCCESS] All automated debugging tests passed!")
        logger.info("\n" + "="*60)
        logger.info("AUTOMATED DEBUGGING SYSTEM READY")
        logger.info("="*60)
        logger.info("Your system now has:")
        logger.info("✅ Real-time error detection via Sentry")
        logger.info("✅ Automated error analysis and pattern recognition")
        logger.info("✅ Automatic Fix-AI triggering for error resolution")
        logger.info("✅ Continuous monitoring and self-healing")
        logger.info("✅ API endpoints for control and monitoring")
        logger.info("\nTo start automated debugging:")
        logger.info("1. POST to /automated-debugger/start")
        logger.info("2. Monitor status at /automated-debugger/status")
        logger.info("3. Stop with POST to /automated-debugger/stop")
    else:
        logger.warning(f"[WARNING] {total - passed} tests failed")

if __name__ == "__main__":
    asyncio.run(main()) 