#!/usr/bin/env python3
"""
RUN OPTIMIZATION TESTS - Quick System Optimization Hub Execution
Simple script to run the System Optimization Hub tests directly

Usage:
    python run_optimization_tests.py                    # Run all tests
    python run_optimization_tests.py system_initialization  # Run specific test
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

def main():
    """Main execution function"""
    print("🧪 SYSTEM OPTIMIZATION HUB - Quick Test Execution")
    print("=" * 60)
    
    # Check if a specific test was requested
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        print(f"🎯 Running specific test: {test_name}")
        
        # Import and run specific test
        from SYSTEM_OPTIMIZATION_HUB import SystemOptimizationHub
        
        async def run_specific_test():
            hub = SystemOptimizationHub()
            result = await hub.run_specific_test(test_name)
            return result
        
        result = asyncio.run(run_specific_test())
        
        if result.status == "PASS":
            print(f"\n✅ TEST PASSED: {test_name}")
        else:
            print(f"\n❌ TEST FAILED: {test_name}")
            if result.error_message:
                print(f"Error: {result.error_message}")
    
    else:
        print("🚀 Running comprehensive test suite...")
        
        # Import and run all tests
        from SYSTEM_OPTIMIZATION_HUB import SystemOptimizationHub
        
        async def run_all_tests():
            hub = SystemOptimizationHub()
            return await hub.run_all_tests()
        
        result = asyncio.run(run_all_tests())
        
        # Display results
        success_rate = result["summary"]["success_rate"]
        total_tests = result["summary"]["total_tests"]
        passed_tests = result["summary"]["passed_tests"]
        
        print(f"\n📊 RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   System Status: {result['system_status']}")
        
        if result["system_status"] == "OPERATIONAL":
            print("\n🎉 SYSTEM IS OPERATIONAL!")
        else:
            print("\n⚠️ SYSTEM NEEDS ATTENTION!")

if __name__ == "__main__":
    main() 