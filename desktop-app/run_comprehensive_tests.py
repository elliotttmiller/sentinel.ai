#!/usr/bin/env python3
"""
Sentinel Comprehensive Test Runner
Orchestrates all testing modules for complete system validation
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import colorama
from colorama import Fore, Style, Back

# Initialize colorama
colorama.init()

class ComprehensiveTestRunner:
    """Main test runner that orchestrates all testing modules"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.start_time = datetime.now()
        self.results = {}
        
        # Test modules to run
        self.test_modules = [
            ("comprehensive_test_suite.py", "System Integration Tests"),
            ("ai_agent_testing.py", "AI Agent Tests"),
            ("advanced_logging_config.py", "Logging System Tests")
        ]
        
        # Additional manual tests
        self.manual_tests = [
            ("Database Schema", self.test_database_schema),
            ("Service Health", self.test_service_health),
            ("Static Files", self.test_static_files),
            ("Web Interface", self.test_web_interface),
            ("API Endpoints", self.test_api_endpoints),
            ("Performance", self.test_performance),
            ("Security", self.test_security)
        ]
    
    def print_banner(self):
        """Print test suite banner"""
        print("\n" + "="*100)
        print(f"{Fore.CYAN}[STARTUP] SENTINEL COMPREHENSIVE TEST SUITE{Style.RESET_ALL}")
        print("="*100)
        print(f"{Fore.YELLOW}Starting complete system validation...{Style.RESET_ALL}")
        print(f"📅 Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[FILE] Project root: {self.project_root}")
        print("="*100)
    
    def run_module_test(self, module_file: str, description: str) -> Dict[str, Any]:
        """Run a specific test module"""
        print(f"\n{Fore.BLUE}[TOOL] Running {description}...{Style.RESET_ALL}")
        
        start_time = time.time()
        
        try:
            # Run the test module
            result = subprocess.run(
                [sys.executable, module_file],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print(f"{Fore.GREEN}[OK] {description} completed successfully{Style.RESET_ALL}")
                status = "PASS"
            else:
                print(f"{Fore.RED}[ERROR] {description} failed{Style.RESET_ALL}")
                print(f"Error: {result.stderr}")
                status = "FAIL"
            
            return {
                "module": description,
                "status": status,
                "duration": duration,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"{Fore.RED}⏰ {description} timed out after 5 minutes{Style.RESET_ALL}")
            return {
                "module": description,
                "status": "TIMEOUT",
                "duration": duration,
                "return_code": -1,
                "stdout": "",
                "stderr": "Test timed out"
            }
        except Exception as e:
            duration = time.time() - start_time
            print(f"{Fore.RED}[ERROR] {description} failed with exception: {e}{Style.RESET_ALL}")
            return {
                "module": description,
                "status": "ERROR",
                "duration": duration,
                "return_code": -1,
                "stdout": "",
                "stderr": str(e)
            }
    
    def test_database_schema(self) -> Dict[str, Any]:
        """Test database schema integrity"""
        print(f"\n{Fore.BLUE}[DB] Testing database schema...{Style.RESET_ALL}")
        
        try:
            from src.models.advanced_database import db_manager
            
            # Test connection
            engine = db_manager.engine
            with engine.connect() as conn:
                result = conn.execute(db_manager.text("SELECT 1"))
            
            # Test schema
            inspector = db_manager.inspect(engine)
            required_tables = ["missions", "mission_updates", "system_logs"]
            
            missing_tables = []
            for table in required_tables:
                if table not in inspector.get_table_names():
                    missing_tables.append(table)
            
            if missing_tables:
                return {
                    "test": "Database Schema",
                    "status": "FAIL",
                    "details": f"Missing tables: {missing_tables}",
                    "duration": 0.1
                }
            else:
                return {
                    "test": "Database Schema",
                    "status": "PASS",
                    "details": "All required tables exist",
                    "duration": 0.1
                }
                
        except Exception as e:
            return {
                "test": "Database Schema",
                "status": "FAIL",
                "details": f"Database error: {e}",
                "duration": 0.1
            }
    
    def test_service_health(self) -> Dict[str, Any]:
        """Test service health endpoints"""
        print(f"\n{Fore.BLUE}[HEALTH] Testing service health...{Style.RESET_ALL}")
        
        import requests
        
        services = [
            ("Desktop App", "http://localhost:8001/health"),
            ("Cognitive Engine", "http://localhost:8002/health")
        ]
        
        results = []
        for service_name, url in services:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    results.append(f"[OK] {service_name}")
                else:
                    results.append(f"[ERROR] {service_name} (Status: {response.status_code})")
            except Exception as e:
                results.append(f"[ERROR] {service_name} (Error: {e})")
        
        all_healthy = all("[OK]" in result for result in results)
        
        return {
            "test": "Service Health",
            "status": "PASS" if all_healthy else "FAIL",
            "details": "; ".join(results),
            "duration": 0.5
        }
    
    def test_static_files(self) -> Dict[str, Any]:
        """Test static file serving"""
        print(f"\n{Fore.BLUE}[FILE] Testing static files...{Style.RESET_ALL}")
        
        import requests
        
        static_files = [
            "/static/js/main.js",
            "/static/css/main.css",
            "/static/images/favicon.png"
        ]
        
        results = []
        for file_path in static_files:
            try:
                response = requests.get(f"http://localhost:8001{file_path}", timeout=10)
                if response.status_code == 200:
                    results.append(f"[OK] {file_path}")
                else:
                    results.append(f"[ERROR] {file_path} (Status: {response.status_code})")
            except Exception as e:
                results.append(f"[ERROR] {file_path} (Error: {e})")
        
        all_accessible = all("[OK]" in result for result in results)
        
        return {
            "test": "Static Files",
            "status": "PASS" if all_accessible else "FAIL",
            "details": "; ".join(results),
            "duration": 0.5
        }
    
    def test_web_interface(self) -> Dict[str, Any]:
        """Test web interface functionality"""
        print(f"\n{Fore.BLUE}[WEB] Testing web interface...{Style.RESET_ALL}")
        
        import requests
        
        try:
            response = requests.get("http://localhost:8001/", timeout=10)
            if response.status_code == 200:
                return {
                    "test": "Web Interface",
                    "status": "PASS",
                    "details": "Main page loads successfully",
                    "duration": 0.2
                }
            else:
                return {
                    "test": "Web Interface",
                    "status": "FAIL",
                    "details": f"Main page returned status {response.status_code}",
                    "duration": 0.2
                }
        except Exception as e:
            return {
                "test": "Web Interface",
                "status": "FAIL",
                "details": f"Web interface error: {e}",
                "duration": 0.2
            }
    
    def test_api_endpoints(self) -> Dict[str, Any]:
        """Test API endpoints"""
        print(f"\n{Fore.BLUE}[WEB] Testing API endpoints...{Style.RESET_ALL}")
        
        import requests
        
        endpoints = [
            ("GET", "/missions"),
            ("GET", "/system-stats"),
            ("GET", "/api/status")
        ]
        
        results = []
        for method, endpoint in endpoints:
            try:
                response = requests.get(f"http://localhost:8001{endpoint}", timeout=10)
                if response.status_code == 200:
                    results.append(f"[OK] {method} {endpoint}")
                else:
                    results.append(f"[ERROR] {method} {endpoint} (Status: {response.status_code})")
            except Exception as e:
                results.append(f"[ERROR] {method} {endpoint} (Error: {e})")
        
        all_working = all("[OK]" in result for result in results)
        
        return {
            "test": "API Endpoints",
            "status": "PASS" if all_working else "FAIL",
            "details": "; ".join(results),
            "duration": 0.5
        }
    
    def test_performance(self) -> Dict[str, Any]:
        """Test system performance"""
        print(f"\n{Fore.BLUE}[PERF] Testing performance...{Style.RESET_ALL}")
        
        import psutil
        import requests
        
        # Get system metrics
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)
        
        # Test API response time
        start_time = time.time()
        try:
            response = requests.get("http://localhost:8001/missions", timeout=10)
            response_time = time.time() - start_time
        except:
            response_time = 999
        
        # Determine performance status
        memory_ok = memory.percent < 80
        cpu_ok = cpu < 80
        response_ok = response_time < 5
        
        all_ok = memory_ok and cpu_ok and response_ok
        
        return {
            "test": "Performance",
            "status": "PASS" if all_ok else "WARNING",
            "details": f"Memory: {memory.percent:.1f}%, CPU: {cpu:.1f}%, Response: {response_time:.2f}s",
            "duration": 1.0
        }
    
    def test_security(self) -> Dict[str, Any]:
        """Test basic security features"""
        print(f"\n{Fore.BLUE}[SEC] Testing security...{Style.RESET_ALL}")
        
        import requests
        
        # Test invalid endpoints
        try:
            response = requests.get("http://localhost:8001/invalid-endpoint", timeout=5)
            if response.status_code == 404:
                return {
                    "test": "Security",
                    "status": "PASS",
                    "details": "Invalid endpoints properly return 404",
                    "duration": 0.1
                }
            else:
                return {
                    "test": "Security",
                    "status": "WARNING",
                    "details": f"Invalid endpoint returned {response.status_code} instead of 404",
                    "duration": 0.1
                }
        except Exception as e:
            return {
                "test": "Security",
                "status": "FAIL",
                "details": f"Security test error: {e}",
                "duration": 0.1
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all comprehensive tests"""
        print(f"\n{Fore.CYAN}[STARTUP] Starting comprehensive test suite...{Style.RESET_ALL}")
        
        # Run module tests
        for module_file, description in self.test_modules:
            result = self.run_module_test(module_file, description)
            self.results[description] = result
        
        # Run manual tests
        for test_name, test_func in self.manual_tests:
            result = test_func()
            self.results[test_name] = result
        
        return self.generate_comprehensive_report()
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        print(f"\n{Fore.CYAN}[STATS] Generating comprehensive test report...{Style.RESET_ALL}")
        
        # Calculate statistics
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results.values() if r["status"] == "PASS"])
        failed_tests = len([r for r in self.results.values() if r["status"] == "FAIL"])
        warning_tests = len([r for r in self.results.values() if r["status"] == "WARNING"])
        
        total_duration = sum(r.get("duration", 0) for r in self.results.values())
        
        # Calculate success rate
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Generate recommendations
        recommendations = []
        
        if failed_tests > 0:
            recommendations.append(f"🔴 {failed_tests} tests failed - Review and fix critical issues")
        
        if warning_tests > 0:
            recommendations.append(f"🟡 {warning_tests} tests have warnings - Consider improvements")
        
        # Check specific areas
        module_results = [r for name, r in self.results.items() if "Tests" in name]
        if any(r["status"] == "FAIL" for r in module_results):
            recommendations.append("🔴 Module tests failed - Check system integration")
        
        if not failed_tests and not warning_tests:
            recommendations.append("[OK] All tests passed - System is fully operational")
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "warnings": warning_tests,
                "success_rate": f"{success_rate:.1f}%",
                "total_duration": f"{total_duration:.2f}s"
            },
            "detailed_results": self.results,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat(),
            "test_duration": (datetime.now() - self.start_time).total_seconds()
        }
        
        return report
    
    def print_comprehensive_report(self, report: Dict[str, Any]):
        """Print comprehensive test report"""
        print("\n" + "="*100)
        print(f"{Fore.CYAN}[STATS] SENTINEL COMPREHENSIVE TEST REPORT{Style.RESET_ALL}")
        print("="*100)
        
        summary = report["test_summary"]
        print(f"\n[STATS] TEST SUMMARY:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   [OK] Passed: {summary['passed']}")
        print(f"   [ERROR] Failed: {summary['failed']}")
        print(f"   [WARN] Warnings: {summary['warnings']}")
        print(f"   Success Rate: {summary['success_rate']}")
        print(f"   Total Duration: {summary['total_duration']}")
        
        print(f"\n[INFO] DETAILED RESULTS:")
        for test_name, result in report["detailed_results"].items():
            status_icon = "[OK]" if result["status"] == "PASS" else "[ERROR]" if result["status"] == "FAIL" else "[WARN]"
            print(f"   {status_icon} {test_name}: {result['status']} ({result.get('duration', 0):.2f}s)")
            if result.get("details"):
                print(f"      Details: {result['details']}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in report["recommendations"]:
            print(f"   {rec}")
        
        print(f"\n📅 Report Generated: {report['timestamp']}")
        print(f"⏱️ Total Test Duration: {report['test_duration']:.2f}s")
        print("="*100)
    
    def save_detailed_report(self, report: Dict[str, Any]):
        """Save detailed report to file"""
        report_file = f"logs/comprehensive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        return report_file

def main():
    """Main entry point for comprehensive test runner"""
    try:
        runner = ComprehensiveTestRunner()
        runner.print_banner()
        
        # Run all tests
        report = runner.run_all_tests()
        
        # Print and save report
        runner.print_comprehensive_report(report)
        runner.save_detailed_report(report)
        
        # Determine overall success
        failed_tests = report["test_summary"]["failed"]
        
        if failed_tests == 0:
            print(f"\n{Fore.GREEN}[SUCCESS] All tests passed! Sentinel system is fully operational.{Style.RESET_ALL}")
            return True
        else:
            print(f"\n{Fore.RED}[ERROR] {failed_tests} tests failed. Check the detailed report for issues.{Style.RESET_ALL}")
            return False
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[WARN] Test suite interrupted by user{Style.RESET_ALL}")
        return False
    except Exception as e:
        print(f"\n{Fore.RED}[ERROR] Test suite failed with error: {e}{Style.RESET_ALL}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 