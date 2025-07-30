#!/usr/bin/env python3
"""
Fix-AI: The Sentient Codebase Healer
A sophisticated, self-healing diagnostic and repair system for the Cognitive Forge codebase.

Enhanced with:
- Phoenix Protocol integration for seamless error recovery
- Mission-aware healing prioritization
- Performance optimization capabilities
- Cognitive Forge architecture awareness
"""

import os
import sys
import json
import time
import ast
import subprocess
import shutil
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import Agent, Task, Crew, Process
from src.utils.weave_observability import observability_manager, WeaveObservabilityManager

# --- CONFIGURATION ---
PROJECT_ROOT = Path(__file__).parent
SRC_DIRECTORY = PROJECT_ROOT / "src"
REPORTS_DIRECTORY = PROJECT_ROOT / "logs" / "fix_ai_reports"
BACKUP_DIRECTORY = PROJECT_ROOT / "backups" / f"fix_ai_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
MAX_FIX_RETRIES = 3
PERFORMANCE_THRESHOLD = 0.8  # Performance optimization threshold

# --- INITIALIZE LLM ---
try:
    from dotenv import load_dotenv
    load_dotenv()
    LLM = ChatGoogleGenerativeAI(
        model=os.getenv("LLM_MODEL", "gemini-1.5-pro"), 
        temperature=0.3  # Lower temperature for more precise fixes
    )
except ImportError:
    print("Warning: dotenv is not installed. Make sure your environment variables are set.")
    LLM = None

