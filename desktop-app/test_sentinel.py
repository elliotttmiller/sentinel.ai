#!/usr/bin/env python3
"""
Sentinel Test Runner - Easy access to all testing capabilities
"""

import sys
import os
from pathlib import Path

def main():
    """Main test runner with menu options"""
    print("🚀 Sentinel Test Runner")
    print("=" * 50)
    print("Choose a test option:")
    print("1. Run Comprehensive Test Suite (Full System)")
    print("2. Run AI Agent Tests Only")
    print("3. Run System Integration Tests Only")
    print("4. Run Performance Tests Only")
    print("5. Run Quick Health Check")
    print("6. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                print("\n🔧 Running Comprehensive Test Suite...")
                os.system("python run_comprehensive_tests.py")
                break
                
            elif choice == "2":
                print("\n🧠 Running AI Agent Tests...")
                os.system("python ai_agent_testing.py")
                break
                
            elif choice == "3":
                print("\n🔧 Running System Integration Tests...")
                os.system("python comprehensive_test_suite.py")
                break
                
            elif choice == "4":
                print("\n⚡ Running Performance Tests...")
                # Import and run performance tests
                from comprehensive_test_suite import SentinelTestSuite
                test_suite = SentinelTestSuite()
                test_suite.run_test(test_suite.test_performance_metrics, "Performance Tests")
                break
                
            elif choice == "5":
                print("\n🏥 Running Quick Health Check...")
                import requests
                
                try:
                    # Test basic endpoints
                    response = requests.get("http://localhost:8001/health", timeout=5)
                    if response.status_code == 200:
                        print("✅ Desktop App: HEALTHY")
                    else:
                        print("❌ Desktop App: UNHEALTHY")
                        
                    response = requests.get("http://localhost:8002/health", timeout=5)
                    if response.status_code == 200:
                        print("✅ Cognitive Engine: HEALTHY")
                    else:
                        print("❌ Cognitive Engine: UNHEALTHY")
                        
                    response = requests.get("http://localhost:8001/missions", timeout=5)
                    if response.status_code == 200:
                        print("✅ API Endpoints: WORKING")
                    else:
                        print("❌ API Endpoints: FAILED")
                        
                    print("\n✅ Quick health check completed!")
                    
                except Exception as e:
                    print(f"❌ Health check failed: {e}")
                break
                
            elif choice == "6":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-6.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 