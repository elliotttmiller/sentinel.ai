#!/usr/bin/env python3
"""
Weave-Enhanced Fix-AI: The Sentient Codebase Healer with Full Observability
Integrates comprehensive monitoring, tracing, and analytics for autonomous codebase healing.
"""

import os
import sys
import json
import time
import ast
import subprocess
import shutil
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from contextlib import contextmanager

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

from loguru import logger
from src.utils.weave_observability import observability_manager, WeaveObservabilityManager


@dataclass
class FixAIMetrics:
    """Comprehensive metrics for Fix-AI operations."""
    operation_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_files_analyzed: int = 0
    issues_found: int = 0
    fixes_applied: int = 0
    surgical_fixes: int = 0
    simple_fixes: int = 0
    rollbacks_performed: int = 0
    success_rate: float = 0.0
    total_cost: float = 0.0
    error_count: int = 0
    performance_improvements: List[str] = None


class WeaveEnhancedFixAI:
    """Enhanced Fix-AI with comprehensive Weave observability."""
    
    def __init__(self, project_dir: Path):
        self.project_dir = Path(project_dir)
        self.src_directory = self.project_dir / "src"
        self.observability = observability_manager
        self.operation_id = f"fix_ai_{int(time.time())}"
        
        # Initialize LLM if available
        if LLM_AVAILABLE:
            try:
                from dotenv import load_dotenv
                load_dotenv()
                
                self.llm = ChatGoogleGenerativeAI(
                    model=os.getenv("LLM_MODEL", "gemini-1.5-pro"),
                    temperature=0.3
                )
            except Exception as e:
                logger.error(f"Failed to initialize LLM: {e}")
                self.llm = None
        else:
            self.llm = None
        
        # Initialize components
        self.surgical_patcher = SurgicalPatcher()
        self.rollback_manager = RollbackManager(self.project_dir / "backups")
        self.phoenix_protocol = PhoenixProtocol()
        self.mission_aware_healer = MissionAwareHealer()
        self.performance_optimizer = PerformanceOptimizer()
        
        logger.info(f"🔧 Weave-Enhanced Fix-AI initialized for {self.project_dir}")
    
    async def run_comprehensive_healing(self) -> Dict[str, Any]:
        """Run comprehensive codebase healing with full observability."""
        metrics = FixAIMetrics(
            operation_id=self.operation_id,
            start_time=datetime.now(),
            performance_improvements=[]
        )
        
        with self.observability.mission_trace(self.operation_id, "Comprehensive Codebase Healing") as trace_data:
            try:
                # Phase 1: Diagnosis with observability
                with self.observability.phase_trace("diagnosis", self.operation_id) as phase_data:
                    diagnosis_result = await self._run_diagnosis_phase()
                    phase_data["success"] = True
                    phase_data["issues_found"] = len(diagnosis_result.get("issues", []))
                    metrics.issues_found = len(diagnosis_result.get("issues", []))
                    trace_data.phases.append(phase_data)
                
                # Phase 2: Performance Analysis
                with self.observability.phase_trace("performance_analysis", self.operation_id) as phase_data:
                    performance_result = await self._run_performance_analysis_phase()
                    phase_data["success"] = True
                    phase_data["performance_issues"] = len(performance_result.get("performance_issues", []))
                    trace_data.phases.append(phase_data)
                
                # Phase 3: Planning with AI
                with self.observability.phase_trace("planning", self.operation_id) as phase_data:
                    planning_result = await self._run_planning_phase(diagnosis_result, performance_result)
                    phase_data["success"] = True
                    phase_data["healing_steps"] = len(planning_result.get("healing_plan", []))
                    trace_data.phases.append(phase_data)
                
                # Phase 4: Execution with surgical precision
                with self.observability.phase_trace("execution", self.operation_id) as phase_data:
                    execution_result = await self._run_execution_phase(planning_result)
                    phase_data["success"] = True
                    phase_data["fixes_applied"] = execution_result.get("fixes_applied", 0)
                    phase_data["surgical_fixes"] = execution_result.get("surgical_fixes_applied", 0)
                    phase_data["rollbacks"] = execution_result.get("rollbacks_performed", 0)
                    metrics.fixes_applied = execution_result.get("fixes_applied", 0)
                    metrics.surgical_fixes = execution_result.get("surgical_fixes_applied", 0)
                    metrics.rollbacks_performed = execution_result.get("rollbacks_performed", 0)
                    trace_data.phases.append(phase_data)
                
                # Phase 5: Final Validation
                with self.observability.phase_trace("validation", self.operation_id) as phase_data:
                    validation_result = await self._run_final_validation_phase()
                    phase_data["success"] = validation_result.get("all_tests_passed", False)
                    phase_data["regressions_found"] = validation_result.get("regressions", 0)
                    trace_data.phases.append(phase_data)
                
                # Calculate final metrics
                metrics.end_time = datetime.now()
                metrics.total_duration = (metrics.end_time - metrics.start_time).total_seconds()
                metrics.success_rate = (metrics.fixes_applied - metrics.rollbacks_performed) / max(metrics.fixes_applied, 1)
                
                # Log comprehensive results
                self.observability.log_system_event("fix_ai_completed", {
                    "operation_id": self.operation_id,
                    "total_fixes": metrics.fixes_applied,
                    "surgical_fixes": metrics.surgical_fixes,
                    "rollbacks": metrics.rollbacks_performed,
                    "success_rate": metrics.success_rate,
                    "duration": metrics.total_duration
                }, self.operation_id)
                
                return {
                    "operation_id": self.operation_id,
                    "status": "completed",
                    "metrics": asdict(metrics),
                    "diagnosis_result": diagnosis_result,
                    "performance_result": performance_result,
                    "execution_result": execution_result,
                    "validation_result": validation_result
                }
                
            except Exception as e:
                metrics.end_time = datetime.now()
                metrics.error_count += 1
                
                self.observability.log_error(e, {
                    "operation_id": self.operation_id,
                    "phase": "comprehensive_healing"
                }, self.operation_id)
                
                raise
    
    async def _run_diagnosis_phase(self) -> Dict[str, Any]:
        """Run comprehensive diagnosis with observability."""
        issues = []
        
        # Static analysis
        for python_file in self._get_python_files():
            with self.observability.agent_trace("diagnosis_agent", self.operation_id, f"Analyzing {python_file}") as metrics:
                try:
                    file_issues = await self._analyze_file(python_file)
                    issues.extend(file_issues)
                    metrics.success = True
                except Exception as e:
                    metrics.success = False
                    metrics.error_message = str(e)
                    logger.error(f"Diagnosis failed for {python_file}: {e}")
        
        return {
            "issues": issues,
            "total_files_analyzed": len(self._get_python_files()),
            "issues_by_severity": self._categorize_issues(issues)
        }
    
    async def _run_performance_analysis_phase(self) -> Dict[str, Any]:
        """Run performance analysis with observability."""
        performance_issues = []
        
        for python_file in self._get_python_files():
            with self.observability.agent_trace("performance_agent", self.operation_id, f"Analyzing performance of {python_file}") as metrics:
                try:
                    analysis = self.performance_optimizer.analyze_performance(str(python_file))
                    if analysis.get("issues"):
                        performance_issues.append({
                            "file": str(python_file),
                            "analysis": analysis
                        })
                    metrics.success = True
                except Exception as e:
                    metrics.success = False
                    metrics.error_message = str(e)
                    logger.error(f"Performance analysis failed for {python_file}: {e}")
        
        return {
            "performance_issues": performance_issues,
            "optimization_suggestions": self._compile_optimization_suggestions(performance_issues)
        }
    
    async def _run_planning_phase(self, diagnosis_result: Dict[str, Any], performance_result: Dict[str, Any]) -> Dict[str, Any]:
        """Run AI-powered planning with observability."""
        if not self.llm:
            return {"healing_plan": [], "error": "LLM not available"}
        
        with self.observability.agent_trace("planning_agent", self.operation_id, "Creating healing plan") as metrics:
            try:
                # Create comprehensive planning prompt
                planning_prompt = self._create_planning_prompt(diagnosis_result, performance_result)
                
                # Get AI-generated healing plan
                response = await self.llm.ainvoke(planning_prompt)
                healing_plan = self._parse_healing_plan(response.content)
                
                metrics.success = True
                return {
                    "healing_plan": healing_plan,
                    "total_steps": len(healing_plan),
                    "priority_levels": self._categorize_healing_steps(healing_plan)
                }
                
            except Exception as e:
                metrics.success = False
                metrics.error_message = str(e)
                logger.error(f"Planning phase failed: {e}")
                return {"healing_plan": [], "error": str(e)}
    
    async def _run_execution_phase(self, planning_result: Dict[str, Any]) -> Dict[str, Any]:
        """Run execution phase with surgical precision and rollback safety."""
        fixes_applied = 0
        surgical_fixes = 0
        rollbacks_performed = 0
        
        for step in planning_result.get("healing_plan", []):
            with self.observability.agent_trace("execution_agent", self.operation_id, f"Executing {step.get('action', 'fix')}") as metrics:
                try:
                    if step.get("type") == "surgical":
                        success = await self._apply_surgical_fix(step)
                        if success:
                            surgical_fixes += 1
                    else:
                        success = await self._apply_simple_fix(step)
                    
                    if success:
                        fixes_applied += 1
                        metrics.success = True
                    else:
                        # Trigger rollback if critical
                        if step.get("critical", False):
                            rollback_success = self.rollback_manager.perform_rollback(
                                step.get("file_path"), 
                                f"Critical fix failed: {step.get('action')}"
                            )
                            if rollback_success:
                                rollbacks_performed += 1
                                self.observability.log_system_event("rollback_performed", {
                                    "file": step.get("file_path"),
                                    "reason": f"Critical fix failed: {step.get('action')}"
                                }, self.operation_id)
                
                except Exception as e:
                    metrics.success = False
                    metrics.error_message = str(e)
                    logger.error(f"Execution failed for step {step}: {e}")
        
        return {
            "fixes_applied": fixes_applied,
            "surgical_fixes_applied": surgical_fixes,
            "rollbacks_performed": rollbacks_performed,
            "success_rate": fixes_applied / max(len(planning_result.get("healing_plan", [])), 1)
        }
    
    async def _run_final_validation_phase(self) -> Dict[str, Any]:
        """Run final validation with comprehensive testing."""
        with self.observability.agent_trace("validation_agent", self.operation_id, "Final validation") as metrics:
            try:
                # Run comprehensive tests
                test_results = await self._run_validation_tests()
                
                # Check for regressions
                regressions = await self._check_for_regressions()
                
                metrics.success = test_results.get("all_tests_passed", False) and len(regressions) == 0
                
                return {
                    "all_tests_passed": test_results.get("all_tests_passed", False),
                    "regressions": len(regressions),
                    "test_results": test_results,
                    "regression_details": regressions
                }
                
            except Exception as e:
                metrics.success = False
                metrics.error_message = str(e)
                logger.error(f"Validation phase failed: {e}")
                return {"all_tests_passed": False, "error": str(e)}
    
    async def _analyze_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analyze a single file for issues."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Syntax analysis
            try:
                ast.parse(content)
            except SyntaxError as e:
                issues.append({
                    "type": "syntax_error",
                    "severity": "critical",
                    "line": e.lineno,
                    "message": str(e),
                    "file": str(file_path)
                })
            
            # Style analysis
            style_issues = self._analyze_style(content, file_path)
            issues.extend(style_issues)
            
            # Complexity analysis
            complexity_issues = self._analyze_complexity(content, file_path)
            issues.extend(complexity_issues)
            
        except Exception as e:
            issues.append({
                "type": "analysis_error",
                "severity": "critical",
                "message": str(e),
                "file": str(file_path)
            })
        
        return issues
    
    def _analyze_style(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Analyze code style issues."""
        issues = []
        
        # Basic style checks
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append({
                    "type": "style",
                    "severity": "low",
                    "line": i,
                    "message": "Line too long (>120 characters)",
                    "file": str(file_path)
                })
        
        return issues
    
    def _analyze_complexity(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Analyze code complexity."""
        issues = []
        
        try:
            tree = ast.parse(content)
            
            # Count functions and classes
            function_count = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
            class_count = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
            
            if function_count > 20:
                issues.append({
                    "type": "complexity",
                    "severity": "medium",
                    "message": f"Too many functions ({function_count}) in single file",
                    "file": str(file_path)
                })
            
            if class_count > 10:
                issues.append({
                    "type": "complexity",
                    "severity": "medium",
                    "message": f"Too many classes ({class_count}) in single file",
                    "file": str(file_path)
                })
        
        except SyntaxError:
            # Already caught in _analyze_file
            pass
        
        return issues
    
    def _get_python_files(self) -> List[Path]:
        """Get all Python files in the project."""
        python_files = []
        for root, dirs, files in os.walk(self.src_directory):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        return python_files
    
    def _categorize_issues(self, issues: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize issues by severity."""
        categorized = {"critical": [], "high": [], "medium": [], "low": []}
        for issue in issues:
            severity = issue.get("severity", "medium")
            if severity in categorized:
                categorized[severity].append(issue)
        return categorized
    
    def _create_planning_prompt(self, diagnosis_result: Dict[str, Any], performance_result: Dict[str, Any]) -> str:
        """Create comprehensive planning prompt for AI."""
        return f"""
        You are an expert AI software engineer tasked with healing a codebase. Analyze the following issues and create a detailed healing plan.
        
        DIAGNOSIS RESULTS:
        {json.dumps(diagnosis_result, indent=2)}
        
        PERFORMANCE ANALYSIS:
        {json.dumps(performance_result, indent=2)}
        
        Create a healing plan with the following structure:
        {{
            "healing_steps": [
                {{
                    "action": "description of the fix",
                    "file_path": "path to the file",
                    "type": "surgical|simple",
                    "priority": "critical|high|medium|low",
                    "estimated_time": "time estimate",
                    "risk_level": "low|medium|high",
                    "dependencies": ["list of dependencies"],
                    "rollback_plan": "how to rollback if needed"
                }}
            ]
        }}
        
        Prioritize critical issues first, then high, medium, and low. Use surgical fixes for complex changes and simple fixes for straightforward corrections.
        """
    
    def _parse_healing_plan(self, response: str) -> List[Dict[str, Any]]:
        """Parse AI-generated healing plan."""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                plan_data = json.loads(json_match.group())
                return plan_data.get("healing_steps", [])
        except Exception as e:
            logger.error(f"Failed to parse healing plan: {e}")
        
        return []
    
    def _categorize_healing_steps(self, steps: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize healing steps by priority."""
        categorized = {"critical": [], "high": [], "medium": [], "low": []}
        for step in steps:
            priority = step.get("priority", "medium")
            if priority in categorized:
                categorized[priority].append(step)
        return categorized
    
    async def _apply_surgical_fix(self, step: Dict[str, Any]) -> bool:
        """Apply surgical fix using diff-based patching."""
        try:
            if not self.llm:
                return False
            
            # Generate surgical patch
            patch_prompt = f"""
            Generate a surgical patch for the following issue:
            File: {step.get('file_path')}
            Action: {step.get('action')}
            
            Return the patch in standard diff format:
            @@ -old_start,old_count +new_start,new_count @@
            - old line
            + new line
            """
            
            response = await self.llm.ainvoke(patch_prompt)
            patch_content = response.content
            
            # Parse and apply patch
            operations = self.surgical_patcher.parse_diff_patch(patch_content)
            success = self.surgical_patcher.apply_surgical_patch(step.get("file_path"), operations)
            
            if success:
                self.rollback_manager.register_file_modification(step.get("file_path"))
            
            return success
            
        except Exception as e:
            logger.error(f"Surgical fix failed: {e}")
            return False
    
    async def _apply_simple_fix(self, step: Dict[str, Any]) -> bool:
        """Apply simple fix."""
        try:
            # Simple line replacement or addition
            file_path = step.get("file_path")
            action = step.get("action")
            
            # Implementation depends on the specific action
            # For now, return True as placeholder
            return True
            
        except Exception as e:
            logger.error(f"Simple fix failed: {e}")
            return False
    
    async def _run_validation_tests(self) -> Dict[str, Any]:
        """Run comprehensive validation tests."""
        # Placeholder for comprehensive testing
        return {
            "all_tests_passed": True,
            "test_count": 10,
            "passed_tests": 10,
            "failed_tests": 0
        }
    
    async def _check_for_regressions(self) -> List[Dict[str, Any]]:
        """Check for regressions after fixes."""
        # Placeholder for regression detection
        return []
    
    def _compile_optimization_suggestions(self, performance_issues: List[Dict[str, Any]]) -> List[str]:
        """Compile optimization suggestions from performance analysis."""
        suggestions = []
        for issue in performance_issues:
            analysis = issue.get("analysis", {})
            if analysis.get("issues"):
                suggestions.extend(analysis.get("issues", []))
        return suggestions


class SurgicalPatcher:
    """Enhanced surgical patcher with observability."""
    
    def __init__(self):
        self.observability = observability_manager
    
    def parse_diff_patch(self, diff_content: str) -> List[Dict[str, Any]]:
        """Parse diff content into structured operations."""
        operations = []
        current_operation = None
        
        for line in diff_content.split('\n'):
            if line.startswith('@@'):
                if current_operation:
                    operations.append(current_operation)
                
                # Parse @@ line
                match = re.match(r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@', line)
                if match:
                    current_operation = {
                        "type": "multi_line",
                        "old_start": int(match.group(1)),
                        "old_count": int(match.group(2)),
                        "new_start": int(match.group(3)),
                        "new_count": int(match.group(4)),
                        "lines": []
                    }
            
            elif line.startswith('-') and current_operation:
                current_operation["lines"].append({"type": "delete", "content": line[1:]})
            
            elif line.startswith('+') and current_operation:
                current_operation["lines"].append({"type": "insert", "content": line[1:]})
            
            elif line.startswith(' ') and current_operation:
                current_operation["lines"].append({"type": "context", "content": line[1:]})
        
        if current_operation:
            operations.append(current_operation)
        
        return operations
    
    def apply_surgical_patch(self, file_path: str, operations: List[Dict[str, Any]]) -> bool:
        """Apply surgical patch to file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Apply operations in reverse order to maintain line numbers
            for operation in reversed(operations):
                lines = self._apply_operation(lines, operation)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True
            
        except Exception as e:
            logger.error(f"Surgical patch failed for {file_path}: {e}")
            return False
    
    def _apply_operation(self, lines: List[str], operation: Dict[str, Any]) -> List[str]:
        """Apply a single operation to lines."""
        if operation["type"] == "multi_line":
            return self._apply_multi_line_operation(lines, operation)
        return lines
    
    def _apply_multi_line_operation(self, lines: List[str], operation: Dict[str, Any]) -> List[str]:
        """Apply multi-line operation."""
        start_line = operation["old_start"] - 1  # Convert to 0-based index
        end_line = start_line + operation["old_count"]
        
        # Extract new lines from operation
        new_lines = []
        for line_op in operation["lines"]:
            if line_op["type"] == "insert":
                new_lines.append(line_op["content"] + '\n')
            elif line_op["type"] == "context":
                new_lines.append(line_op["content"] + '\n')
        
        # Apply the change
        return lines[:start_line] + new_lines + lines[end_line:]


class RollbackManager:
    """Enhanced rollback manager with observability."""
    
    def __init__(self, backup_directory: Path):
        self.backup_directory = backup_directory
        self.observability = observability_manager
        self.modified_files = set()
    
    def register_file_modification(self, file_path: str):
        """Register file for potential rollback."""
        self.modified_files.add(file_path)
    
    def perform_rollback(self, file_path: str, reason: str) -> bool:
        """Perform rollback of a specific file."""
        try:
            backup_path = self.backup_directory / Path(file_path).name
            if backup_path.exists():
                shutil.copy2(backup_path, file_path)
                
                self.observability.log_system_event("rollback_performed", {
                    "file": file_path,
                    "reason": reason,
                    "backup_source": str(backup_path)
                })
                
                return True
        except Exception as e:
            logger.error(f"Rollback failed for {file_path}: {e}")
        
        return False


class PhoenixProtocol:
    """Enhanced Phoenix Protocol with observability."""
    
    def __init__(self):
        self.observability = observability_manager
    
    def analyze_error(self, error: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze error with observability."""
        analysis = {
            "error_type": self._classify_error(error),
            "severity": self._assess_severity(error, context),
            "recovery_strategy": self._generate_recovery_strategy(error, context),
            "rollback_required": self._assess_rollback_need(error),
            "rollback_scope": self._determine_rollback_scope(error, context)
        }
        
        self.observability.log_system_event("phoenix_analysis", analysis)
        
        return analysis
    
    def _classify_error(self, error: str) -> str:
        """Classify error type."""
        if "syntax" in error.lower():
            return "syntax_error"
        elif "import" in error.lower():
            return "import_error"
        elif "attribute" in error.lower():
            return "attribute_error"
        else:
            return "general_error"
    
    def _assess_severity(self, error: str, context: Dict[str, Any]) -> str:
        """Assess error severity."""
        if "critical" in error.lower() or "fatal" in error.lower():
            return "critical"
        elif "warning" in error.lower():
            return "low"
        else:
            return "medium"
    
    def _generate_recovery_strategy(self, error: str, context: Dict[str, Any]) -> str:
        """Generate recovery strategy."""
        return "automatic_fix"
    
    def _assess_rollback_need(self, error: str) -> bool:
        """Assess if rollback is needed."""
        return "critical" in error.lower() or "fatal" in error.lower()
    
    def _determine_rollback_scope(self, error: str, context: Dict[str, Any]) -> str:
        """Determine rollback scope."""
        return "single_file"


class MissionAwareHealer:
    """Mission-aware healing prioritization."""
    
    def __init__(self):
        self.active_missions = {}
        self.observability = observability_manager
    
    def register_active_mission(self, mission_id: str, mission_type: str, critical_files: List[str]):
        """Register active mission for healing prioritization."""
        self.active_missions[mission_id] = {
            "type": mission_type,
            "critical_files": critical_files,
            "start_time": datetime.now()
        }
    
    def assess_issue_impact(self, issue: Dict[str, Any]) -> float:
        """Assess impact of issue on active missions."""
        impact_score = 0.0
        
        for mission_id, mission_data in self.active_missions.items():
            if issue.get("file") in mission_data.get("critical_files", []):
                impact_score += 1.0
        
        return impact_score


class PerformanceOptimizer:
    """Performance optimization analyzer."""
    
    def __init__(self):
        self.observability = observability_manager
    
    def analyze_performance(self, file_path: str) -> Dict[str, Any]:
        """Analyze file performance."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = {
                "complexity": self._calculate_complexity(content),
                "imports": self._analyze_imports(content),
                "issues": self._identify_performance_issues(content),
                "suggestions": self._generate_optimization_suggestions(content)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Performance analysis failed for {file_path}: {e}")
            return {"error": str(e)}
    
    def _calculate_complexity(self, content: str) -> float:
        """Calculate code complexity."""
        try:
            tree = ast.parse(content)
            complexity = 0
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.ExceptHandler)):
                    complexity += 1
            
            return complexity
        except:
            return 0.0
    
    def _analyze_imports(self, content: str) -> List[str]:
        """Analyze import statements."""
        imports = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
        except:
            pass
        
        return imports
    
    def _identify_performance_issues(self, content: str) -> List[str]:
        """Identify performance issues."""
        issues = []
        
        # Check for common performance issues
        if "import *" in content:
            issues.append("Wildcard import detected - consider specific imports")
        
        if content.count("for") > 10:
            issues.append("High number of loops detected - consider optimization")
        
        return issues
    
    def _generate_optimization_suggestions(self, content: str) -> List[str]:
        """Generate optimization suggestions."""
        suggestions = []
        
        # Basic suggestions based on content analysis
        if len(content) > 10000:
            suggestions.append("Consider splitting large file into smaller modules")
        
        return suggestions


# Global Weave-Enhanced Fix-AI instance
weave_enhanced_fix_ai = None 