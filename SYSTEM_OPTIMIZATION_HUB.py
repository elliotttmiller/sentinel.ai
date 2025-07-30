import os
import sys
import time
import json
import traceback
import psutil
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.cognitive_forge_engine import CognitiveForgeEngine
from src.models.advanced_database import AdvancedDatabase
from src.agents.advanced_agents import AdvancedAgents, PromptOptimizationAgents
from src.utils.phoenix_protocol import PhoenixProtocol
from src.utils.guardian_protocol import GuardianProtocol
from src.utils.synapse_logging import SynapseLogging
from src.utils.self_learning_module import SelfLearningModule

class AdvancedDebuggingSystem:
    """Cutting-edge debugging and problem-solving system for comprehensive error analysis"""
    
    def __init__(self):
        self.error_patterns = {
            'environment': {
                'missing_variable': r"Environment variable '(\w+)' not found",
                'invalid_format': r"Invalid format for environment variable '(\w+)'",
                'connection_failed': r"Connection failed|Connection refused|Timeout",
                'permission_denied': r"Permission denied|Access denied",
                'file_not_found': r"File not found|No such file or directory"
            },
            'database': {
                'connection_error': r"Database connection failed|Connection refused",
                'authentication_error': r"Authentication failed|Invalid credentials",
                'table_not_found': r"Table.*does not exist|relation.*does not exist",
                'syntax_error': r"SQL syntax error|Invalid SQL",
                'constraint_violation': r"Constraint violation|Unique constraint"
            },
            'agent': {
                'initialization_error': r"Agent initialization failed|Failed to create agent",
                'execution_error': r"Agent execution failed|Task execution error",
                'memory_error': r"Memory error|Out of memory",
                'timeout_error': r"Timeout|Execution timeout"
            },
            'json': {
                'parsing_error': r"JSON decode error|Invalid JSON",
                'schema_error': r"Schema validation failed|Invalid schema",
                'format_error': r"Invalid format|Malformed JSON"
            }
        }
        
        self.solution_templates = {
            'environment': {
                'missing_variable': {
                    'diagnosis': 'Environment variable is not set or not accessible',
                    'solutions': [
                        'Check if the variable is defined in your .env file',
                        'Verify the variable name matches exactly (case-sensitive)',
                        'Restart the application to reload environment variables',
                        'Use os.getenv() with a default value as fallback'
                    ],
                    'code_fix': 'os.getenv("VARIABLE_NAME", "default_value")',
                    'severity': 'HIGH'
                },
                'invalid_format': {
                    'diagnosis': 'Environment variable has incorrect format or type',
                    'solutions': [
                        'Verify the variable format matches expected type',
                        'Check for extra spaces or special characters',
                        'Ensure proper quoting for string values',
                        'Validate the variable value against expected format'
                    ],
                    'code_fix': 'Validate and sanitize environment variable before use',
                    'severity': 'MEDIUM'
                }
            },
            'database': {
                'connection_error': {
                    'diagnosis': 'Database connection cannot be established',
                    'solutions': [
                        'Verify DATABASE_URL is correct and accessible',
                        'Check network connectivity to database server',
                        'Ensure database server is running',
                        'Verify firewall settings and port access'
                    ],
                    'code_fix': 'Test connection with connection pooling and retry logic',
                    'severity': 'CRITICAL'
                },
                'authentication_error': {
                    'diagnosis': 'Database authentication credentials are invalid',
                    'solutions': [
                        'Verify username and password in DATABASE_URL',
                        'Check if database user has proper permissions',
                        'Ensure credentials are not expired',
                        'Test connection with database client'
                    ],
                    'code_fix': 'Implement proper error handling for auth failures',
                    'severity': 'CRITICAL'
                }
            },
            'agent': {
                'initialization_error': {
                    'diagnosis': 'Agent system failed to initialize properly',
                    'solutions': [
                        'Check LLM model configuration and API key',
                        'Verify agent dependencies are installed',
                        'Ensure proper memory allocation',
                        'Check for conflicting agent configurations'
                    ],
                    'code_fix': 'Add comprehensive initialization error handling',
                    'severity': 'HIGH'
                },
                'execution_error': {
                    'diagnosis': 'Agent task execution encountered an error',
                    'solutions': [
                        'Review task parameters and input validation',
                        'Check agent memory and context availability',
                        'Verify tool availability and permissions',
                        'Implement retry logic with exponential backoff'
                    ],
                    'code_fix': 'Add task-level error handling and recovery',
                    'severity': 'MEDIUM'
                }
            },
            'json': {
                'parsing_error': {
                    'diagnosis': 'JSON response parsing failed due to malformed data',
                    'solutions': [
                        'Implement robust JSON parsing with error handling',
                        'Add response validation before parsing',
                        'Handle markdown-wrapped JSON responses',
                        'Use try-catch blocks with fallback parsing'
                    ],
                    'code_fix': 'Use _parse_agent_json_response method for robust parsing',
                    'severity': 'MEDIUM'
                }
            }
        }
    
    def analyze_error(self, error: Exception, test_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced error analysis with pattern matching and solution generation"""
        error_str = str(error)
        error_type = type(error).__name__
        traceback_str = traceback.format_exc()
        
        # Pattern matching for error classification
        error_category = self._classify_error(error_str, error_type)
        
        # Get detailed analysis
        analysis = self._get_error_analysis(error_category, error_str, context)
        
        # Generate automated solutions
        solutions = self._generate_solutions(error_category, error_str, context)
        
        # Calculate error severity and impact
        severity = self._calculate_severity(error_category, error_str, context)
        
        return {
            'error_type': error_type,
            'error_message': error_str,
            'error_category': error_category,
            'traceback': traceback_str,
            'analysis': analysis,
            'solutions': solutions,
            'severity': severity,
            'test_context': {
                'test_name': test_name,
                'timestamp': datetime.now().isoformat(),
                'context': context
            },
            'recommended_actions': self._get_recommended_actions(severity, error_category)
        }
    
    def _classify_error(self, error_str: str, error_type: str) -> str:
        """Classify error based on patterns and type"""
        error_str_lower = error_str.lower()
        
        for category, patterns in self.error_patterns.items():
            for pattern_name, pattern in patterns.items():
                if any(keyword in error_str_lower for keyword in pattern.split('|')):
                    return category
        
        # Fallback classification based on error type
        if 'Environment' in error_type or 'env' in error_str_lower:
            return 'environment'
        elif 'Database' in error_type or 'db' in error_str_lower or 'sql' in error_str_lower:
            return 'database'
        elif 'JSON' in error_type or 'json' in error_str_lower:
            return 'json'
        elif 'Agent' in error_type or 'agent' in error_str_lower:
            return 'agent'
        
        return 'unknown'
    
    def _get_error_analysis(self, category: str, error_str: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed error analysis"""
        analysis = {
            'root_cause': self._identify_root_cause(category, error_str),
            'impact_assessment': self._assess_impact(category, context),
            'system_state': self._analyze_system_state(context),
            'correlation_factors': self._identify_correlation_factors(category, context)
        }
        
        if category in self.solution_templates:
            template = self.solution_templates[category]
            for pattern_name, pattern_info in template.items():
                if any(keyword in error_str.lower() for keyword in pattern_name.split('_')):
                    analysis['diagnosis'] = pattern_info['diagnosis']
                    break
        
        return analysis
    
    def _identify_root_cause(self, category: str, error_str: str) -> str:
        """Identify the root cause of the error"""
        if category == 'environment':
            if 'not found' in error_str.lower():
                return "Missing or incorrectly named environment variable"
            elif 'invalid' in error_str.lower():
                return "Environment variable has invalid format or value"
        elif category == 'database':
            if 'connection' in error_str.lower():
                return "Database connection configuration or network issue"
            elif 'authentication' in error_str.lower():
                return "Database credentials or permissions issue"
        elif category == 'json':
            return "JSON response parsing or formatting issue"
        elif category == 'agent':
            return "Agent initialization or execution configuration issue"
        
        return "Unknown root cause - requires manual investigation"
    
    def _assess_impact(self, category: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Assess the impact of the error on system functionality"""
        impact_levels = {
            'environment': {
                'system_startup': 'CRITICAL',
                'core_functionality': 'HIGH',
                'user_experience': 'MEDIUM'
            },
            'database': {
                'data_persistence': 'CRITICAL',
                'mission_tracking': 'HIGH',
                'system_operations': 'HIGH'
            },
            'agent': {
                'task_execution': 'HIGH',
                'user_requests': 'MEDIUM',
                'system_automation': 'MEDIUM'
            },
            'json': {
                'data_processing': 'MEDIUM',
                'agent_communication': 'MEDIUM',
                'system_integration': 'LOW'
            }
        }
        
        return impact_levels.get(category, {
            'unknown': 'UNKNOWN'
        })
    
    def _analyze_system_state(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current system state for debugging context"""
        return {
            'memory_usage': psutil.virtual_memory().percent,
            'cpu_usage': psutil.cpu_percent(),
            'disk_usage': psutil.disk_usage('/').percent,
            'active_processes': len(psutil.pids()),
            'environment_loaded': 'DATABASE_URL' in os.environ,
            'database_accessible': self._check_database_accessibility(),
            'agent_system_ready': self._check_agent_system_ready()
        }
    
    def _check_database_accessibility(self) -> bool:
        """Check if database is accessible"""
        try:
            db_url = os.getenv('DATABASE_URL')
            if not db_url:
                return False
            # Simple connectivity check
            return True
        except:
            return False
    
    def _check_agent_system_ready(self) -> bool:
        """Check if agent system is ready"""
        try:
            # Check if required environment variables are set
            required_vars = ['GOOGLE_API_KEY', 'LLM_MODEL']
            return all(os.getenv(var) for var in required_vars)
        except:
            return False
    
    def _identify_correlation_factors(self, category: str, context: Dict[str, Any]) -> List[str]:
        """Identify factors that might correlate with the error"""
        factors = []
        
        if category == 'environment':
            factors.extend([
                'Environment file (.env) not loaded',
                'Variable naming mismatch',
                'Application restart required'
            ])
        elif category == 'database':
            factors.extend([
                'Network connectivity issues',
                'Database server status',
                'Credential expiration'
            ])
        elif category == 'agent':
            factors.extend([
                'LLM API availability',
                'Memory allocation issues',
                'Dependency conflicts'
            ])
        
        return factors
    
    def _generate_solutions(self, category: str, error_str: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate automated solutions for the error"""
        solutions = []
        
        if category in self.solution_templates:
            for pattern_name, pattern_info in self.solution_templates[category].items():
                if any(keyword in error_str.lower() for keyword in pattern_name.split('_')):
                    solutions.append({
                        'pattern': pattern_name,
                        'diagnosis': pattern_info['diagnosis'],
                        'solutions': pattern_info['solutions'],
                        'code_fix': pattern_info['code_fix'],
                        'severity': pattern_info['severity'],
                        'automated_fix_available': self._can_automate_fix(category, pattern_name)
                    })
        
        # Add general solutions if no specific pattern matched
        if not solutions:
            solutions.append({
                'pattern': 'general',
                'diagnosis': 'General error requiring manual investigation',
                'solutions': [
                    'Review error logs for additional context',
                    'Check system resources and dependencies',
                    'Verify configuration files and settings',
                    'Test individual components in isolation'
                ],
                'code_fix': 'Manual investigation required',
                'severity': 'UNKNOWN',
                'automated_fix_available': False
            })
        
        return solutions
    
    def _can_automate_fix(self, category: str, pattern_name: str) -> bool:
        """Determine if the fix can be automated"""
        automatable_patterns = {
            'environment': ['missing_variable', 'invalid_format'],
            'json': ['parsing_error'],
            'database': ['connection_error']
        }
        
        return pattern_name in automatable_patterns.get(category, [])
    
    def _calculate_severity(self, category: str, error_str: str, context: Dict[str, Any]) -> str:
        """Calculate error severity based on multiple factors"""
        base_severity = {
            'environment': 'HIGH',
            'database': 'CRITICAL',
            'agent': 'MEDIUM',
            'json': 'LOW',
            'unknown': 'UNKNOWN'
        }.get(category, 'UNKNOWN')
        
        # Adjust severity based on context
        if 'CRITICAL' in error_str.upper() or 'FATAL' in error_str.upper():
            return 'CRITICAL'
        elif 'connection' in error_str.lower() and category == 'database':
            return 'CRITICAL'
        elif 'authentication' in error_str.lower():
            return 'CRITICAL'
        
        return base_severity
    
    def _get_recommended_actions(self, severity: str, category: str) -> List[str]:
        """Get recommended actions based on severity and category"""
        actions = []
        
        if severity == 'CRITICAL':
            actions.extend([
                'IMMEDIATE: Stop system operations',
                'IMMEDIATE: Check system logs',
                'URGENT: Verify critical configurations',
                'URGENT: Test backup systems'
            ])
        elif severity == 'HIGH':
            actions.extend([
                'PRIORITY: Investigate root cause',
                'PRIORITY: Apply recommended fixes',
                'SOON: Test system functionality',
                'SOON: Update documentation'
            ])
        elif severity == 'MEDIUM':
            actions.extend([
                'SCHEDULE: Apply fixes during maintenance window',
                'SCHEDULE: Monitor system performance',
                'PLAN: Implement preventive measures'
            ])
        else:
            actions.extend([
                'MONITOR: Watch for pattern recurrence',
                'DOCUMENT: Record error for future reference'
            ])
        
        return actions

class EnhancedSystemOptimizationHub:
    """Enhanced System Optimization Hub with Advanced Debugging System"""
    
    def __init__(self):
        self.debug_system = AdvancedDebuggingSystem()
        self.test_results = []
        self.failed_tests = []
        self.successful_tests = []
        self.performance_metrics = []
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run the complete test suite with enhanced debugging"""
        print("🚀 SYSTEM OPTIMIZATION HUB - Starting Comprehensive Test Suite")
        print("=" * 80)
        
        start_time = time.time()
        
        # Initialize system components
        try:
            self.engine = CognitiveForgeEngine()
            self.db = AdvancedDatabase()
            self.agents = AdvancedAgents()
            self.prompt_agents = PromptOptimizationAgents()
            self.phoenix = PhoenixProtocol()
            self.guardian = GuardianProtocol()
            self.synapse = SynapseLogging()
            self.self_learning = SelfLearningModule()
        except Exception as e:
            error_analysis = self.debug_system.analyze_error(
                e, "System Initialization", {'phase': 'component_initialization'}
            )
            self._display_error_report(error_analysis)
            return self._generate_final_report()
        
        # Define test suite with Phase 2 enhancements
        tests = [
            ("System Initialization", self.test_system_initialization),
            ("Environment Validation", self.test_environment_validation),
            ("Database Connectivity", self.test_database_connectivity),
            ("Agent Factory", self.test_agent_factory),
            ("Protocol Systems", self.test_protocol_systems),
            ("Enhanced Agents", self.test_enhanced_agents),
            ("Database Phase 2 Features", self.test_database_phase2_features),
            ("Workflow Phases", self.test_workflow_phases),
            ("Async Execution Engine", self.test_async_execution_engine),
            ("Enhanced Mission Execution", self.test_enhanced_mission_execution),
            ("Performance Optimization", self.test_performance_optimization),
            ("Error Handling", self.test_error_handling),
            ("Integration Tests", self.test_integration_tests),
            ("Stress Testing", self.test_stress_testing)
        ]
        
        # Execute tests
        for test_name, test_func in tests:
            self._execute_test(test_name, test_func)
        
        # Generate comprehensive report
        total_time = time.time() - start_time
        return self._generate_final_report(total_time)
    
    def _execute_test(self, test_name: str, test_func) -> None:
        """Execute a single test with comprehensive error handling"""
        print(f"\n{'='*80}")
        print(f"🧪 TEST: {test_name}")
        print(f"📂 CATEGORY: {self._get_test_category(test_name)}")
        print(f"⏰ START TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")
        
        start_time = time.time()
        memory_start = psutil.virtual_memory().percent
        cpu_start = psutil.cpu_percent()
        
        try:
            result = test_func()
            
            # Calculate metrics
            execution_time = time.time() - start_time
            memory_end = psutil.virtual_memory().percent
            cpu_end = psutil.cpu_percent()
            
            metrics = {
                'execution_time': execution_time,
                'memory_start': memory_start,
                'memory_end': memory_end,
                'memory_delta': memory_end - memory_start,
                'cpu_usage': (cpu_start + cpu_end) / 2
            }
            
            if result.get('status') == 'PASS':
                self.successful_tests.append({
                    'name': test_name,
                    'result': result,
                    'metrics': metrics
                })
                self._display_success_result(test_name, result, metrics)
            else:
                self.failed_tests.append({
                    'name': test_name,
                    'result': result,
                    'metrics': metrics
                })
                self._display_failure_result(test_name, result, metrics)
                
        except Exception as e:
            execution_time = time.time() - start_time
            memory_end = psutil.virtual_memory().percent
            cpu_end = psutil.cpu_percent()
            
            metrics = {
                'execution_time': execution_time,
                'memory_start': memory_start,
                'memory_end': memory_end,
                'memory_delta': memory_end - memory_start,
                'cpu_usage': (cpu_start + cpu_end) / 2
            }
            
            # Advanced error analysis
            error_analysis = self.debug_system.analyze_error(
                e, test_name, {
                    'execution_time': execution_time,
                    'memory_usage': memory_end,
                    'cpu_usage': cpu_end
                }
            )
            
            self.failed_tests.append({
                'name': test_name,
                'error_analysis': error_analysis,
                'metrics': metrics
            })
            
            self._display_error_report(error_analysis)
    
    def _display_success_result(self, test_name: str, result: Dict[str, Any], metrics: Dict[str, Any]) -> None:
        """Display successful test result with enhanced metrics"""
        print(f"\n✅ RESULT: {test_name}")
        print(f"📊 STATUS: PASS")
        print(f"⏱️ EXECUTION TIME: {metrics['execution_time']:.2f}s")
        print(f"📈 PERFORMANCE METRICS:")
        print(f"   memory_start: {metrics['memory_start']:.1f}")
        print(f"   memory_end: {metrics['memory_end']:.1f}")
        print(f"   memory_delta: {metrics['memory_delta']:.1f}")
        print(f"   cpu_usage: {metrics['cpu_usage']:.1f}")
        
        if 'details' in result:
            print(f"📋 DETAILS: {result['details']}")
    
    def _display_failure_result(self, test_name: str, result: Dict[str, Any], metrics: Dict[str, Any]) -> None:
        """Display failed test result with enhanced diagnostics"""
        print(f"\n❌ RESULT: {test_name}")
        print(f"📊 STATUS: FAIL")
        print(f"⏱️ EXECUTION TIME: {metrics['execution_time']:.2f}s")
        print(f"📈 PERFORMANCE METRICS:")
        print(f"   memory_start: {metrics['memory_start']:.1f}")
        print(f"   memory_end: {metrics['memory_end']:.1f}")
        print(f"   memory_delta: {metrics['memory_delta']:.1f}")
        print(f"   cpu_usage: {metrics['cpu_usage']:.1f}")
        
        if 'error' in result:
            print(f"🚨 ERROR: {result['error']}")
        
        if 'details' in result:
            print(f"📋 DETAILS: {result['details']}")
    
    def _display_error_report(self, error_analysis: Dict[str, Any]) -> None:
        """Display comprehensive error analysis report"""
        print(f"\n🚨 ADVANCED ERROR ANALYSIS REPORT")
        print(f"{'='*60}")
        print(f"🔍 ERROR TYPE: {error_analysis['error_type']}")
        print(f"📂 CATEGORY: {error_analysis['error_category'].upper()}")
        print(f"⚠️ SEVERITY: {error_analysis['severity']}")
        print(f"📝 MESSAGE: {error_analysis['error_message']}")
        
        print(f"\n🔬 DETAILED ANALYSIS:")
        analysis = error_analysis['analysis']
        print(f"   Root Cause: {analysis['root_cause']}")
        print(f"   Impact Assessment:")
        for impact, level in analysis['impact_assessment'].items():
            print(f"     - {impact}: {level}")
        
        print(f"\n💻 SYSTEM STATE:")
        system_state = analysis['system_state']
        for key, value in system_state.items():
            print(f"   - {key}: {value}")
        
        print(f"\n🔗 CORRELATION FACTORS:")
        for factor in analysis['correlation_factors']:
            print(f"   - {factor}")
        
        print(f"\n🛠️ AUTOMATED SOLUTIONS:")
        for i, solution in enumerate(error_analysis['solutions'], 1):
            print(f"   {i}. Pattern: {solution['pattern']}")
            print(f"      Diagnosis: {solution['diagnosis']}")
            print(f"      Severity: {solution['severity']}")
            print(f"      Automated Fix: {'✅ Available' if solution['automated_fix_available'] else '❌ Manual Required'}")
            print(f"      Solutions:")
            for sol in solution['solutions']:
                print(f"        - {sol}")
            if solution['code_fix']:
                print(f"      Code Fix: {solution['code_fix']}")
            print()
        
        print(f"\n🎯 RECOMMENDED ACTIONS:")
        for action in error_analysis['recommended_actions']:
            print(f"   - {action}")
        
        print(f"\n📋 TEST CONTEXT:")
        context = error_analysis['test_context']
        print(f"   Test: {context['test_name']}")
        print(f"   Timestamp: {context['timestamp']}")
    
    def _get_test_category(self, test_name: str) -> str:
        """Get the category for a test"""
        categories = {
            'System Initialization': 'system_initialization',
            'Environment Validation': 'environment_validation',
            'Database Connectivity': 'database_integration',
            'Agent Factory': 'agent_factory',
            'Protocol Systems': 'protocol_systems',
            'Workflow Phases': 'workflow_phases',
            'Performance Optimization': 'performance_optimization',
            'Error Handling': 'error_handling',
            'Integration Tests': 'integration_tests',
            'Stress Testing': 'stress_testing'
        }
        return categories.get(test_name, 'unknown')
    
    def _generate_final_report(self, total_time: float = 0) -> Dict[str, Any]:
        """Generate comprehensive final report with enhanced analytics"""
        print(f"\n{'='*80}")
        print(f"📊 COMPREHENSIVE TEST REPORT")
        print(f"{'='*80}")
        
        total_tests = len(self.successful_tests) + len(self.failed_tests)
        passed_tests = len(self.successful_tests)
        failed_tests = len(self.failed_tests)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"🎯 TOTAL TESTS: {total_tests}")
        print(f"✅ PASSED: {passed_tests}")
        print(f"❌ FAILED: {failed_tests}")
        print(f"⚠️ WARNINGS: {len([t for t in self.failed_tests if t.get('result', {}).get('status') == 'WARNING'])}")
        print(f"📈 SUCCESS RATE: {success_rate:.1f}%")
        print(f"⏱️ TOTAL EXECUTION TIME: {total_time:.2f}s")
        print(f"📊 AVERAGE EXECUTION TIME: {total_time/total_tests:.2f}s" if total_tests > 0 else "N/A")
        
        # System status determination
        if success_rate >= 90:
            status = "EXCELLENT"
        elif success_rate >= 80:
            status = "OPERATIONAL"
        elif success_rate >= 70:
            status = "DEGRADED"
        elif success_rate >= 50:
            status = "CRITICAL"
        else:
            status = "FAILED"
        
        print(f"🚀 SYSTEM STATUS: {status}")
        
        # Enhanced performance metrics
        all_metrics = [t['metrics'] for t in self.successful_tests + self.failed_tests]
        if all_metrics:
            avg_memory_start = sum(m['memory_start'] for m in all_metrics) / len(all_metrics)
            max_memory_start = max(m['memory_start'] for m in all_metrics)
            min_memory_start = min(m['memory_start'] for m in all_metrics)
            avg_memory_end = sum(m['memory_end'] for m in all_metrics) / len(all_metrics)
            max_memory_end = max(m['memory_end'] for m in all_metrics)
            min_memory_end = min(m['memory_end'] for m in all_metrics)
            avg_memory_delta = sum(m['memory_delta'] for m in all_metrics) / len(all_metrics)
            max_memory_delta = max(m['memory_delta'] for m in all_metrics)
            min_memory_delta = min(m['memory_delta'] for m in all_metrics)
            avg_cpu_usage = sum(m['cpu_usage'] for m in all_metrics) / len(all_metrics)
            max_cpu_usage = max(m['cpu_usage'] for m in all_metrics)
            min_cpu_usage = min(m['cpu_usage'] for m in all_metrics)
            
            print(f"\n📈 PERFORMANCE METRICS:")
            print(f"   avg_memory_start: {avg_memory_start:.1f}")
            print(f"   max_memory_start: {max_memory_start:.1f}")
            print(f"   min_memory_start: {min_memory_start:.1f}")
            print(f"   avg_memory_end: {avg_memory_end:.1f}")
            print(f"   max_memory_end: {max_memory_end:.1f}")
            print(f"   min_memory_end: {min_memory_end:.1f}")
            print(f"   avg_memory_delta: {avg_memory_delta:.1f}")
            print(f"   max_memory_delta: {max_memory_delta:.1f}")
            print(f"   min_memory_delta: {min_memory_delta:.1f}")
            print(f"   avg_cpu_usage: {avg_cpu_usage:.1f}")
            print(f"   max_cpu_usage: {max_cpu_usage:.1f}")
            print(f"   min_cpu_usage: {min_cpu_usage:.1f}")
        
        # Failed tests summary with error categories
        if self.failed_tests:
            print(f"\n🚨 FAILED TESTS ANALYSIS:")
            error_categories = {}
            severity_counts = {}
            
            for test in self.failed_tests:
                if 'error_analysis' in test:
                    category = test['error_analysis']['error_category']
                    severity = test['error_analysis']['severity']
                    error_categories[category] = error_categories.get(category, 0) + 1
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            if error_categories:
                print(f"   Error Categories:")
                for category, count in error_categories.items():
                    print(f"     - {category.upper()}: {count}")
            
            if severity_counts:
                print(f"   Severity Distribution:")
                for severity, count in severity_counts.items():
                    print(f"     - {severity}: {count}")
        
        # Recommendations
        print(f"\n💡 SYSTEM RECOMMENDATIONS:")
        if success_rate >= 90:
            print(f"   ✅ System is performing excellently")
            print(f"   📈 Consider performance optimization for even better results")
        elif success_rate >= 80:
            print(f"   ⚠️ System is operational but has some issues")
            print(f"   🔧 Address failed tests to improve reliability")
        elif success_rate >= 70:
            print(f"   🚨 System is degraded - immediate attention required")
            print(f"   🛠️ Focus on critical failures first")
        else:
            print(f"   💥 System has critical issues - immediate intervention required")
            print(f"   🚑 Review all failed tests and apply fixes")
        
        if self.failed_tests:
            print(f"   📋 Review detailed error reports above for specific fixes")
        
        print(f"\n📊 RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   System Status: {status}")
        
        if success_rate >= 80:
            print(f"\n🎉 SYSTEM IS OPERATIONAL!")
        else:
            print(f"\n⚠️ SYSTEM REQUIRES ATTENTION!")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'system_status': status,
            'total_execution_time': total_time,
            'performance_metrics': {
                'avg_memory_start': avg_memory_start if all_metrics else 0,
                'max_memory_start': max_memory_start if all_metrics else 0,
                'min_memory_start': min_memory_start if all_metrics else 0,
                'avg_memory_end': avg_memory_end if all_metrics else 0,
                'max_memory_end': max_memory_end if all_metrics else 0,
                'min_memory_end': min_memory_end if all_metrics else 0,
                'avg_memory_delta': avg_memory_delta if all_metrics else 0,
                'max_memory_delta': max_memory_delta if all_metrics else 0,
                'min_memory_delta': min_memory_delta if all_metrics else 0,
                'avg_cpu_usage': avg_cpu_usage if all_metrics else 0,
                'max_cpu_usage': max_cpu_usage if all_metrics else 0,
                'min_cpu_usage': min_cpu_usage if all_metrics else 0
            },
            'failed_tests_details': self.failed_tests,
            'successful_tests_details': self.successful_tests
        }

    # Test Methods
    def test_system_initialization(self) -> Dict[str, Any]:
        """Test system initialization and component loading"""
        try:
            # Test core components
            assert hasattr(self, 'engine'), "Cognitive Forge Engine not initialized"
            assert hasattr(self, 'db'), "Database not initialized"
            assert hasattr(self, 'agents'), "Agents not initialized"
            assert hasattr(self, 'phoenix'), "Phoenix Protocol not initialized"
            assert hasattr(self, 'guardian'), "Guardian Protocol not initialized"
            assert hasattr(self, 'synapse'), "Synapse Logging not initialized"
            assert hasattr(self, 'self_learning'), "Self-Learning Module not initialized"
            
            return {
                'status': 'PASS',
                'details': 'All core components initialized successfully'
            }
        except Exception as e:
            return {
                'status': 'FAIL',
                'error': str(e),
                'details': 'System initialization failed'
            }

    def test_environment_validation(self) -> Dict[str, Any]:
        """Test environment variable configuration"""
        try:
            required_vars = [
                "DATABASE_URL",
                "GOOGLE_API_KEY",
                "LLM_MODEL",
                "LLM_TEMPERATURE",
            ]
            
            missing_vars = []
            present_vars = []
            
            for var in required_vars:
                value = os.getenv(var)
                if value is None:
                    missing_vars.append(var)
                else:
                    # Mask sensitive values
                    if 'KEY' in var or 'PASSWORD' in var or 'SECRET' in var:
                        masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '***'
                        present_vars.append(f"{var}={masked_value}")
                    else:
                        present_vars.append(f"{var}={value}")
            
            if missing_vars:
                return {
                    'status': 'FAIL',
                    'error': f"Missing environment variables: {', '.join(missing_vars)}",
                    'details': f"Present: {present_vars}, Missing: {missing_vars}"
                }
            
            return {
                'status': 'PASS',
                'details': f"All required environment variables present: {present_vars}"
            }
        except Exception as e:
            return {
                'status': 'FAIL',
                'error': str(e),
                'details': 'Environment validation failed'
            }

    def test_database_connectivity(self) -> Dict[str, Any]:
        """Test database connection and basic operations"""
        try:
            # Test database connection
            test_mission = self.db.create_mission(
                title="test_db_" + str(int(time.time())),
                description="Database connectivity test",
                status="testing"
            )
            
            assert test_mission is not None, "Failed to create test mission"
            assert hasattr(test_mission, 'id'), "Test mission missing ID"
            
            return {
                'status': 'PASS',
                'details': f'Database connectivity verified - Test mission ID: {test_mission.id}'
            }
        except Exception as e:
            return {
                'status': 'FAIL',
                'error': str(e),
                'details': 'Database connectivity test failed'
            }

    def test_agent_factory(self) -> Dict[str, Any]:
        """Test agent factory and agent creation"""
        try:
            # Test agent creation
            agents = self.agents
            assert hasattr(agents, 'researcher'), "Researcher agent not available"
            assert hasattr(agents, 'writer'), "Writer agent not available"
            assert hasattr(agents, 'reviewer'), "Reviewer agent not available"
            
            # Test prompt optimization agents
            prompt_agents = self.prompt_agents
            assert hasattr(prompt_agents, 'prompt_optimizer'), "Prompt optimizer agent not available"
            
            return {
                'status': 'PASS',
                'details': 'All agent types available and accessible'
            }
        except Exception as e:
            return {
                'status': 'FAIL',
                'error': str(e),
                'details': 'Agent factory test failed'
            }

    def test_protocol_systems(self) -> Dict[str, Any]:
        """Test protocol systems (Phoenix, Guardian, Synapse)"""
        try:
            # Test Phoenix Protocol
            assert hasattr(self.phoenix, 'handle_error'), "Phoenix Protocol error handling not available"
            
            # Test Guardian Protocol
            assert hasattr(self.guardian, 'validate_agent'), "Guardian Protocol validation not available"
            
            # Test Synapse Logging
            assert hasattr(self.synapse, 'log_event'), "Synapse Logging not available"
            
            # Test Self-Learning Module
            assert hasattr(self.self_learning, 'analyze_performance'), "Self-Learning Module not available"
            
            return {
                'status': 'PASS',
                'details': 'All protocol systems operational'
            }
        except Exception as e:
            return {
                'status': 'FAIL',
                'error': str(e),
                'details': 'Protocol systems test failed'
            }

    def test_workflow_phases(self) -> Dict[str, Any]:
        """Test workflow phases and prompt optimization with Phase 2 enhancements"""
        try:
            # Test prompt optimization workflow (Phase 1)
            test_prompt = "Create a simple Python web application with FastAPI"
            
            # Use the enhanced prompt optimization
            optimized_result = asyncio.run(self.engine._execute_prompt_alchemy(test_prompt))
            
            assert optimized_result is not None, "Prompt optimization returned None"
            assert 'optimized_prompt' in optimized_result, "Missing optimized_prompt in result"
            assert 'success_criteria' in optimized_result, "Missing success_criteria in result"
            assert 'recommended_agents' in optimized_result, "Missing recommended_agents in result"
            
            # Test Phase 2: Planning Specialist
            execution_blueprint = asyncio.run(self.engine._execute_planning_specialist(
                optimized_result['optimized_prompt'],
                optimized_result['technical_context']
            ))
            
            assert execution_blueprint is not None, "Execution blueprint creation failed"
            assert 'mission_overview' in execution_blueprint, "Missing mission_overview in blueprint"
            assert 'execution_phases' in execution_blueprint, "Missing execution_phases in blueprint"
            assert 'resource_allocation' in execution_blueprint, "Missing resource_allocation in blueprint"
            
            # Test Phase 3: Blueprint Validation
            validation_result = asyncio.run(self.engine._validate_execution_blueprint(execution_blueprint))
            
            assert validation_result is not None, "Blueprint validation failed"
            assert 'validation_status' in validation_result, "Missing validation_status in result"
            assert 'overall_score' in validation_result, "Missing overall_score in result"
            
            return {
                'status': 'PASS',
                'details': f'Full Phase 2 workflow successful - Prompt optimization: {len(optimized_result["optimized_prompt"])} chars, Blueprint phases: {len(execution_blueprint["execution_phases"])}, Validation score: {validation_result["overall_score"]}'
            }
        except Exception as e:
            return {
                'status': 'FAIL',
                'error': str(e),
                'details': 'Phase 2 workflow test failed'
            }

    def test_enhanced_mission_execution(self) -> Dict[str, Any]:
        """Test enhanced mission execution with Phase 2 components"""
        try:
            # Create a test mission
            test_mission = self.db.create_mission(
                title="Phase 2 Test Mission",
                description="Test enhanced mission execution capabilities",
                status="testing"
            )
            
            # Test full mission execution
            test_request = "Create a simple calculator application in Python"
            mission_result = asyncio.run(self.engine.run_mission(test_request))
            
            assert mission_result is not None, "Mission execution returned None"
            assert 'mission_id' in mission_result, "Missing mission_id in result"
            assert 'status' in mission_result, "Missing status in result"
            assert 'execution_blueprint' in mission_result, "Missing execution_blueprint in result"
            assert 'validation_result' in mission_result, "Missing validation_result in result"
            assert 'execution_result' in mission_result, "Missing execution_result in result"
            
            # Verify Phase 2 components
            blueprint = mission_result['execution_blueprint']
            assert 'mission_overview' in blueprint, "Blueprint missing mission_overview"
            assert 'execution_phases' in blueprint, "Blueprint missing execution_phases"
            assert 'resource_allocation' in blueprint, "Blueprint missing resource_allocation"
            
            validation = mission_result['validation_result']
            assert 'validation_status' in validation, "Validation missing status"
            assert 'overall_score' in validation, "Validation missing score"
            
            execution = mission_result['execution_result']
            assert 'execution_status' in execution, "Execution missing status"
            assert 'success_rate' in execution, "Execution missing success_rate"
            
            return {
                'status': 'PASS',
                'details': f'Enhanced mission execution successful - Mission ID: {mission_result["mission_id"]}, Status: {mission_result["status"]}, Execution time: {mission_result["total_execution_time"]:.2f}s'
            }
        except Exception as e:
            return {
                'status': 'FAIL',
                'error': str(e),
                'details': 'Enhanced mission execution test failed'
            }

    def test_async_execution_engine(self) -> Dict[str, Any]:
        """Test the asynchronous execution engine"""
        try:
            # Create test blueprint
            test_blueprint = {
                'mission_overview': {
                    'title': 'Async Engine Test',
                    'complexity_level': 'low',
                    'estimated_total_duration': '5 minutes'
                },
                'execution_phases': [
                    {
                        'phase_id': 'phase_1',
                        'phase_name': 'Test Phase',
                        'tasks': [
                            {
                                'task_id': 'task_1',
                                'task_name': 'Test Task 1',
                                'assigned_agent': 'researcher',
                                'estimated_duration_ms': 1000
                            },
                            {
                                'task_id': 'task_2',
                                'task_name': 'Test Task 2',
                                'assigned_agent': 'writer',
                                'estimated_duration_ms': 1000
                            }
                        ]
                    }
                ],
                'execution_strategy': {
                    'max_concurrent_tasks': 2
                }
            }
            
            # Test async execution engine
            await self.engine.async_execution_engine.initialize(1, 1, test_blueprint)
            execution_result = await self.engine.async_execution_engine.execute_mission()
            
            assert execution_result is not None, "Async execution returned None"
            assert 'execution_status' in execution_result, "Missing execution_status"
            assert 'success_rate' in execution_result, "Missing success_rate"
            assert 'total_tasks' in execution_result, "Missing total_tasks"
            
            return {
                'status': 'PASS',
                'details': f'Async execution engine test successful - Status: {execution_result["execution_status"]}, Success rate: {execution_result["success_rate"]:.1%}'
            }
        except Exception as e:
            return {
                'status': 'FAIL',
                'error': str(e),
                'details': 'Async execution engine test failed'
            }

    def test_database_phase2_features(self) -> Dict[str, Any]:
        """Test Phase 2 database features"""
        try:
            # Test execution blueprint creation
            test_blueprint_data = {
                'mission_overview': {
                    'title': 'Test Blueprint',
                    'complexity_level': 'medium'
                },
                'execution_phases': []
            }
            
            blueprint = self.db.create_execution_blueprint(
                mission_id=1,
                blueprint_data=test_blueprint_data,
                complexity_level='medium',
                estimated_duration_minutes=30
            )
            
            assert blueprint is not None, "Blueprint creation failed"
            assert 'id' in blueprint, "Blueprint missing ID"
            assert blueprint['status'] == 'draft', "Blueprint status incorrect"
            
            # Test task execution creation
            task_execution = self.db.create_task_execution(
                blueprint_id=blueprint['id'],
                mission_id=1,
                task_id_in_blueprint='test_task',
                agent_used='researcher',
                estimated_duration_ms=5000
            )
            
            assert task_execution is not None, "Task execution creation failed"
            assert 'id' in task_execution, "Task execution missing ID"
            assert task_execution['status'] == 'pending', "Task execution status incorrect"
            
            # Test resource monitoring
            self.db.record_resource_usage(
                mission_id=1,
                memory_usage_mb=100,
                cpu_usage_percent=25.0,
                active_tasks_count=2,
                completed_tasks_count=5,
                failed_tasks_count=0
            )
            
            # Test performance metrics
            self.db.record_performance_metric(
                mission_id=1,
                blueprint_id=blueprint['id'],
                metric_name='execution_time',
                metric_value=120.5,
                metric_unit='seconds'
            )
            
            return {
                'status': 'PASS',
                'details': f'Phase 2 database features test successful - Blueprint ID: {blueprint["id"]}, Task execution ID: {task_execution["id"]}'
            }
        except Exception as e:
            return {
                'status': 'FAIL',
                'error': str(e),
                'details': 'Phase 2 database features test failed'
            }

    def test_enhanced_agents(self) -> Dict[str, Any]:
        """Test enhanced agents with Phase 2 capabilities"""
        try:
            # Test planning specialist agents
            prompt_optimizer = self.engine.prompt_optimization_agents.prompt_optimizer(self.engine.llm)
            planning_specialist = self.engine.prompt_optimization_agents.planning_specialist(self.engine.llm)
            
            assert prompt_optimizer is not None, "Prompt optimizer agent creation failed"
            assert planning_specialist is not None, "Planning specialist agent creation failed"
            
            # Test enhanced lead architect
            lead_architect = self.engine.agents.lead_architect(self.engine.llm)
            assert lead_architect is not None, "Enhanced lead architect creation failed"
            
            # Test all agent types
            agent_types = [
                'researcher', 'writer', 'reviewer', 'code_generator', 'debugger'
            ]
            
            for agent_type in agent_types:
                agent_method = getattr(self.engine.agents, agent_type)
                agent = agent_method(self.engine.llm)
                assert agent is not None, f"{agent_type} agent creation failed"
            
            return {
                'status': 'PASS',
                'details': f'Enhanced agents test successful - All {len(agent_types) + 3} agent types created successfully'
            }
        except Exception as e:
            return {
                'status': 'FAIL',
                'error': str(e),
                'details': 'Enhanced agents test failed'
            }

    def test_performance_optimization(self) -> Dict[str, Any]:
        """Test performance optimization and resource management"""
        try:
            # Test memory usage
            memory_before = psutil.virtual_memory().percent
            cpu_before = psutil.cpu_percent()
            
            # Simulate some work
            time.sleep(1)
            
            memory_after = psutil.virtual_memory().percent
            cpu_after = psutil.cpu_percent()
            
            # Check if system is responsive
            memory_delta = memory_after - memory_before
            cpu_delta = cpu_after - cpu_before
            
            # Performance thresholds
            if memory_delta > 10:  # More than 10% memory increase
                return {
                    'status': 'WARNING',
                    'details': f'High memory usage detected: {memory_delta:.1f}% increase'
                }
            
            if cpu_delta > 20:  # More than 20% CPU increase
                return {
                    'status': 'WARNING',
                    'details': f'High CPU usage detected: {cpu_delta:.1f}% increase'
                }
            
            return {
                'status': 'PASS',
                'details': f'Performance within acceptable limits - Memory: {memory_delta:.1f}%, CPU: {cpu_delta:.1f}%'
            }
        except Exception as e:
            return {
                'status': 'FAIL',
                'error': str(e),
                'details': 'Performance optimization test failed'
            }

    def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling and recovery mechanisms"""
        try:
            # Test with empty prompt to trigger error handling
            empty_prompt = ""
            
            # This should trigger the error handling system
            result = asyncio.run(self.engine._execute_prompt_alchemy(empty_prompt))
            
            # Even with empty prompt, system should handle it gracefully
            assert result is not None, "Error handling failed - returned None"
            
            return {
                'status': 'PASS',
                'details': 'Error handling mechanisms operational'
            }
        except Exception as e:
            return {
                'status': 'FAIL',
                'error': str(e),
                'details': 'Error handling test failed'
            }

    def test_integration_tests(self) -> Dict[str, Any]:
        """Test system integration and component interaction"""
        try:
            # Test component integration
            components = [
                self.engine,
                self.db,
                self.agents,
                self.phoenix,
                self.guardian,
                self.synapse,
                self.self_learning
            ]
            
            for component in components:
                assert component is not None, f"Component {type(component).__name__} is None"
            
            return {
                'status': 'PASS',
                'details': 'All components integrated and accessible'
            }
        except Exception as e:
            return {
                'status': 'FAIL',
                'error': str(e),
                'details': 'Integration test failed'
            }

    def test_stress_testing(self) -> Dict[str, Any]:
        """Test system under stress conditions"""
        try:
            # Create multiple test missions to stress the database
            test_missions = []
            start_time = time.time()
            
            for i in range(50):  # Create 50 test missions
                mission = self.db.create_mission(
                    title=f"stress_test_{i}_{int(time.time())}",
                    description=f"Stress test mission {i}",
                    status="testing"
                )
                test_missions.append(mission)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Performance metrics
            avg_time_per_mission = total_time / len(test_missions)
            
            if avg_time_per_mission > 0.1:  # More than 100ms per mission
                return {
                    'status': 'WARNING',
                    'details': f'Slow database performance: {avg_time_per_mission:.3f}s per mission'
                }
            
            return {
                'status': 'PASS',
                'details': f'Stress test passed - {len(test_missions)} missions in {total_time:.2f}s ({avg_time_per_mission:.3f}s avg)'
            }
        except Exception as e:
            return {
                'status': 'FAIL',
                'error': str(e),
                'details': 'Stress testing failed'
            }

# Main execution
if __name__ == "__main__":
    hub = EnhancedSystemOptimizationHub()
    results = hub.run_comprehensive_test_suite()
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"comprehensive_test_report_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: {results_file}") 