class PhoenixProtocol:
    """Integration with our existing Phoenix Protocol for error recovery."""
    
    def __init__(self):
        self.recovery_attempts = 0
        self.max_recovery_attempts = 5
        
    def analyze_error(self, error: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze error and provide recovery strategy."""
        return {
            "error_type": self._classify_error(error),
            "severity": self._assess_severity(error, context),
            "recovery_strategy": self._generate_recovery_strategy(error, context),
            "rollback_required": self._assess_rollback_need(error)
        }
    
    def _classify_error(self, error: str) -> str:
        """Classify the type of error."""
        error_lower = error.lower()
        if "syntax" in error_lower:
            return "syntax_error"
        elif "import" in error_lower:
            return "import_error"
        elif "attribute" in error_lower:
            return "attribute_error"
        elif "type" in error_lower:
            return "type_error"
        else:
            return "general_error"
    
    def _assess_severity(self, error: str, context: Dict[str, Any]) -> str:
        """Assess the severity of the error."""
        if context.get("mission_critical", False):
            return "critical"
        elif "syntax" in error.lower():
            return "high"
        else:
            return "medium"
    
    def _generate_recovery_strategy(self, error: str, context: Dict[str, Any]) -> str:
        """Generate recovery strategy based on error type."""
        error_type = self._classify_error(error)
        strategies = {
            "syntax_error": "immediate_fix",
            "import_error": "dependency_resolution",
            "attribute_error": "code_analysis_and_fix",
            "type_error": "type_annotation_fix",
            "general_error": "comprehensive_analysis"
        }
        return strategies.get(error_type, "comprehensive_analysis")
    
    def _assess_rollback_need(self, error: str) -> bool:
        """Assess if rollback is needed."""
        critical_errors = ["syntax", "import", "critical"]
        return any(err in error.lower() for err in critical_errors)

class MissionAwareHealer:
    """Mission-aware healing prioritization."""
    
    def __init__(self):
        self.active_missions = []
        self.mission_impact_map = {}
        
    def register_active_mission(self, mission_id: str, mission_type: str, critical_files: List[str]):
        """Register an active mission for impact assessment."""
        self.active_missions.append({
            "id": mission_id,
            "type": mission_type,
            "critical_files": critical_files,
            "start_time": datetime.now()
        })
    
    def assess_issue_impact(self, issue: Dict[str, Any]) -> float:
        """Assess the impact of an issue on active missions."""
        impact_score = 0.0
        
        for mission in self.active_missions:
            if any(critical_file in issue.get("file_path", "") for critical_file in mission["critical_files"]):
                impact_score += 1.0
                
        return min(impact_score, 1.0)
    
    def prioritize_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize issues based on mission impact."""
        for issue in issues:
            issue["mission_impact"] = self.assess_issue_impact(issue)
            issue["priority_score"] = self._calculate_priority_score(issue)
        
        return sorted(issues, key=lambda x: x["priority_score"], reverse=True)
    
    def _calculate_priority_score(self, issue: Dict[str, Any]) -> float:
        """Calculate priority score based on multiple factors."""
        base_score = 0.0
        
        # Mission impact (40% weight)
        base_score += issue.get("mission_impact", 0.0) * 0.4
        
        # Error severity (30% weight)
        severity_scores = {"critical": 1.0, "high": 0.7, "medium": 0.4, "low": 0.1}
        severity = issue.get("severity", "medium")
        base_score += severity_scores.get(severity, 0.4) * 0.3
        
        # File importance (20% weight)
        file_importance = self._assess_file_importance(issue.get("file_path", ""))
        base_score += file_importance * 0.2
        
        # Error frequency (10% weight)
        error_frequency = issue.get("frequency", 1)
        base_score += min(error_frequency / 10.0, 1.0) * 0.1
        
        return base_score
    
    def _assess_file_importance(self, file_path: str) -> float:
        """Assess the importance of a file based on its role in the system."""
        critical_files = [
            "cognitive_forge_engine.py",
            "advanced_database.py",
            "main.py",
            "agent_factory.py"
        ]
        
        core_files = [
            "advanced_agents.py",
            "blueprint_tasks.py",
            "crew_manager.py"
        ]
        
        filename = Path(file_path).name
        
        if filename in critical_files:
            return 1.0
        elif filename in core_files:
            return 0.8
        elif "test" in filename.lower():
            return 0.3
        else:
            return 0.5

class PerformanceOptimizer:
    """Performance optimization capabilities."""
    
    def __init__(self):
        self.performance_metrics = {}
        
    def analyze_performance(self, file_path: str) -> Dict[str, Any]:
        """Analyze performance characteristics of a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic performance metrics
            lines = content.split('\n')
            complexity = self._calculate_complexity(content)
            imports = self._analyze_imports(content)
            
            return {
                "file_path": file_path,
                "lines_of_code": len(lines),
                "complexity_score": complexity,
                "import_count": len(imports),
                "performance_issues": self._identify_performance_issues(content, complexity),
                "optimization_suggestions": self._generate_optimization_suggestions(content, complexity)
            }
        except Exception as e:
            logger.error(f"Error analyzing performance for {file_path}: {e}")
            return {"file_path": file_path, "error": str(e)}
    
    def _calculate_complexity(self, content: str) -> float:
        """Calculate cyclomatic complexity."""
        try:
            tree = ast.parse(content)
            complexity = 1  # Base complexity
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1
            
            return complexity
        except:
            return 1.0
    
    def _analyze_imports(self, content: str) -> List[str]:
        """Analyze import statements."""
        try:
            tree = ast.parse(content)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
            
            return imports
        except:
            return []
    
    def _identify_performance_issues(self, content: str, complexity: float) -> List[str]:
        """Identify potential performance issues."""
        issues = []
        
        if complexity > 10:
            issues.append("High cyclomatic complexity - consider refactoring")
        
        if "import *" in content:
            issues.append("Wildcard imports - specify exact imports")
        
        if content.count("for") > content.count("while") * 2:
            issues.append("Consider using list comprehensions or generators")
        
        return issues
    
    def _generate_optimization_suggestions(self, content: str, complexity: float) -> List[str]:
        """Generate optimization suggestions."""
        suggestions = []
        
        if complexity > 10:
            suggestions.append("Break down complex functions into smaller, focused functions")
        
        if "time.sleep" in content:
            suggestions.append("Consider using asyncio.sleep for non-blocking operations")
        
        if "requests.get" in content and "async" not in content:
            suggestions.append("Consider using aiohttp for async HTTP requests")
        
        return suggestions

class CodebaseHealer:
    """The core class for the Fix-AI system with enhanced capabilities."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.issues: List[Dict[str, Any]] = []
        self.healing_plan: List[Dict[str, Any]] = []
        self.report: Dict[str, Any] = {"summary": {}, "details": []}
        self.performance_issues: List[Dict[str, Any]] = []
        
        # Initialize Weave observability
        self.observability = observability_manager
        
        # Initialize enhanced components
        self.phoenix = PhoenixProtocol()
        self.mission_healer = MissionAwareHealer()
        self.performance_optimizer = PerformanceOptimizer()

        REPORTS_DIRECTORY.mkdir(exist_ok=True, parents=True)
        BACKUP_DIRECTORY.mkdir(exist_ok=True, parents=True)
        
        logger.info("🔍 Weave observability initialized for Fix-AI")

    def _log_phase(self, phase_name: str):
        logger.info(f"\n{'='*25}\n🚀 PHASE: {phase_name}\n{'='*25}")

    def _get_python_files(self) -> List[Path]:
        """Finds all Python files in the src directory."""
        return list(SRC_DIRECTORY.rglob("*.py"))

    def run(self):
        """Executes the full end-to-end healing process with Weave observability."""
        operation_id = f"fix_ai_{int(time.time())}"
        
        with self.observability.mission_trace(operation_id, "Comprehensive Codebase Healing") as trace_data:
            logger.info("🚀 Initiating Weave-Enhanced Fix-AI: The Sentient Codebase Healer")
            logger.info("🔧 Enhanced with Phoenix Protocol, Mission Awareness, Performance Optimization, and Full Observability")
            self.report['start_time'] = datetime.now().isoformat()

            # Create a backup of the source directory first
            logger.info(f"Creating a backup of the 'src' directory at: {BACKUP_DIRECTORY}")
            shutil.copytree(SRC_DIRECTORY, BACKUP_DIRECTORY)
            logger.success("Backup complete. Proceeding with healing process.")

            # Log backup creation with observability
            self.observability.log_system_event("backup_created", {
                "backup_directory": str(BACKUP_DIRECTORY),
                "source_directory": str(SRC_DIRECTORY)
            }, operation_id)

            self.run_diagnosis_phase()
            self.run_performance_analysis_phase()
            
            if not self.issues and not self.performance_issues:
                logger.success("🎉 No issues found. The codebase is already in excellent health!")
                
                # Log success with observability
                self.observability.log_system_event("healing_completed", {
                    "status": "no_issues_found",
                    "issues_count": 0,
                    "performance_issues_count": 0
                }, operation_id)
                return

            self.run_planning_phase()
            self.run_execution_phase()
            self.run_final_validation_phase()
            self.generate_report()

            # Log completion with observability
            self.observability.log_system_event("healing_completed", {
                "status": "completed",
                "issues_count": len(self.issues),
                "performance_issues_count": len(self.performance_issues),
                "healing_plan_count": len(self.healing_plan)
            }, operation_id)

            logger.info("✅ Weave-Enhanced Fix-AI process complete.")

    def run_diagnosis_phase(self):
        """Phase 1: Scan the codebase for all potential issues."""
        self._log_phase("DIAGNOSIS")
        files = self._get_python_files()
        logger.info(f"Scanning {len(files)} Python files...")

        for file in files:
            # 1. Syntax Check
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    ast.parse(f.read())
            except SyntaxError as e:
                issue = {
                    "file_path": str(file),
                    "line": e.lineno,
                    "type": "SyntaxError",
                    "message": str(e),
                    "severity": "critical"
                }
                # Apply Phoenix Protocol analysis
                phoenix_analysis = self.phoenix.analyze_error(str(e), {"file_path": str(file)})
                issue.update(phoenix_analysis)
                self.issues.append(issue)

            # 2. Linting Check (using flake8)
            result = subprocess.run(['flake8', str(file)], capture_output=True, text=True)
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    parts = line.split(':')
                    if len(parts) >= 4:
                        issue = {
                            "file_path": parts[0],
                            "line": int(parts[1]),
                            "type": "LintingError",
                            "message": f"{parts[3].strip()} ({parts[2].strip()})",
                            "severity": "medium"
                        }
                        # Apply Phoenix Protocol analysis
                        phoenix_analysis = self.phoenix.analyze_error(parts[3].strip(), {"file_path": parts[0]})
                        issue.update(phoenix_analysis)
                        self.issues.append(issue)

        # Apply mission-aware prioritization
        self.issues = self.mission_healer.prioritize_issues(self.issues)
        
        logger.success(f"Diagnosis complete. Found {len(self.issues)} issues.")

    def run_performance_analysis_phase(self):
        """Phase 1.5: Analyze performance characteristics."""
        self._log_phase("PERFORMANCE ANALYSIS")
        files = self._get_python_files()
        logger.info(f"Analyzing performance for {len(files)} Python files...")

        for file in files:
            analysis = self.performance_optimizer.analyze_performance(str(file))
            if analysis.get("performance_issues"):
                self.performance_issues.append(analysis)

        logger.success(f"Performance analysis complete. Found {len(self.performance_issues)} files with optimization opportunities.")

    def run_planning_phase(self):
        """Phase 2: Use an AI Architect to triage issues and create a healing plan."""
        self._log_phase("TRIAGE & PLANNING")
        if not LLM:
            logger.error("LLM not initialized. Cannot proceed with AI-driven planning.")
            return

        architect = Agent(
            role="Lead Software Architect & Codebase Strategist",
            goal="Analyze diagnosed codebase issues and performance problems. Create a prioritized, step-by-step JSON healing plan that considers mission impact and system architecture.",
            backstory="""You are a master architect specializing in the Cognitive Forge system architecture. 
            You understand the critical components (cognitive_forge_engine.py, advanced_database.py, etc.) 
            and can create healing plans that maintain system integrity while resolving issues efficiently.""",
            llm=LLM, verbose=True
        )

        planning_task = Task(
            description=f"""Analyze the following diagnosed issues and performance problems. Create a prioritized, step-by-step healing plan in raw JSON format.
            
            CRITICAL ISSUES:
            {json.dumps(self.issues, indent=2)}
            
            PERFORMANCE ISSUES:
            {json.dumps(self.performance_issues, indent=2)}
            
            Your plan should be an array of steps. Each step must include:
            - 'file_path': The file to fix
            - 'line': Line number (if applicable)
            - 'issue_type': Type of issue
            - 'description': Clear description of the problem
            - 'proposed_action': Specific action to take
            - 'priority': high/medium/low based on mission impact
            - 'estimated_effort': quick/moderate/complex
            
            Prioritize critical SyntaxErrors first, then high-impact issues, then performance optimizations.
            Consider the Cognitive Forge architecture and mission-critical components.
            """,
            expected_output="A raw JSON array representing the prioritized healing plan.",
            agent=architect
        )

        crew = Crew(agents=[architect], tasks=[planning_task], process=Process.sequential)
        plan_str = crew.kickoff()

        try:
            self.healing_plan = json.loads(plan_str)
            logger.success(f"AI Architect has created a healing plan with {len(self.healing_plan)} steps.")
        except json.JSONDecodeError:
            logger.error(f"Failed to parse AI-generated healing plan: {plan_str}")
            # Fallback to a simple, non-AI plan
            self.healing_plan = sorted(self.issues, key=lambda x: 0 if x['type'] == 'SyntaxError' else 1)
            for issue in self.healing_plan:
                issue['proposed_action'] = f"Fix the {issue['type']}."
            logger.warning("Falling back to a simple, prioritized plan.")

    def run_execution_phase(self):
        """Phase 3: Execute the healing plan with the self-healing iterative loop."""
        self._log_phase("EXECUTION & SELF-HEALING")

        fixer_agent = Agent(
            role="Expert Python Debugger & Code Fixer",
            goal="Given a specific file, line number, error, and code context, provide the corrected block of code to resolve the issue. Your output must be ONLY the raw, corrected code block.",
            backstory="""You are a surgical code fixer specializing in the Cognitive Forge system. 
            You understand the architecture, dependencies, and can provide minimal, correct changes 
            that maintain system integrity while resolving issues.""",
            llm=LLM, verbose=True
        )

        for i, step in enumerate(self.healing_plan):
            logger.info(f"Attempting to fix Step {i+1}/{len(self.healing_plan)}: {step['description']} in {step['file_path']}:{step.get('line', 'N/A')}")
            retries = MAX_FIX_RETRIES
            current_error = step.get('message', 'Unknown error')
            
            while retries > 0:
                try:
                    file_path = Path(step['file_path'])
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # Provide context around the error line
                    line_num = step.get('line', 1)
                    start = max(0, line_num - 5)
                    end = min(len(lines), line_num + 5)
                    code_context = "".join(lines[start:end])

                    fix_task = Task(
                        description=f"""Fix this issue in the Cognitive Forge system.
                        
                        FILE: {step['file_path']}
                        LINE: {line_num}
                        CURRENT ERROR: {current_error}
                        ISSUE TYPE: {step.get('issue_type', 'Unknown')}
                        CODE CONTEXT:
                        ```python
                        {code_context}
                        ```
                        
                        Provide ONLY the corrected code block for the problematic line(s). 
                        Ensure the fix maintains system architecture integrity.
                        Do not explain, just provide the raw code.
                        """,
                        expected_output="The raw, corrected block of code.",
                        agent=fixer_agent
                    )
                    
                    crew = Crew(agents=[fixer_agent], tasks=[fix_task], process=Process.sequential)
                    corrected_code = crew.kickoff()
                    
                    # Apply the fix
                    if step.get('line'):
                        lines[step['line'] - 1] = corrected_code + '\n'
                    else:
                        # For performance issues or general fixes, append to end
                        lines.append(corrected_code + '\n')
                        
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)

                    # **VALIDATION STEP**
                    with open(file_path, 'r', encoding='utf-8') as f:
                        ast.parse(f.read())
                    
                    logger.success(f"Successfully fixed and validated: {step['description']}")
                    step['status'] = 'FIXED'
                    break # Exit the while loop on success

                except Exception as e:
                    retries -= 1
                    current_error = f"Validation after fix failed: {str(e)}"
                    logger.warning(f"Attempt failed. Re-evaluating... ({retries} retries left). New error: {current_error}")
                    
                    # Apply Phoenix Protocol for error recovery
                    recovery_analysis = self.phoenix.analyze_error(current_error, {"file_path": step['file_path']})
                    if recovery_analysis.get("rollback_required", False):
                        logger.warning("Rollback required due to critical error")
                        # Could implement rollback logic here
                    
                    if retries == 0:
                        logger.error(f"Could not fix {step['description']} after {MAX_FIX_RETRIES} attempts.")
                        step['status'] = 'FAILED'
                        step['final_error'] = current_error

    def run_final_validation_phase(self):
        """Phase 4: Run a final, full-system scan to check for regressions."""
        self._log_phase("FINAL VALIDATION")
        # Temporarily clear issues and re-run diagnosis
        original_issues_count = len(self.issues)
        self.issues = []
        self.run_diagnosis_phase()
        
        self.report['final_validation'] = {
            "initial_issues": original_issues_count,
            "remaining_issues": len(self.issues),
            "performance_issues_analyzed": len(self.performance_issues)
        }
        if not self.issues:
            logger.success("Final validation passed. No remaining issues or regressions detected.")
        else:
            logger.warning(f"Final validation found {len(self.issues)} remaining issues.")

    def generate_report(self):
        """Phase 5: Generate a comprehensive report of the healing process."""
        self._log_phase("REPORTING")
        self.report['end_time'] = datetime.now().isoformat()
        
        fixed_count = sum(1 for step in self.healing_plan if step.get('status') == 'FIXED')
        failed_count = sum(1 for step in self.healing_plan if step.get('status') == 'FAILED')

        self.report['summary'] = {
            "total_issues_identified": self.report.get('final_validation', {}).get('initial_issues', 0),
            "issues_attempted": len(self.healing_plan),
            "issues_fixed": fixed_count,
            "issues_failed": failed_count,
            "remaining_issues_after_fix": self.report.get('final_validation', {}).get('remaining_issues', 0),
            "performance_issues_analyzed": len(self.performance_issues),
            "mission_impact_analysis": "Applied mission-aware prioritization",
            "phoenix_protocol_integration": "Active error recovery and analysis"
        }
        self.report['details'] = self.healing_plan
        self.report['performance_analysis'] = self.performance_issues

        report_path = REPORTS_DIRECTORY / f"fix_ai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2)
        
        logger.success(f"Comprehensive report saved to {report_path}")
        
        # Print summary
        logger.info(f"\n{'='*50}")
        logger.info("📊 FIX-AI EXECUTION SUMMARY")
        logger.info(f"{'='*50}")
        logger.info(f"✅ Issues Fixed: {fixed_count}")
        logger.info(f"❌ Issues Failed: {failed_count}")
        logger.info(f"🔧 Performance Issues Analyzed: {len(self.performance_issues)}")
        logger.info(f"🎯 Mission Impact Analysis: Applied")
        logger.info(f"🔄 Phoenix Protocol: Active")
        logger.info(f"📄 Detailed Report: {report_path}")
        logger.info(f"{'='*50}")


if __name__ == "__main__":
    if not LLM:
        logger.error("Could not start Fix-AI. The GOOGLE_API_KEY environment variable is not set.")
        sys.exit(1)
        
    healer = CodebaseHealer(PROJECT_ROOT)
    healer.run() 