#!/usr/bin/env python3
"""
Test script for Fix-AI: The Sentient Codebase Healer
"""

import asyncio
import json
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_fix_ai_availability():
    """Test if Fix-AI is available and can be imported"""
    try:
        logger.info("[TEST] Testing Fix-AI availability...")
        
        # Check if Fix-AI.py exists
        fix_ai_path = Path("Fix-AI.py")
        if not fix_ai_path.exists():
            logger.error("[FAIL] Fix-AI.py not found in current directory")
            return False
        
        logger.success("[PASS] Fix-AI.py found")
        
        # Try to import Fix-AI
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("Fix_AI", "Fix-AI.py")
            Fix_AI = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(Fix_AI)
            CodebaseHealer = Fix_AI.CodebaseHealer
            logger.success("[PASS] Fix-AI imported successfully")
            return True
        except ImportError as e:
            logger.error(f"[FAIL] Failed to import Fix-AI: {e}")
            return False
            
    except Exception as e:
        logger.error(f"[FAIL] Fix-AI availability test failed: {e}")
        return False

async def test_guardian_protocol_integration():
    """Test Guardian Protocol integration with Fix-AI"""
    try:
        logger.info("[TEST] Testing Guardian Protocol Fix-AI integration...")
        
        # Import Guardian Protocol
        from src.utils.guardian_protocol import GuardianProtocol
        from src.utils.google_ai_wrapper import create_google_ai_llm
        
        # Initialize LLM
        llm = create_google_ai_llm()
        
        # Initialize Guardian Protocol
        guardian = GuardianProtocol(llm)
        
        # Check Fix-AI availability
        fix_ai_available = guardian.fix_ai_available
        logger.info(f"[INFO] Fix-AI available: {fix_ai_available}")
        
        if fix_ai_available:
            logger.success("[PASS] Guardian Protocol can access Fix-AI")
            
            # Test system status
            status = guardian.get_system_status()
            logger.info(f"[INFO] Guardian Protocol status: {json.dumps(status, indent=2)}")
            
            return True
        else:
            logger.warning("[WARN] Fix-AI not available in Guardian Protocol")
            return False
            
    except Exception as e:
        logger.error(f"[FAIL] Guardian Protocol integration test failed: {e}")
        return False

async def test_fix_ai_diagnosis():
    """Test Fix-AI diagnosis phase"""
    try:
        logger.info("[TEST] Testing Fix-AI diagnosis phase...")
        
        import importlib.util
        spec = importlib.util.spec_from_file_location("Fix_AI", "Fix-AI.py")
        Fix_AI = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(Fix_AI)
        CodebaseHealer = Fix_AI.CodebaseHealer
        
        # Create healer instance
        healer = CodebaseHealer(Path("."))
        
        # Run diagnosis phase only
        healer.run_diagnosis_phase()
        
        logger.info(f"[INFO] Found {len(healer.issues)} issues in codebase")
        
        if healer.issues:
            logger.info("[INFO] Sample issues found:")
            for issue in healer.issues[:3]:  # Show first 3 issues
                logger.info(f"  - {issue['type']}: {issue['message']} in {issue['file_path']}:{issue['line']}")
        
        logger.success("[PASS] Fix-AI diagnosis phase completed")
        return True
        
    except Exception as e:
        logger.error(f"[FAIL] Fix-AI diagnosis test failed: {e}")
        return False

async def main():
    """Run all Fix-AI tests"""
    logger.info("="*60)
    logger.info("FIX-AI TEST SUITE")
    logger.info("="*60)
    
    tests = [
        ("Fix-AI Availability", test_fix_ai_availability),
        ("Guardian Protocol Integration", test_guardian_protocol_integration),
        ("Fix-AI Diagnosis", test_fix_ai_diagnosis),
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
        logger.success("[SUCCESS] All Fix-AI tests passed!")
    else:
        logger.warning(f"[WARNING] {total - passed} tests failed")

if __name__ == "__main__":
    asyncio.run(main()) 