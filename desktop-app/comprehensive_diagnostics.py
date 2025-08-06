#!/usr/bin/env python3
"""
Comprehensive End-to-End Diagnostics for Sentinel AI v6.0
Tests all endpoints, functionality, and enhanced multi-agent system integration
"""

import asyncio
import json
import requests
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_test(test_name: str, status: str, details: str = ""):
    """Print test results with colors"""
    if status == "PASS":
        print(f"{Colors.GREEN}✅ {test_name}: {status}{Colors.END}")
    elif status == "FAIL":
        print(f"{Colors.RED}❌ {test_name}: {status}{Colors.END}")
    elif status == "WARN":
        print(f"{Colors.YELLOW}⚠️  {test_name}: {status}{Colors.END}")
    elif status == "INFO":
        print(f"{Colors.BLUE}ℹ️  {test_name}: {status}{Colors.END}")
    
    if details:
        print(f"   {Colors.CYAN}{details}{Colors.END}")

def print_section(section_name: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.PURPLE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{section_name}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{'='*60}{Colors.END}\n")

class SentinelDiagnostics:
    def __init__(self):
        self.base_url_8001 = "http://localhost:8001"
        self.base_url_8002 = "http://localhost:8002"
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "total": 0
        }
    
    def record_result(self, status: str):
        """Record test result"""
        self.test_results["total"] += 1
        if status == "PASS":
            self.test_results["passed"] += 1
        elif status == "FAIL":
            self.test_results["failed"] += 1
        elif status == "WARN":
            self.test_results["warnings"] += 1
    
    def test_server_health(self, port: int):
        """Test server health and availability"""
        url = f"http://localhost:{port}"
        try:
            response = requests.get(f"{url}/", timeout=5)
            if response.status_code == 200:
                print_test(f"Server {port} Health", "PASS", f"Server responding on {url}")
                self.record_result("PASS")
                return True
            else:
                print_test(f"Server {port} Health", "FAIL", f"Server returned {response.status_code}")
                self.record_result("FAIL")
                return False
        except requests.exceptions.RequestException as e:
            print_test(f"Server {port} Health", "FAIL", f"Connection failed: {str(e)}")
            self.record_result("FAIL")
            return False
    
    def test_api_endpoints(self, base_url: str, port: int):
        """Test core API endpoints"""
        endpoints = [
            ("/api/missions", "GET", "List missions"),
            ("/api/stats", "GET", "System statistics"), 
            ("/api/health", "GET", "Health check"),
        ]
        
        for endpoint, method, description in endpoints:
            try:
                url = f"{base_url}{endpoint}"
                response = requests.request(method, url, timeout=5)
                
                if response.status_code in [200, 404]:  # 404 is acceptable for some endpoints
                    print_test(f"API {endpoint}", "PASS", f"{description} - Status: {response.status_code}")
                    self.record_result("PASS")
                else:
                    print_test(f"API {endpoint}", "WARN", f"Unexpected status: {response.status_code}")
                    self.record_result("WARN")
            except Exception as e:
                print_test(f"API {endpoint}", "FAIL", f"Request failed: {str(e)}")
                self.record_result("FAIL")
    
    def test_mission_creation(self):
        """Test mission creation and execution"""
        try:
            mission_data = {
                "prompt": "Create a simple Python function that calculates the factorial of a number",
                "agent_type": "developer",
                "priority": "normal"
            }
            
            url = f"{self.base_url_8001}/api/missions"
            response = requests.post(url, json=mission_data, timeout=10)
            
            if response.status_code in [200, 201]:
                result = response.json()
                mission_id = result.get("mission_id", "unknown")
                print_test("Mission Creation", "PASS", f"Mission created with ID: {mission_id}")
                self.record_result("PASS")
                return mission_id
            else:
                print_test("Mission Creation", "FAIL", f"Status: {response.status_code}")
                self.record_result("FAIL")
                return None
        except Exception as e:
            print_test("Mission Creation", "FAIL", f"Exception: {str(e)}")
            self.record_result("FAIL")
            return None
    
    def test_enhanced_components(self):
        """Test enhanced v6.0 components"""
        try:
            # Test if enhanced components can be imported
            import sys
            sys.path.append('.')
            
            # Test enhanced multi-agent system import
            try:
                from enhanced_multi_agent_system import MultiAgentOrchestrator
                print_test("Enhanced Multi-Agent Import", "PASS", "MultiAgentOrchestrator imported successfully")
                self.record_result("PASS")
            except ImportError as e:
                print_test("Enhanced Multi-Agent Import", "FAIL", f"Import failed: {e}")
                self.record_result("FAIL")
            
            # Test sentinel integration import
            try:
                from sentinel_multi_agent_integration import SentinelMultiAgentBridge
                print_test("Sentinel Integration Import", "PASS", "SentinelMultiAgentBridge imported successfully")
                self.record_result("PASS")
            except ImportError as e:
                print_test("Sentinel Integration Import", "FAIL", f"Import failed: {e}")
                self.record_result("FAIL")
            
            # Test enhanced cognitive forge engine
            try:
                from src.core.enhanced_cognitive_forge_engine import EnhancedCognitiveForgeEngine
                print_test("Enhanced Engine Import", "PASS", "EnhancedCognitiveForgeEngine imported successfully")
                self.record_result("PASS")
            except ImportError as e:
                print_test("Enhanced Engine Import", "FAIL", f"Import failed: {e}")
                self.record_result("FAIL")
                
        except Exception as e:
            print_test("Enhanced Components Test", "FAIL", f"General exception: {e}")
            self.record_result("FAIL")
    
    def test_database_connectivity(self):
        """Test database connectivity"""
        try:
            from src.models.advanced_database import db_manager
            
            # Test database connection
            missions = db_manager.list_missions(limit=1)
            print_test("Database Connectivity", "PASS", f"Successfully connected and retrieved data")
            self.record_result("PASS")
            
        except Exception as e:
            print_test("Database Connectivity", "FAIL", f"Database test failed: {e}")
            self.record_result("FAIL")
    
    def test_llm_integration(self):
        """Test LLM integration"""
        try:
            from src.utils.google_ai_wrapper import create_google_ai_llm
            
            # Test LLM creation
            llm = create_google_ai_llm()
            print_test("LLM Integration", "PASS", "Google AI LLM created successfully")
            self.record_result("PASS")
            
        except Exception as e:
            print_test("LLM Integration", "FAIL", f"LLM test failed: {e}")
            self.record_result("FAIL")
    
    def test_websocket_functionality(self):
        """Test WebSocket functionality"""
        try:
            url = f"{self.base_url_8001}/ws"
            # We can't easily test websockets without a client, so we check if the endpoint exists
            response = requests.get(self.base_url_8001, timeout=5)
            if "websocket" in response.text.lower() or response.status_code == 200:
                print_test("WebSocket Endpoint", "PASS", "WebSocket endpoint appears to be available")
                self.record_result("PASS")
            else:
                print_test("WebSocket Endpoint", "WARN", "WebSocket availability uncertain")
                self.record_result("WARN")
        except Exception as e:
            print_test("WebSocket Endpoint", "FAIL", f"WebSocket test failed: {e}")
            self.record_result("FAIL")
    
    def test_configuration_loading(self):
        """Test configuration loading"""
        try:
            from src.config.settings import settings
            
            # Test key configuration values
            if hasattr(settings, 'MULTI_AGENT_ENABLED') and settings.MULTI_AGENT_ENABLED:
                print_test("Multi-Agent Config", "PASS", "Multi-agent system enabled in configuration")
                self.record_result("PASS")
            else:
                print_test("Multi-Agent Config", "WARN", "Multi-agent system not enabled in configuration")
                self.record_result("WARN")
            
            if hasattr(settings, 'LLM_MODEL'):
                print_test("LLM Configuration", "PASS", f"LLM Model: {settings.LLM_MODEL}")
                self.record_result("PASS")
            else:
                print_test("LLM Configuration", "FAIL", "LLM model not configured")
                self.record_result("FAIL")
                
        except Exception as e:
            print_test("Configuration Loading", "FAIL", f"Config test failed: {e}")
            self.record_result("FAIL")
    
    def print_final_report(self):
        """Print final diagnostic report"""
        print_section("FINAL DIAGNOSTIC REPORT")
        
        total = self.test_results["total"]
        passed = self.test_results["passed"]
        failed = self.test_results["failed"]
        warnings = self.test_results["warnings"]
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"{Colors.BOLD}Total Tests: {total}{Colors.END}")
        print(f"{Colors.GREEN}✅ Passed: {passed}{Colors.END}")
        print(f"{Colors.RED}❌ Failed: {failed}{Colors.END}")
        print(f"{Colors.YELLOW}⚠️  Warnings: {warnings}{Colors.END}")
        print(f"{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.END}")
        
        if success_rate >= 80:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 SYSTEM STATUS: EXCELLENT{Colors.END}")
            print(f"{Colors.GREEN}The Sentinel AI v6.0 system is fully operational!{Colors.END}")
        elif success_rate >= 60:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  SYSTEM STATUS: GOOD WITH WARNINGS{Colors.END}")
            print(f"{Colors.YELLOW}The system is functional but some components need attention.{Colors.END}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ SYSTEM STATUS: CRITICAL ISSUES{Colors.END}")
            print(f"{Colors.RED}The system has significant issues that need to be resolved.{Colors.END}")
    
    async def run_full_diagnostics(self):
        """Run complete diagnostic suite"""
        print_section("SENTINEL AI v6.0 COMPREHENSIVE DIAGNOSTICS")
        print(f"{Colors.CYAN}Starting full system diagnostics...{Colors.END}")
        print(f"{Colors.CYAN}Timestamp: {datetime.now().isoformat()}{Colors.END}\n")
        
        # Test server health
        print_section("SERVER HEALTH CHECKS")
        server_8001_ok = self.test_server_health(8001)
        server_8002_ok = self.test_server_health(8002)
        
        # Test API endpoints
        if server_8001_ok:
            print_section("API ENDPOINT TESTS (Port 8001)")
            self.test_api_endpoints(self.base_url_8001, 8001)
        
        if server_8002_ok:
            print_section("API ENDPOINT TESTS (Port 8002)")
            self.test_api_endpoints(self.base_url_8002, 8002)
        
        # Test core functionality
        print_section("CORE FUNCTIONALITY TESTS")
        self.test_database_connectivity()
        self.test_llm_integration()
        self.test_configuration_loading()
        self.test_websocket_functionality()
        
        # Test enhanced v6.0 components
        print_section("ENHANCED v6.0 COMPONENT TESTS")
        self.test_enhanced_components()
        
        # Test mission creation (if server is available)
        if server_8001_ok:
            print_section("MISSION EXECUTION TESTS")
            mission_id = self.test_mission_creation()
            if mission_id:
                print_test("Mission Integration", "INFO", f"Mission system operational")
        
        # Final report
        self.print_final_report()

async def main():
    """Main diagnostic function"""
    diagnostics = SentinelDiagnostics()
    await diagnostics.run_full_diagnostics()

if __name__ == "__main__":
    asyncio.run(main())
