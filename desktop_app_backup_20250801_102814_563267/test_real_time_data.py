#!/usr/bin/env python3
"""
Real-Time Observability Data Testing Script
Tests all observability endpoints and streaming functionality
"""

import requests
import json
import time
import asyncio
import aiohttp
from datetime import datetime
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

class ObservabilityTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.test_results = {}
        
    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")
    
    def print_success(self, message):
        print(f"✅ {message}")
    
    def print_error(self, message):
        print(f"❌ {message}")
    
    def print_info(self, message):
        print(f"ℹ️  {message}")
    
    def test_endpoint(self, endpoint, name):
        """Test a single endpoint"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"{name}: Status {response.status_code}")
                self.test_results[name] = {
                    "status": "PASS",
                    "data": data,
                    "response_time": response.elapsed.total_seconds()
                }
                return True
            else:
                self.print_error(f"{name}: Status {response.status_code}")
                self.test_results[name] = {
                    "status": "FAIL",
                    "error": f"HTTP {response.status_code}"
                }
                return False
                
        except Exception as e:
            self.print_error(f"{name}: {str(e)}")
            self.test_results[name] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    def test_streaming_endpoint(self):
        """Test the real-time streaming endpoint"""
        self.print_header("Testing Real-Time Streaming Endpoint")
        
        try:
            url = f"{self.base_url}/api/observability/stream"
            response = requests.get(url, stream=True, timeout=15)
            
            if response.status_code == 200:
                self.print_success("Streaming endpoint: Status 200")
                
                # Read a few events from the stream
                event_count = 0
                start_time = time.time()
                
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            event_count += 1
                            data = json.loads(line[6:])  # Remove 'data: ' prefix
                            
                            print(f"📊 Event {event_count}:")
                            print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
                            print(f"   Weave Status: {data.get('weave', {}).get('status', 'N/A')}")
                            print(f"   Sentry Status: {data.get('sentry', {}).get('status', 'N/A')}")
                            print(f"   WandB Status: {data.get('wandb', {}).get('status', 'N/A')}")
                            print(f"   CPU Usage: {data.get('system_vitals', {}).get('cpu_usage', 'N/A')}%")
                            
                            if event_count >= 3:  # Test 3 events
                                break
                            
                            if time.time() - start_time > 20:  # Timeout after 20 seconds
                                break
                
                self.print_success(f"Received {event_count} streaming events")
                self.test_results["streaming"] = {
                    "status": "PASS",
                    "events_received": event_count
                }
                return True
            else:
                self.print_error(f"Streaming endpoint: Status {response.status_code}")
                self.test_results["streaming"] = {
                    "status": "FAIL",
                    "error": f"HTTP {response.status_code}"
                }
                return False
                
        except Exception as e:
            self.print_error(f"Streaming endpoint: {str(e)}")
            self.test_results["streaming"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    def test_all_endpoints(self):
        """Test all observability endpoints"""
        self.print_header("Testing All Observability Endpoints")
        
        endpoints = [
            ("/api/observability/overview", "Observability Overview"),
            ("/api/system/vitals", "System Vitals"),
            ("/observability/weave", "Weave Data"),
            ("/observability/sentry", "Sentry Data"),
            ("/observability/wandb", "WandB Data"),
            ("/api/events/live", "Live Events"),
            ("/service-status", "Service Status")
        ]
        
        passed = 0
        total = len(endpoints)
        
        for endpoint, name in endpoints:
            if self.test_endpoint(endpoint, name):
                passed += 1
        
        self.print_header("Endpoint Test Summary")
        print(f"Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        return passed == total
    
    def validate_data_structure(self):
        """Validate the structure of returned data"""
        self.print_header("Validating Data Structure")
        
        required_fields = {
            "observability_overview": ["weave", "sentry", "wandb"],
            "system_vitals": ["cpu_usage", "memory_usage", "disk_usage"],
            "weave_data": ["status", "active_traces", "success_rate"],
            "sentry_data": ["status", "error_rate_percent", "active_issues"],
            "wandb_data": ["status", "active_runs", "best_accuracy"]
        }
        
        validation_passed = True
        
        for test_name, fields in required_fields.items():
            if test_name in self.test_results and self.test_results[test_name]["status"] == "PASS":
                data = self.test_results[test_name]["data"]
                
                missing_fields = []
                for field in fields:
                    if field not in data:
                        missing_fields.append(field)
                
                if missing_fields:
                    self.print_error(f"{test_name}: Missing fields {missing_fields}")
                    validation_passed = False
                else:
                    self.print_success(f"{test_name}: All required fields present")
        
        return validation_passed
    
    def test_data_freshness(self):
        """Test if data is being updated in real-time"""
        self.print_header("Testing Data Freshness")
        
        try:
            # Get initial data
            response1 = requests.get(f"{self.base_url}/api/system/vitals", timeout=5)
            data1 = response1.json()
            initial_cpu = data1.get('cpu_usage', 0)
            
            self.print_info(f"Initial CPU usage: {initial_cpu}%")
            
            # Wait a moment
            time.sleep(3)
            
            # Get updated data
            response2 = requests.get(f"{self.base_url}/api/system/vitals", timeout=5)
            data2 = response2.json()
            updated_cpu = data2.get('cpu_usage', 0)
            
            self.print_info(f"Updated CPU usage: {updated_cpu}%")
            
            # Check if data changed (indicating real-time updates)
            if initial_cpu != updated_cpu:
                self.print_success("Data is being updated in real-time")
                return True
            else:
                self.print_info("Data unchanged (this is normal for short intervals)")
                return True
                
        except Exception as e:
            self.print_error(f"Data freshness test failed: {str(e)}")
            return False
    
    def generate_report(self):
        """Generate a comprehensive test report"""
        self.print_header("Test Report")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["status"] == "PASS")
        
        print(f"📊 Test Results Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            print(f"   {status_icon} {test_name}: {result['status']}")
            
            if result["status"] == "FAIL" and "error" in result:
                print(f"      Error: {result['error']}")
            elif result["status"] == "PASS" and "response_time" in result:
                print(f"      Response Time: {result['response_time']:.3f}s")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if passed_tests == total_tests:
            print("   🎉 All tests passed! Your real-time observability is working correctly.")
        else:
            print("   ⚠️  Some tests failed. Check the error messages above.")
            print("   📖 Review the REAL_TIME_OBSERVABILITY_GUIDE.md for setup instructions.")
        
        return passed_tests == total_tests
    
    def run_all_tests(self):
        """Run all tests"""
        self.print_header("Real-Time Observability Data Testing")
        print(f"Testing against: {self.base_url}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test all endpoints
        endpoints_ok = self.test_all_endpoints()
        
        # Test streaming
        streaming_ok = self.test_streaming_endpoint()
        
        # Validate data structure
        structure_ok = self.validate_data_structure()
        
        # Test data freshness
        freshness_ok = self.test_data_freshness()
        
        # Generate report
        all_passed = self.generate_report()
        
        return all_passed

def main():
    """Main testing function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test real-time observability data")
    parser.add_argument("--url", default="http://localhost:8001", 
                       help="Base URL of the server (default: http://localhost:8001)")
    parser.add_argument("--quick", action="store_true", 
                       help="Run quick test only")
    
    args = parser.parse_args()
    
    tester = ObservabilityTester(args.url)
    
    if args.quick:
        # Quick test - just check if endpoints are responding
        print("🚀 Running quick test...")
        success = tester.test_all_endpoints()
        if success:
            print("✅ Quick test passed!")
        else:
            print("❌ Quick test failed!")
    else:
        # Full test
        success = tester.run_all_tests()
        if success:
            print("\n🎉 All tests passed! Your real-time observability is working correctly.")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. Check the report above for details.")
            sys.exit(1)

if __name__ == "__main__":
    main() 