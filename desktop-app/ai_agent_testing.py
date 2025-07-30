#!/usr/bin/env python3
"""
AI Agent Testing Module for Sentinel System
Comprehensive testing of AI features, agents, and configurations
"""

import os
import sys
import time
import json
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
from loguru import logger

@dataclass
class AITestResult:
    """AI test result data structure"""
    test_name: str
    status: str  # "PASS", "FAIL", "WARNING"
    duration: float
    model_used: str
    prompt: str
    response: str
    tokens_used: Optional[int] = None
    confidence_score: Optional[float] = None
    error: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class AIAgentTester:
    """Comprehensive AI agent testing system"""
    
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.cognitive_url = "http://localhost:8002"
        self.results: List[AITestResult] = []
        
        # Test prompts for different AI capabilities
        self.test_prompts = {
            "code_generation": [
                "Create a Python function that calculates the factorial of a number",
                "Write a function to reverse a string in Python",
                "Create a class for a simple calculator with basic operations"
            ],
            "code_review": [
                "Review this code for best practices: def add(a,b): return a+b",
                "Check this function for potential bugs: def divide(a,b): return a/b",
                "Analyze this code for performance issues: for i in range(1000000): pass"
            ],
            "problem_solving": [
                "How would you solve the problem of finding duplicate elements in an array?",
                "Explain the difference between breadth-first and depth-first search",
                "What's the time complexity of binary search and why?"
            ],
            "documentation": [
                "Write documentation for a function that sorts a list",
                "Create a README for a Python project",
                "Write API documentation for a REST endpoint"
            ],
            "debugging": [
                "Help me debug this error: IndexError: list index out of range",
                "Why does this code fail: x = []; print(x[0])",
                "Fix this code: def get_item(lst, idx): return lst[idx]"
            ]
        }
    
    def test_ai_generation(self, prompt: str, expected_type: str = "code") -> AITestResult:
        """Test AI code generation capability"""
        start_time = time.time()
        
        try:
            logger.info(f"[AI] Testing AI generation: {prompt[:50]}...")
            
            response = requests.post(
                f"{self.cognitive_url}/generate",
                json={
                    "prompt": prompt,
                    "model": "gemini-1.5-pro-latest",
                    "max_tokens": 1000
                },
                timeout=60
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Analyze response quality
                response_text = result.get("response", "")
                quality_score = self.analyze_response_quality(response_text, expected_type)
                
                return AITestResult(
                    test_name=f"AI Generation - {expected_type}",
                    status="PASS" if quality_score > 0.7 else "WARNING",
                    duration=duration,
                    model_used=result.get("model", "unknown"),
                    prompt=prompt,
                    response=response_text,
                    tokens_used=result.get("tokens_used"),
                    confidence_score=quality_score
                )
            else:
                return AITestResult(
                    test_name=f"AI Generation - {expected_type}",
                    status="FAIL",
                    duration=duration,
                    model_used="unknown",
                    prompt=prompt,
                    response="",
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            duration = time.time() - start_time
            return AITestResult(
                test_name=f"AI Generation - {expected_type}",
                status="FAIL",
                duration=duration,
                model_used="unknown",
                prompt=prompt,
                response="",
                error=str(e)
            )
    
    def test_mission_execution(self, prompt: str, agent_type: str = "developer") -> AITestResult:
        """Test complete mission execution"""
        start_time = time.time()
        
        try:
            logger.info(f"[TARGET] Testing mission execution: {prompt[:50]}...")
            
            mission_id = f"test_mission_{int(time.time())}"
            
            response = requests.post(
                f"{self.cognitive_url}/mission",
                json={
                    "prompt": prompt,
                    "mission_id": mission_id,
                    "agent_type": agent_type
                },
                timeout=120
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Check mission status
                status_response = requests.get(f"{self.base_url}/mission/{mission_id}")
                if status_response.status_code == 200:
                    mission_status = status_response.json()
                    final_status = mission_status.get("status", "unknown")
                    
                    return AITestResult(
                        test_name=f"Mission Execution - {agent_type}",
                        status="PASS" if final_status == "completed" else "WARNING",
                        duration=duration,
                        model_used=result.get("model", "unknown"),
                        prompt=prompt,
                        response=str(result),
                        confidence_score=1.0 if final_status == "completed" else 0.5
                    )
                else:
                    return AITestResult(
                        test_name=f"Mission Execution - {agent_type}",
                        status="WARNING",
                        duration=duration,
                        model_used="unknown",
                        prompt=prompt,
                        response=str(result),
                        error="Could not verify mission status"
                    )
            else:
                return AITestResult(
                    test_name=f"Mission Execution - {agent_type}",
                    status="FAIL",
                    duration=duration,
                    model_used="unknown",
                    prompt=prompt,
                    response="",
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            duration = time.time() - start_time
            return AITestResult(
                test_name=f"Mission Execution - {agent_type}",
                status="FAIL",
                duration=duration,
                model_used="unknown",
                prompt=prompt,
                response="",
                error=str(e)
            )
    
    def test_agent_types(self) -> List[AITestResult]:
        """Test different agent types"""
        logger.info("[BOT] Testing different agent types...")
        
        agent_types = ["developer", "analyst", "researcher", "debugger"]
        results = []
        
        for agent_type in agent_types:
            prompt = f"Create a simple {agent_type} task to test capabilities"
            result = self.test_mission_execution(prompt, agent_type)
            results.append(result)
        
        return results
    
    def test_ai_capabilities(self) -> List[AITestResult]:
        """Test various AI capabilities"""
        logger.info("[AI] Testing AI capabilities...")
        
        results = []
        
        # Test code generation
        for prompt in self.test_prompts["code_generation"]:
            result = self.test_ai_generation(prompt, "code")
            results.append(result)
        
        # Test code review
        for prompt in self.test_prompts["code_review"]:
            result = self.test_ai_generation(prompt, "review")
            results.append(result)
        
        # Test problem solving
        for prompt in self.test_prompts["problem_solving"]:
            result = self.test_ai_generation(prompt, "problem_solving")
            results.append(result)
        
        return results
    
    def test_ai_performance(self) -> Dict[str, Any]:
        """Test AI performance under load"""
        logger.info("[PERF] Testing AI performance...")
        
        # Test concurrent requests
        start_time = time.time()
        concurrent_results = []
        
        def make_concurrent_request(prompt: str):
            try:
                response = requests.post(
                    f"{self.cognitive_url}/generate",
                    json={"prompt": prompt},
                    timeout=30
                )
                return response.status_code == 200
            except:
                return False
        
        # Run concurrent tests
        import threading
        threads = []
        for i in range(5):
            prompt = f"Generate a simple function {i}"
            thread = threading.Thread(target=lambda: concurrent_results.append(make_concurrent_request(prompt)))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        duration = time.time() - start_time
        success_rate = sum(concurrent_results) / len(concurrent_results)
        
        return {
            "concurrent_requests": len(concurrent_results),
            "success_rate": success_rate,
            "total_duration": duration,
            "avg_response_time": duration / len(concurrent_results) if concurrent_results else 0
        }
    
    def test_ai_configuration(self) -> Dict[str, Any]:
        """Test AI configuration and settings"""
        logger.info("[CONFIG] Testing AI configuration...")
        
        config_tests = {}
        
        try:
            # Test model availability
            response = requests.get(f"{self.cognitive_url}/health")
            if response.status_code == 200:
                config_tests["model_availability"] = "PASS"
            else:
                config_tests["model_availability"] = "FAIL"
            
            # Test API key configuration
            response = requests.post(
                f"{self.cognitive_url}/generate",
                json={"prompt": "test"},
                timeout=10
            )
            
            if response.status_code == 200:
                config_tests["api_key"] = "PASS"
            elif response.status_code == 401:
                config_tests["api_key"] = "FAIL - Invalid API key"
            else:
                config_tests["api_key"] = f"WARNING - Status {response.status_code}"
            
            # Test model parameters
            response = requests.post(
                f"{self.cognitive_url}/generate",
                json={
                    "prompt": "test",
                    "temperature": 0.7,
                    "max_tokens": 100
                },
                timeout=10
            )
            
            if response.status_code == 200:
                config_tests["model_parameters"] = "PASS"
            else:
                config_tests["model_parameters"] = f"FAIL - Status {response.status_code}"
            
        except Exception as e:
            config_tests["error"] = str(e)
        
        return config_tests
    
    def analyze_response_quality(self, response: str, expected_type: str) -> float:
        """Analyze the quality of AI response"""
        if not response:
            return 0.0
        
        score = 0.0
        
        # Basic length check
        if len(response) > 50:
            score += 0.2
        
        # Content type analysis
        if expected_type == "code":
            if "def " in response or "class " in response or "import " in response:
                score += 0.3
            if "return" in response or "print" in response:
                score += 0.2
        elif expected_type == "review":
            if any(word in response.lower() for word in ["bug", "issue", "problem", "improve", "better"]):
                score += 0.3
        elif expected_type == "problem_solving":
            if any(word in response.lower() for word in ["algorithm", "complexity", "solution", "approach"]):
                score += 0.3
        
        # Structure analysis
        if response.count("\n") > 2:
            score += 0.2
        
        # Completeness check
        if response.endswith((".", ":", "}")) or len(response.split()) > 20:
            score += 0.1
        
        return min(score, 1.0)
    
    def run_comprehensive_ai_tests(self) -> Dict[str, Any]:
        """Run comprehensive AI testing suite"""
        logger.info("[STARTUP] Starting comprehensive AI testing suite...")
        
        all_results = []
        
        # Test AI capabilities
        capability_results = self.test_ai_capabilities()
        all_results.extend(capability_results)
        
        # Test agent types
        agent_results = self.test_agent_types()
        all_results.extend(agent_results)
        
        # Test performance
        performance_results = self.test_ai_performance()
        
        # Test configuration
        config_results = self.test_ai_configuration()
        
        # Generate comprehensive report
        total_tests = len(all_results)
        passed_tests = len([r for r in all_results if r.status == "PASS"])
        failed_tests = len([r for r in all_results if r.status == "FAIL"])
        warning_tests = len([r for r in all_results if r.status == "WARNING"])
        
        avg_duration = sum(r.duration for r in all_results) / total_tests if total_tests > 0 else 0
        avg_confidence = sum(r.confidence_score or 0 for r in all_results) / total_tests if total_tests > 0 else 0
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "warnings": warning_tests,
                "success_rate": f"{(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%",
                "avg_duration": f"{avg_duration:.2f}s",
                "avg_confidence": f"{avg_confidence:.2f}"
            },
            "performance_metrics": performance_results,
            "configuration_status": config_results,
            "detailed_results": [self._result_to_dict(r) for r in all_results],
            "recommendations": self._generate_ai_recommendations(all_results, performance_results, config_results),
            "timestamp": datetime.now().isoformat()
        }
        
        return report
    
    def _result_to_dict(self, result: AITestResult) -> Dict[str, Any]:
        """Convert test result to dictionary"""
        return {
            "test_name": result.test_name,
            "status": result.status,
            "duration": result.duration,
            "model_used": result.model_used,
            "prompt": result.prompt,
            "response": result.response[:200] + "..." if len(result.response) > 200 else result.response,
            "tokens_used": result.tokens_used,
            "confidence_score": result.confidence_score,
            "error": result.error,
            "timestamp": result.timestamp
        }
    
    def _generate_ai_recommendations(self, results: List[AITestResult], 
                                   performance: Dict[str, Any], 
                                   config: Dict[str, Any]) -> List[str]:
        """Generate AI-specific recommendations"""
        recommendations = []
        
        # Analyze test results
        failed_tests = [r for r in results if r.status == "FAIL"]
        slow_tests = [r for r in results if r.duration > 30]
        low_confidence_tests = [r for r in results if r.confidence_score and r.confidence_score < 0.5]
        
        if failed_tests:
            recommendations.append(f"🔴 {len(failed_tests)} AI tests failed - Check model configuration and API keys")
        
        if slow_tests:
            recommendations.append(f"🟡 {len(slow_tests)} AI tests are slow - Consider model optimization")
        
        if low_confidence_tests:
            recommendations.append(f"🟡 {len(low_confidence_tests)} AI responses have low confidence - Review prompts")
        
        # Analyze performance
        if performance.get("success_rate", 0) < 0.8:
            recommendations.append("🔴 Low concurrent request success rate - Check system resources")
        
        if performance.get("avg_response_time", 0) > 10:
            recommendations.append("🟡 High average response time - Consider model optimization")
        
        # Analyze configuration
        if config.get("api_key") != "PASS":
            recommendations.append("🔴 API key configuration issue - Check environment variables")
        
        if config.get("model_availability") != "PASS":
            recommendations.append("🔴 Model availability issue - Check AI service status")
        
        if not failed_tests and not slow_tests and performance.get("success_rate", 0) >= 0.8:
            recommendations.append("[OK] AI system is performing well - Continue monitoring")
        
        return recommendations
    
    def print_ai_test_report(self, report: Dict[str, Any]):
        """Print comprehensive AI test report"""
        print("\n" + "="*80)
        print("[AI] SENTINEL AI COMPREHENSIVE TEST REPORT")
        print("="*80)
        
        summary = report["test_summary"]
        print(f"\n[STATS] AI TEST SUMMARY:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   [OK] Passed: {summary['passed']}")
        print(f"   [ERROR] Failed: {summary['failed']}")
        print(f"   [WARN] Warnings: {summary['warnings']}")
        print(f"   Success Rate: {summary['success_rate']}")
        print(f"   Avg Duration: {summary['avg_duration']}")
        print(f"   Avg Confidence: {summary['avg_confidence']}")
        
        performance = report["performance_metrics"]
        print(f"\n[PERF] AI PERFORMANCE:")
        print(f"   Concurrent Requests: {performance.get('concurrent_requests', 0)}")
        print(f"   Success Rate: {performance.get('success_rate', 0):.1%}")
        print(f"   Avg Response Time: {performance.get('avg_response_time', 0):.2f}s")
        
        config = report["configuration_status"]
        print(f"\n[CONFIG] AI CONFIGURATION:")
        for key, value in config.items():
            status_icon = "[OK]" if value == "PASS" else "[ERROR]" if "FAIL" in str(value) else "[WARN]"
            print(f"   {status_icon} {key}: {value}")
        
        print(f"\n💡 AI RECOMMENDATIONS:")
        for rec in report["recommendations"]:
            print(f"   {rec}")
        
        print(f"\n📅 Report Generated: {report['timestamp']}")
        print("="*80)

def main():
    """Main entry point for AI testing"""
    print(f"[AI] Starting Sentinel AI Comprehensive Testing...")
    
    try:
        tester = AIAgentTester()
        report = tester.run_comprehensive_ai_tests()
        tester.print_ai_test_report(report)
        
        # Save detailed report
        report_file = f"logs/ai_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Detailed AI report saved to: {report_file}")
        
        # Return success based on test results
        failed_tests = report["test_summary"]["failed"]
        if failed_tests == 0:
            print(f"\n[OK] All AI tests passed! AI system is fully operational.")
            return True
        else:
            print(f"\n[ERROR] {failed_tests} AI tests failed. Check the detailed report.")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] AI testing failed: {e}")
        logger.error(f"AI testing failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 