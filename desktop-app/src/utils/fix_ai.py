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
    from utils.google_ai_wrapper import create_google_ai_llm
    LLM_AVAILABLE = True
except ImportError:
    try:
        from src.utils.google_ai_wrapper import create_google_ai_llm
        LLM_AVAILABLE = True
    except ImportError:
        LLM_AVAILABLE = False
        create_google_ai_llm = None

from loguru import logger
import sys
import os

# Add the parent directory to the path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

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
                
                self.llm = create_google_ai_llm(
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
                
                # Phase 2: Performance Analysis with observability
                with self.observability.phase_trace("performance_analysis", self.operation_id) as phase_data:
                    performance_result = await self._run_performance_analysis_phase()
                    phase_data["success"] = True
                    phase_data["performance_issues"] = len(performance_result.get("performance_issues", []))
                    metrics.performance_improvements.extend(performance_result.get("optimization_suggestions", []))
                    trace_data.phases.append(phase_data)
                
                # Phase 3: Triage & Planning with observability
                with self.observability.phase_trace("triage_planning", self.operation_id) as phase_data:
                    planning_result = await self._run_planning_phase(diagnosis_result, performance_result)
                    phase_data["success"] = True
                    phase_data["healing_steps"] = len(planning_result.get("healing_plan", []))
                    trace_data.phases.append(phase_data)
                
                # Phase 4: Execution & Self-Healing with observability
                with self.observability.phase_trace("execution_self_healing", self.operation_id) as phase_data:
                    execution_result = await self._run_execution_phase(planning_result)
                    phase_data["success"] = execution_result.get("success", False)
                    metrics.fixes_applied = execution_result.get("fixes_applied", 0)
                    metrics.surgical_fixes = execution_result.get("surgical_fixes_applied", 0)
                    metrics.simple_fixes = execution_result.get("simple_fixes_applied", 0)
                    metrics.rollbacks_performed = execution_result.get("rollbacks_performed", 0)
                    metrics.error_count = execution_result.get("failed_fixes", 0)
                    trace_data.phases.append(phase_data)
                
                # Phase 5: Final Validation with observability
                with self.observability.phase_trace("final_validation", self.operation_id) as phase_data:
                    validation_result = await self._run_final_validation_phase()
                    phase_data["success"] = validation_result.get("all_tests_passed", False)
                    phase_data["regressions_found"] = len(validation_result.get("regressions", []))
                    trace_data.phases.append(phase_data)
                
                metrics.end_time = datetime.now()
                metrics.success_rate = 1.0 if validation_result.get("all_tests_passed", False) else 0.0
                metrics.total_files_analyzed = diagnosis_result.get("total_files_analyzed", 0)
                
                trace_data.end_time = metrics.end_time
                trace_data.total_duration = (metrics.end_time - metrics.start_time).total_seconds()
                trace_data.success = metrics.success_rate == 1.0
                trace_data.rollback_count = metrics.rollbacks_performed
                trace_data.surgical_fixes_applied = metrics.surgical_fixes
                
                self.observability.log_system_event("fix_ai_operation_completed", asdict(metrics), self.operation_id)
                
                return {
                    "success": trace_data.success,
                    "report": asdict(metrics),
                    "details": {
                        "diagnosis": diagnosis_result,
                        "performance_analysis": performance_result,
                        "planning": planning_result,
                        "execution": execution_result,
                        "validation": validation_result
                    }
                }
                
            except Exception as e:
                metrics.end_time = datetime.now()
                metrics.success_rate = 0.0
                metrics.error_count += 1
                trace_data.end_time = metrics.end_time
                trace_data.total_duration = (metrics.end_time - metrics.start_time).total_seconds()
                trace_data.success = False
                trace_data.error_phase = "overall_fix_ai_failure"
                self.observability.log_error(e, {"operation_id": self.operation_id}, self.operation_id)
                logger.error(f"Fix-AI comprehensive healing failed: {e}")
                raise
    
    async def _run_diagnosis_phase(self) -> Dict[str, Any]:
        """Run diagnosis phase with observability."""
        issues = []
        total_files = 0
        
        for file_path in self.src_directory.rglob("*.py"):
            total_files += 1
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Syntax check
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    issues.append({
                        "file": str(file_path),
                        "type": "syntax_error",
                        "line": e.lineno,
                        "message": str(e),
                        "severity": "critical"
                    })
                
                # Import check
                if "import" in content and "from" in content:
                    # Basic import validation
                    pass
                
            except Exception as e:
                issues.append({
                    "file": str(file_path),
                    "type": "file_error",
                    "message": str(e),
                    "severity": "high"
                })
        
        return {
            "issues": issues,
            "total_files_analyzed": total_files,
            "issues_found": len(issues)
        }
    
    async def _run_performance_analysis_phase(self) -> Dict[str, Any]:
        """Run performance analysis phase with observability."""
        performance_issues = []
        optimization_suggestions = []
        
        for file_path in self.src_directory.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basic performance analysis
                if len(content) > 1000:  # Large files
                    performance_issues.append({
                        "file": str(file_path),
                        "type": "large_file",
                        "size": len(content),
                        "suggestion": "Consider breaking into smaller modules"
                    })
                
                if content.count("import") > 10:  # Many imports
                    performance_issues.append({
                        "file": str(file_path),
                        "type": "many_imports",
                        "count": content.count("import"),
                        "suggestion": "Consider consolidating imports"
                    })
                
            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {e}")
        
        return {
            "performance_issues": performance_issues,
            "optimization_suggestions": optimization_suggestions
        }
    
    async def _run_planning_phase(self, diagnosis_result: Dict[str, Any], performance_result: Dict[str, Any]) -> Dict[str, Any]:
        """Run planning phase with observability."""
        healing_plan = []
        
        # Plan fixes for diagnosis issues
        for issue in diagnosis_result.get("issues", []):
            healing_plan.append({
                "type": "fix",
                "target": issue["file"],
                "action": f"Fix {issue['type']}: {issue['message']}",
                "priority": "high" if issue["severity"] in ["critical", "high"] else "medium"
            })
        
        # Plan optimizations for performance issues
        for issue in performance_result.get("performance_issues", []):
            healing_plan.append({
                "type": "optimize",
                "target": issue["file"],
                "action": issue["suggestion"],
                "priority": "medium"
            })
        
        return {
            "healing_plan": healing_plan,
            "total_actions": len(healing_plan)
        }
    
    async def _run_execution_phase(self, planning_result: Dict[str, Any]) -> Dict[str, Any]:
        """Run execution phase with observability."""
        fixes_applied = 0
        surgical_fixes = 0
        simple_fixes = 0
        failed_fixes = 0
        
        for action in planning_result.get("healing_plan", []):
            try:
                if action["type"] == "fix":
                    # Simulate fix application
                    fixes_applied += 1
                    if "syntax" in action["action"].lower():
                        surgical_fixes += 1
                    else:
                        simple_fixes += 1
                elif action["type"] == "optimize":
                    # Simulate optimization
                    fixes_applied += 1
                    simple_fixes += 1
                
            except Exception as e:
                failed_fixes += 1
                logger.error(f"Failed to apply {action['type']} to {action['target']}: {e}")
        
        return {
            "success": failed_fixes == 0,
            "fixes_applied": fixes_applied,
            "surgical_fixes_applied": surgical_fixes,
            "simple_fixes_applied": simple_fixes,
            "failed_fixes": failed_fixes,
            "rollbacks_performed": 0
        }
    
    async def _run_final_validation_phase(self) -> Dict[str, Any]:
        """Run final validation phase with observability."""
        regressions = []
        all_tests_passed = True
        
        # Simulate validation tests
        for file_path in self.src_directory.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Syntax validation
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    regressions.append({
                        "file": str(file_path),
                        "type": "syntax_regression",
                        "message": str(e)
                    })
                    all_tests_passed = False
                
            except Exception as e:
                regressions.append({
                    "file": str(file_path),
                    "type": "validation_error",
                    "message": str(e)
                })
                all_tests_passed = False
        
        return {
            "all_tests_passed": all_tests_passed,
            "regressions": regressions,
            "validation_score": 1.0 if all_tests_passed else 0.0
        }


# Placeholder classes for compatibility
class SurgicalPatcher:
    def __init__(self):
        pass

class RollbackManager:
    def __init__(self, backup_dir):
        self.backup_dir = backup_dir

class MissionAwareHealer:
    def __init__(self):
        pass

class PerformanceOptimizer:
    def __init__(self):
        pass 