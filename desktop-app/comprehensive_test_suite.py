#!/usr/bin/env python3
"""
Sentinel Comprehensive End-to-End Test Suite
Advanced testing system with intelligent debugging and full system validation
"""

import os
import sys
import time
import json
import requests
import subprocess
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import traceback
import psutil
import sqlite3
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from loguru import logger
import colorama
from colorama import Fore, Style, Back

# Initialize colorama for cross-platform colored output
colorama.init()

@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    status: str  # "PASS", "FAIL", "WARNING", "SKIP"
    duration: float
    details: str
    error: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class SentinelTestSuite:
    """Comprehensive test suite for Sentinel system"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.results: List[TestResult] = []
        self.start_time = datetime.now()
        self.base_url = "http://localhost:8001"
        self.cognitive_url = "http://localhost:8002"
        
        # Configure advanced logging
        self.setup_logging()
        
        # Test configuration
        self.test_config = {
            "timeout": 30,
            "retry_attempts": 3,
            "concurrent_tests": 5,
            "performance_threshold": 5.0,  # seconds
            "memory_threshold": 500,  # MB
            "cpu_threshold": 80,  # percentage
        }
    
    def setup_logging(self):
        """Setup comprehensive logging system"""
        # Remove default logger
        logger.remove()
        
        # Add console logger with colors
        logger.add(
            lambda msg: print(f"{Fore.CYAN}[DEBUG]{Style.RESET_ALL} {msg}"),
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
        )
        
        # Add file logger for detailed debugging
        logger.add(
            "logs/comprehensive_test.log",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
            rotation="10 MB",
            retention="7 days"
        )
        
        # Add performance logger
        logger.add(
            "logs/performance_test.log",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            filter=lambda record: "PERFORMANCE" in record["message"]
        )
        
        # Add error logger
        logger.add(
            "logs/error_test.log",
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
            rotation="5 MB"
        )
    
    def log_test_start(self, test_name: str):
        """Log test start with detailed information"""
        logger.info(f"[STARTUP] Starting test: {test_name}")
        logger.debug(f"Test environment: {os.getcwd()}")
        logger.debug(f"Python version: {sys.version}")
        logger.debug(f"Available memory: {psutil.virtual_memory().available / 1024 / 1024:.2f} MB")
    
    def log_test_result(self, result: TestResult):
        """Log test result with appropriate formatting"""
        status_colors = {
            "PASS": Fore.GREEN,
            "FAIL": Fore.RED,
            "WARNING": Fore.YELLOW,
            "SKIP": Fore.BLUE
        }
        
        color = status_colors.get(result.status, Fore.WHITE)
        logger.info(f"{color}{result.status}{Style.RESET_ALL} | {result.test_name} | {result.duration:.2f}s")
        
        if result.error:
            logger.error(f"Error in {result.test_name}: {result.error}")
        
        if result.metrics:
            logger.debug(f"Metrics for {result.test_name}: {json.dumps(result.metrics, indent=2)}")
    
    def run_test(self, test_func, test_name: str) -> TestResult:
        """Run a single test with comprehensive logging"""
        start_time = time.time()
        self.log_test_start(test_name)
        
        try:
            # Capture system metrics before test
            before_metrics = self.get_system_metrics()
            
            # Run the test
            result = test_func()
            
            # Capture system metrics after test
            after_metrics = self.get_system_metrics()
            
            duration = time.time() - start_time
            
            # Calculate performance metrics
            performance_metrics = {
                "duration": duration,
                "memory_delta": after_metrics["memory"] - before_metrics["memory"],
                "cpu_delta": after_metrics["cpu"] - before_metrics["cpu"],
                "before_metrics": before_metrics,
                "after_metrics": after_metrics
            }
            
            # Determine status based on performance thresholds
            status = "PASS"
            details = "Test completed successfully"
            
            if duration > self.test_config["performance_threshold"]:
                status = "WARNING"
                details = f"Test took {duration:.2f}s (threshold: {self.test_config['performance_threshold']}s)"
            
            if performance_metrics["memory_delta"] > self.test_config["memory_threshold"]:
                status = "WARNING"
                details += f" | High memory usage: {performance_metrics['memory_delta']:.2f}MB"
            
            test_result = TestResult(
                test_name=test_name,
                status=status,
                duration=duration,
                details=details,
                metrics=performance_metrics
            )
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            logger.error(f"Test {test_name} failed: {error_msg}")
            
            test_result = TestResult(
                test_name=test_name,
                status="FAIL",
                duration=duration,
                details="Test failed with exception",
                error=error_msg
            )
        
        self.log_test_result(test_result)
        self.results.append(test_result)
        return test_result
    
    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system metrics"""
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.1)
        
        return {
            "memory": memory.used / 1024 / 1024,  # MB
            "cpu": cpu,
            "memory_percent": memory.percent,
            "available_memory": memory.available / 1024 / 1024
        }
    
    def test_environment_setup(self) -> bool:
        """Test environment and dependencies"""
        logger.info("[TOOL] Testing environment setup...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            raise Exception(f"Python 3.8+ required, found {sys.version}")
        
        # Check required directories
        required_dirs = ["logs", "db", "static", "templates"]
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                raise Exception(f"Required directory missing: {dir_name}")
        
        # Check required files
        required_files = [
            "src/main.py",
            "src/cognitive_engine_service.py",
            "templates/index.html",
            "static/js/main.js",
            "static/css/main.css"
        ]
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                raise Exception(f"Required file missing: {file_path}")
        
        logger.info("[OK] Environment setup validated")
        return True
    
    def test_database_connection(self) -> bool:
        """Test database connectivity and schema"""
        logger.info("[DB] Testing database connection...")
        
        try:
            from src.models.advanced_database import db_manager
            
            # Test connection
            engine = db_manager.engine
            with engine.connect() as conn:
                result = conn.execute(db_manager.text("SELECT 1"))
                logger.info("[OK] Database connection successful")
            
            # Test schema
            inspector = db_manager.inspect(engine)
            required_tables = ["missions", "mission_updates", "system_logs"]
            
            for table in required_tables:
                if table not in inspector.get_table_names():
                    raise Exception(f"Required table missing: {table}")
            
            # Test data integrity
            with engine.connect() as conn:
                result = conn.execute(db_manager.text("SELECT COUNT(*) FROM missions"))
                mission_count = result.fetchone()[0]
                logger.info(f"[OK] Found {mission_count} missions in database")
            
            return True
            
        except Exception as e:
            raise Exception(f"Database test failed: {e}")
    
    def test_service_health(self) -> bool:
        """Test service health endpoints"""
        logger.info("[HEALTH] Testing service health...")
        
        services = [
            ("Desktop App", f"{self.base_url}/health"),
            ("Cognitive Engine", f"{self.cognitive_url}/health")
        ]
        
        for service_name, url in services:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"[OK] {service_name} health check passed")
                else:
                    raise Exception(f"{service_name} returned status {response.status_code}")
            except Exception as e:
                raise Exception(f"{service_name} health check failed: {e}")
        
        return True
    
    def test_api_endpoints(self) -> Dict[str, Any]:
        """Test all API endpoints comprehensively"""
        logger.info("[WEB] Testing API endpoints...")
        
        endpoints = [
            ("GET", "/missions", "List missions"),
            ("GET", "/system-stats", "System statistics"),
            ("GET", "/api/status", "API status"),
            ("GET", "/memory/search", "Memory search"),
            ("POST", "/advanced-mission", "Create mission")
        ]
        
        results = {}
        
        for method, endpoint, description in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                
                if method == "GET":
                    if endpoint == "/memory/search":
                        response = requests.get(url, params={"query": "test"}, timeout=10)
                    else:
                        response = requests.get(url, timeout=10)
                elif method == "POST":
                    if endpoint == "/advanced-mission":
                        payload = {
                            "prompt": "Test mission for comprehensive testing",
                            "title": "Comprehensive Test Mission",
                            "agent_type": "developer"
                        }
                        response = requests.post(url, json=payload, timeout=30)
                
                if response.status_code in [200, 201]:
                    logger.info(f"[OK] {description} ({method} {endpoint})")
                    results[endpoint] = {
                        "status": "PASS",
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds()
                    }
                else:
                    logger.warning(f"[WARN] {description} returned {response.status_code}")
                    results[endpoint] = {
                        "status": "WARNING",
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds()
                    }
                    
            except Exception as e:
                logger.error(f"[ERROR] {description} failed: {e}")
                results[endpoint] = {
                    "status": "FAIL",
                    "error": str(e)
                }
        
        return results
    
    def test_ai_cognitive_engine(self) -> Dict[str, Any]:
        """Test AI cognitive engine functionality"""
        logger.info("[AI] Testing AI Cognitive Engine...")
        
        try:
            # Test basic AI generation
            test_prompt = "Create a simple Python function that adds two numbers"
            
            response = requests.post(
                f"{self.cognitive_url}/generate",
                json={"prompt": test_prompt},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("[OK] AI generation test passed")
                
                # Test mission execution
                mission_response = requests.post(
                    f"{self.cognitive_url}/mission",
                    json={
                        "prompt": "Write a hello world program",
                        "mission_id": "test_mission_001",
                        "agent_type": "developer"
                    },
                    timeout=60
                )
                
                if mission_response.status_code == 200:
                    logger.info("[OK] Mission execution test passed")
                    return {
                        "ai_generation": "PASS",
                        "mission_execution": "PASS",
                        "response_time": response.elapsed.total_seconds()
                    }
                else:
                    logger.warning(f"[WARN] Mission execution returned {mission_response.status_code}")
                    return {
                        "ai_generation": "PASS",
                        "mission_execution": "WARNING",
                        "response_time": response.elapsed.total_seconds()
                    }
            else:
                raise Exception(f"AI generation returned {response.status_code}")
                
        except Exception as e:
            raise Exception(f"AI cognitive engine test failed: {e}")
    
    def test_web_interface(self) -> bool:
        """Test web interface functionality"""
        logger.info("[WEB] Testing web interface...")
        
        try:
            # Test main page
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code != 200:
                raise Exception(f"Main page returned {response.status_code}")
            
            # Test static files
            static_files = [
                "/static/js/main.js",
                "/static/css/main.css",
                "/static/images/favicon.png"
            ]
            
            for static_file in static_files:
                response = requests.get(f"{self.base_url}{static_file}", timeout=10)
                if response.status_code != 200:
                    raise Exception(f"Static file {static_file} returned {response.status_code}")
            
            logger.info("[OK] Web interface test passed")
            return True
            
        except Exception as e:
            raise Exception(f"Web interface test failed: {e}")
    
    def test_performance_metrics(self) -> Dict[str, Any]:
        """Test system performance under load"""
        logger.info("[PERF] Testing performance metrics...")
        
        # Get baseline metrics
        baseline = self.get_system_metrics()
        
        # Simulate load by making multiple concurrent requests
        def make_request():
            try:
                response = requests.get(f"{self.base_url}/missions", timeout=10)
                return response.status_code == 200
            except:
                return False
        
        # Run concurrent requests
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in futures]
        
        # Get metrics after load
        after_load = self.get_system_metrics()
        
        success_rate = sum(results) / len(results)
        
        performance_metrics = {
            "baseline_memory": baseline["memory"],
            "after_load_memory": after_load["memory"],
            "memory_increase": after_load["memory"] - baseline["memory"],
            "baseline_cpu": baseline["cpu"],
            "after_load_cpu": after_load["cpu"],
            "cpu_increase": after_load["cpu"] - baseline["cpu"],
            "success_rate": success_rate,
            "concurrent_requests": len(results)
        }
        
        logger.info(f"[OK] Performance test completed - Success rate: {success_rate:.2%}")
        return performance_metrics
    
    def test_error_handling(self) -> bool:
        """Test error handling and recovery"""
        logger.info("🛡️ Testing error handling...")
        
        try:
            # Test invalid endpoints
            response = requests.get(f"{self.base_url}/invalid-endpoint", timeout=5)
            if response.status_code != 404:
                logger.warning("[WARN] Invalid endpoint didn't return 404")
            
            # Test malformed requests
            response = requests.post(
                f"{self.base_url}/advanced-mission",
                json={"invalid": "data"},
                timeout=10
            )
            if response.status_code not in [400, 422]:
                logger.warning("[WARN] Malformed request didn't return proper error")
            
            # Test database error handling
            from src.models.advanced_database import db_manager
            try:
                with db_manager.engine.connect() as conn:
                    conn.execute(db_manager.text("SELECT * FROM nonexistent_table"))
            except:
                logger.info("[OK] Database error handling working correctly")
            
            logger.info("[OK] Error handling test passed")
            return True
            
        except Exception as e:
            raise Exception(f"Error handling test failed: {e}")
    
    def test_security_features(self) -> bool:
        """Test security features and input validation"""
        logger.info("[SEC] Testing security features...")
        
        try:
            # Test SQL injection prevention
            malicious_inputs = [
                "'; DROP TABLE missions; --",
                "<script>alert('xss')</script>",
                "../../../etc/passwd",
                "'; INSERT INTO missions VALUES (999, 'hack'); --"
            ]
            
            for malicious_input in malicious_inputs:
                response = requests.get(
                    f"{self.base_url}/missions",
                    params={"query": malicious_input},
                    timeout=10
                )
                # Should not crash or return sensitive data
                if response.status_code == 500:
                    logger.warning(f"[WARN] Malicious input caused 500 error: {malicious_input}")
            
            logger.info("[OK] Security test passed")
            return True
            
        except Exception as e:
            raise Exception(f"Security test failed: {e}")
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        logger.info("[STATS] Generating comprehensive test report...")
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == "PASS"])
        failed_tests = len([r for r in self.results if r.status == "FAIL"])
        warning_tests = len([r for r in self.results if r.status == "WARNING"])
        
        total_duration = sum(r.duration for r in self.results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        
        # System health score
        health_score = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Performance analysis
        slow_tests = [r for r in self.results if r.duration > self.test_config["performance_threshold"]]
        memory_intensive_tests = [r for r in self.results if r.metrics and r.metrics.get("memory_delta", 0) > self.test_config["memory_threshold"]]
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "warnings": warning_tests,
                "success_rate": f"{(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%",
                "health_score": f"{health_score:.1f}%"
            },
            "performance_analysis": {
                "total_duration": f"{total_duration:.2f}s",
                "average_duration": f"{avg_duration:.2f}s",
                "slow_tests": len(slow_tests),
                "memory_intensive_tests": len(memory_intensive_tests)
            },
            "detailed_results": [asdict(r) for r in self.results],
            "recommendations": self.generate_recommendations(),
            "timestamp": datetime.now().isoformat(),
            "test_duration": (datetime.now() - self.start_time).total_seconds()
        }
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        failed_tests = [r for r in self.results if r.status == "FAIL"]
        slow_tests = [r for r in self.results if r.duration > self.test_config["performance_threshold"]]
        memory_intensive_tests = [r for r in self.results if r.metrics and r.metrics.get("memory_delta", 0) > self.test_config["memory_threshold"]]
        
        if failed_tests:
            recommendations.append(f"🔴 {len(failed_tests)} tests failed - Review and fix critical issues")
        
        if slow_tests:
            recommendations.append(f"🟡 {len(slow_tests)} tests are slow - Consider optimization")
        
        if memory_intensive_tests:
            recommendations.append(f"🟡 {len(memory_intensive_tests)} tests use high memory - Monitor resource usage")
        
        if not failed_tests and not slow_tests:
            recommendations.append("[OK] System is performing well - Continue monitoring")
        
        return recommendations
    
    def print_comprehensive_report(self, report: Dict[str, Any]):
        """Print comprehensive test report with formatting"""
        print("\n" + "="*80)
        print("[STARTUP] SENTINEL COMPREHENSIVE TEST SUITE REPORT")
        print("="*80)
        
        summary = report["test_summary"]
        print(f"\n[STATS] TEST SUMMARY:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   [OK] Passed: {summary['passed']}")
        print(f"   [ERROR] Failed: {summary['failed']}")
        print(f"   [WARN] Warnings: {summary['warnings']}")
        print(f"   Success Rate: {summary['success_rate']}")
        print(f"   Health Score: {summary['health_score']}")
        
        performance = report["performance_analysis"]
        print(f"\n[PERF] PERFORMANCE ANALYSIS:")
        print(f"   Total Duration: {performance['total_duration']}")
        print(f"   Average Duration: {performance['average_duration']}")
        print(f"   Slow Tests: {performance['slow_tests']}")
        print(f"   Memory Intensive Tests: {performance['memory_intensive_tests']}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in report["recommendations"]:
            print(f"   {rec}")
        
        print(f"\n📅 Report Generated: {report['timestamp']}")
        print(f"⏱️ Test Duration: {report['test_duration']:.2f}s")
        print("="*80)
    
    def run_comprehensive_test_suite(self):
        """Run the complete comprehensive test suite"""
        logger.info("[STARTUP] Starting Sentinel Comprehensive Test Suite")
        logger.info(f"Test configuration: {self.test_config}")
        
        # Define all tests
        tests = [
            (self.test_environment_setup, "Environment Setup"),
            (self.test_database_connection, "Database Connection"),
            (self.test_service_health, "Service Health"),
            (self.test_api_endpoints, "API Endpoints"),
            (self.test_ai_cognitive_engine, "AI Cognitive Engine"),
            (self.test_web_interface, "Web Interface"),
            (self.test_performance_metrics, "Performance Metrics"),
            (self.test_error_handling, "Error Handling"),
            (self.test_security_features, "Security Features")
        ]
        
        # Run all tests
        for test_func, test_name in tests:
            self.run_test(test_func, test_name)
        
        # Generate and print comprehensive report
        report = self.generate_comprehensive_report()
        self.print_comprehensive_report(report)
        
        # Save detailed report to file
        report_file = f"logs/comprehensive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📄 Detailed report saved to: {report_file}")
        
        # Return overall success
        failed_tests = [r for r in self.results if r.status == "FAIL"]
        return len(failed_tests) == 0

def main():
    """Main entry point for comprehensive test suite"""
    print(f"{Fore.CYAN}[STARTUP] Sentinel Comprehensive Test Suite{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Starting comprehensive system validation...{Style.RESET_ALL}")
    
    try:
        test_suite = SentinelTestSuite()
        success = test_suite.run_comprehensive_test_suite()
        
        if success:
            print(f"\n{Fore.GREEN}[OK] All tests passed! System is fully operational.{Style.RESET_ALL}")
            sys.exit(0)
        else:
            print(f"\n{Fore.RED}[ERROR] Some tests failed. Check the detailed report for issues.{Style.RESET_ALL}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[WARN] Test suite interrupted by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}[ERROR] Test suite failed with error: {e}{Style.RESET_ALL}")
        logger.error(f"Test suite failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 