#!/usr/bin/env python3
"""
Fix-AI: The Sentient Codebase Healer
A sophisticated, self-healing diagnostic and repair system for the Cognitive Forge codebase.

Enhanced with:
- Phoenix Protocol integration for seamless error recovery
- Mission-aware healing prioritization
- Performance optimization capabilities
- Cognitive Forge architecture awareness
- Simplified architecture to avoid dependency issues
- Surgical Patching for precise multi-line fixes
- Automated Rollback for critical failure recovery
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
from loguru import logger

# --- CONFIGURATION ---
PROJECT_ROOT = Path(__file__).parent
SRC_DIRECTORY = PROJECT_ROOT / "src"
REPORTS_DIRECTORY = PROJECT_ROOT / "logs" / "fix_ai_reports"
BACKUP_DIRECTORY = PROJECT_ROOT / "backups" / f"fix_ai_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
MAX_FIX_RETRIES = 3
PERFORMANCE_THRESHOLD = 0.8

# --- INITIALIZE LLM ---
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    # Try to import LLM without CrewAI dependencies
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        LLM = ChatGoogleGenerativeAI(
            model=os.getenv("LLM_MODEL", "gemini-1.5-pro"), 
            temperature=0.3
        )
        LLM_AVAILABLE = True
    except ImportError:
        logger.warning("Langchain Google GenAI not available. Running in analysis-only mode.")
        LLM = None
        LLM_AVAILABLE = False
        
except ImportError:
    print("Warning: dotenv is not installed. Make sure your environment variables are set.")
    LLM = None
    LLM_AVAILABLE = False

class RollbackManager:
    """Automated rollback system for critical failure recovery."""
    
    def __init__(self, backup_directory: Path):
        self.backup_directory = backup_directory
        self.rollback_history = []
        self.files_modified = set()
        
    def register_file_modification(self, file_path: str):
        """Register that a file has been modified and may need rollback."""
        self.files_modified.add(file_path)
        logger.debug(f"Registered file for potential rollback: {file_path}")
    
    def perform_rollback(self, file_path: str, reason: str = "Critical failure") -> bool:
        """Perform automated rollback of a specific file."""
        try:
            # Calculate relative path from src directory
            src_path = Path(SRC_DIRECTORY)
            file_rel_path = Path(file_path).relative_to(src_path)
            backup_file_path = self.backup_directory / file_rel_path
            
            if not backup_file_path.exists():
                logger.error(f"Backup file not found: {backup_file_path}")
                return False
            
            # Create backup of current state before rollback
            current_backup_path = Path(file_path).parent / f".{Path(file_path).name}.pre_rollback"
            if Path(file_path).exists():
                shutil.copy2(file_path, current_backup_path)
                logger.info(f"Created pre-rollback backup: {current_backup_path}")
            
            # Perform the rollback
            shutil.copy2(backup_file_path, file_path)
            
            # Record rollback in history
            rollback_record = {
                "timestamp": datetime.now().isoformat(),
                "file_path": file_path,
                "reason": reason,
                "backup_source": str(backup_file_path),
                "pre_rollback_backup": str(current_backup_path) if current_backup_path.exists() else None
            }
            self.rollback_history.append(rollback_record)
            
            logger.warning(f"🔄 AUTOMATED ROLLBACK: {file_path} - {reason}")
            logger.info(f"Rollback completed successfully. File restored from backup.")
            
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed for {file_path}: {e}")
            return False
    
    def perform_selective_rollback(self, files_to_rollback: List[str], reason: str = "Critical failure") -> Dict[str, bool]:
        """Perform rollback on multiple files and return results."""
        results = {}
        
        for file_path in files_to_rollback:
            success = self.perform_rollback(file_path, reason)
            results[file_path] = success
        
        return results
    
    def perform_full_rollback(self, reason: str = "Critical system failure") -> bool:
        """Perform full rollback of all modified files."""
        logger.warning(f"🔄 INITIATING FULL SYSTEM ROLLBACK - {reason}")
        
        if not self.files_modified:
            logger.info("No files were modified. Full rollback not needed.")
            return True
        
        # Remove current src directory
        if SRC_DIRECTORY.exists():
            shutil.rmtree(SRC_DIRECTORY)
            logger.info("Removed current src directory")
        
        # Restore from backup
        shutil.copytree(self.backup_directory, SRC_DIRECTORY)
        logger.success("Full system rollback completed successfully")
        
        # Record full rollback
        rollback_record = {
            "timestamp": datetime.now().isoformat(),
            "type": "full_system_rollback",
            "reason": reason,
            "files_affected": len(self.files_modified),
            "backup_source": str(self.backup_directory)
        }
        self.rollback_history.append(rollback_record)
        
        return True
    
    def get_rollback_history(self) -> List[Dict[str, Any]]:
        """Get the complete rollback history."""
        return self.rollback_history
    
    def validate_backup_integrity(self) -> bool:
        """Validate that the backup directory is intact and accessible."""
        try:
            if not self.backup_directory.exists():
                logger.error(f"Backup directory does not exist: {self.backup_directory}")
                return False
            
            # Check if backup contains expected structure
            backup_files = list(self.backup_directory.rglob("*.py"))
            if not backup_files:
                logger.error("Backup directory contains no Python files")
                return False
            
            logger.info(f"Backup integrity validated. {len(backup_files)} Python files found.")
            return True
            
        except Exception as e:
            logger.error(f"Backup integrity validation failed: {e}")
            return False

class SurgicalPatcher:
    """Advanced surgical patching system for precise code modifications."""
    
    def __init__(self):
        self.patch_history = []
        
    def parse_diff_patch(self, diff_content: str) -> List[Dict[str, Any]]:
        """Parse a diff patch and extract surgical operations."""
        operations = []
        lines = diff_content.strip().split('\n')
        
        current_operation = None
        line_number = 0
        
        for line in lines:
            # Parse diff header
            if line.startswith('@@'):
                # Extract line numbers from @@ -old_start,old_count +new_start,new_count @@
                match = re.search(r'@@ -(\d+),?(\d+)? \+(\d+),?(\d+)? @@', line)
                if match:
                    old_start = int(match.group(1))
                    old_count = int(match.group(2)) if match.group(2) else 1
                    new_start = int(match.group(3))
                    new_count = int(match.group(4)) if match.group(4) else 1
                    
                    current_operation = {
                        'type': 'multi_line',
                        'old_start': old_start,
                        'old_count': old_count,
                        'new_start': new_start,
                        'new_count': new_count,
                        'lines': []
                    }
                    operations.append(current_operation)
                    line_number = old_start
                    
            elif current_operation and line.startswith(' '):
                # Context line (unchanged)
                current_operation['lines'].append({
                    'type': 'context',
                    'line_number': line_number,
                    'content': line[1:],
                    'action': 'keep'
                })
                line_number += 1
                
            elif current_operation and line.startswith('-'):
                # Deletion line
                current_operation['lines'].append({
                    'type': 'deletion',
                    'line_number': line_number,
                    'content': line[1:],
                    'action': 'delete'
                })
                line_number += 1
                
            elif current_operation and line.startswith('+'):
                # Addition line
                current_operation['lines'].append({
                    'type': 'addition',
                    'line_number': None,  # Will be calculated during application
                    'content': line[1:],
                    'action': 'insert'
                })
                
        return operations
    
    def apply_surgical_patch(self, file_path: str, operations: List[Dict[str, Any]]) -> bool:
        """Apply surgical patch operations to a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Sort operations by line number (descending) to avoid offset issues
            sorted_operations = sorted(operations, key=lambda x: x.get('old_start', 0), reverse=True)
            
            for operation in sorted_operations:
                if operation['type'] == 'multi_line':
                    lines = self._apply_multi_line_operation(lines, operation)
                elif operation['type'] == 'single_line':
                    lines = self._apply_single_line_operation(lines, operation)
            
            # Write the modified file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True
            
        except Exception as e:
            logger.error(f"Error applying surgical patch to {file_path}: {e}")
            return False
    
    def _apply_multi_line_operation(self, lines: List[str], operation: Dict[str, Any]) -> List[str]:
        """Apply a multi-line surgical operation."""
        old_start = operation['old_start'] - 1  # Convert to 0-based index
        old_count = operation['old_count']
        
        # Calculate the actual lines to replace
        actual_lines = []
        insertions = []
        deletions = []
        
        for line_op in operation['lines']:
            if line_op['action'] == 'keep':
                actual_lines.append(line_op['content'])
            elif line_op['action'] == 'delete':
                deletions.append(line_op['content'])
            elif line_op['action'] == 'insert':
                insertions.append(line_op['content'])
        
        # Verify the context matches
        context_lines = lines[old_start:old_start + len(actual_lines)]
        if not self._verify_context(context_lines, actual_lines):
            logger.warning(f"Context mismatch in surgical patch at line {old_start + 1}")
            return lines
        
        # Apply the surgical operation
        new_lines = []
        new_lines.extend(lines[:old_start])
        
        # Add the modified content
        for line_op in operation['lines']:
            if line_op['action'] in ['keep', 'insert']:
                new_lines.append(line_op['content'] + '\n')
        
        new_lines.extend(lines[old_start + old_count:])
        
        return new_lines
    
    def _apply_single_line_operation(self, lines: List[str], operation: Dict[str, Any]) -> List[str]:
        """Apply a single-line surgical operation."""
        line_number = operation['line_number'] - 1  # Convert to 0-based index
        action = operation['action']
        content = operation['content']
        
        if action == 'replace':
            lines[line_number] = content + '\n'
        elif action == 'delete':
            lines.pop(line_number)
        elif action == 'insert':
            lines.insert(line_number, content + '\n')
        
        return lines
    
    def _verify_context(self, actual_lines: List[str], expected_lines: List[str]) -> bool:
        """Verify that the context lines match before applying a patch."""
        if len(actual_lines) != len(expected_lines):
            return False
        
        for actual, expected in zip(actual_lines, expected_lines):
            if actual.strip() != expected.strip():
                return False
        
        return True
    
    def generate_simple_patch(self, file_path: str, line_number: int, old_content: str, new_content: str) -> Dict[str, Any]:
        """Generate a simple single-line patch operation."""
        return {
            'type': 'single_line',
            'line_number': line_number,
            'action': 'replace',
            'old_content': old_content,
            'new_content': new_content
        }

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
            "rollback_required": self._assess_rollback_need(error),
            "rollback_scope": self._determine_rollback_scope(error, context)
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
        critical_errors = ["syntax", "import", "critical", "indentation", "unexpected indent"]
        return any(err in error.lower() for err in critical_errors)
    
    def _determine_rollback_scope(self, error: str, context: Dict[str, Any]) -> str:
        """Determine the scope of rollback needed."""
        error_lower = error.lower()
        
        # Full system rollback indicators
        full_rollback_indicators = [
            "multiple files affected",
            "system corruption",
            "backup integrity",
            "critical system failure"
        ]
        
        # Single file rollback indicators
        single_file_indicators = [
            "syntax error",
            "import error",
            "indentation error",
            "single file issue"
        ]
        
        for indicator in full_rollback_indicators:
            if indicator in error_lower or indicator in context.get("description", "").lower():
                return "full_system"
        
        for indicator in single_file_indicators:
            if indicator in error_lower:
                return "single_file"
        
        return "single_file"  # Default to single file rollback

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

class SurgicalAIFixer:
    """Advanced AI-powered code fixer with surgical patching capabilities."""
    
    def __init__(self, llm):
        self.llm = llm
        self.patcher = SurgicalPatcher()
    
    def generate_surgical_fix(self, file_path: str, line_num: int, error: str, code_context: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Generate a surgical fix using the LLM."""
        if not self.llm:
            return "# AI fix not available - manual review required", []
        
        # Determine if this needs a surgical patch or simple fix
        needs_surgical = self._assess_surgical_need(error, code_context)
        
        if needs_surgical:
            return self._generate_surgical_patch(file_path, line_num, error, code_context)
        else:
            return self._generate_simple_fix(file_path, line_num, error, code_context)
    
    def _assess_surgical_need(self, error: str, code_context: str) -> bool:
        """Assess if the error requires surgical patching."""
        surgical_indicators = [
            "indentation",
            "missing colon",
            "unexpected indent",
            "expected an indented block",
            "multiple lines",
            "function definition",
            "class definition",
            "try/except",
            "if/elif/else",
            "for/while loop"
        ]
        
        error_lower = error.lower()
        context_lower = code_context.lower()
        
        # Check for surgical indicators
        for indicator in surgical_indicators:
            if indicator in error_lower or indicator in context_lower:
                return True
        
        # Check if context spans multiple lines
        if code_context.count('\n') > 3:
            return True
        
        return False
    
    def _generate_surgical_patch(self, file_path: str, line_num: int, error: str, code_context: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Generate a surgical patch for complex fixes."""
        prompt = f"""
        Generate a surgical patch to fix this Python code issue. Provide your response in standard diff format.
        
        FILE: {file_path}
        LINE: {line_num}
        ERROR: {error}
        
        CODE CONTEXT:
        ```python
        {code_context}
        ```
        
        Provide ONLY a diff patch in this format:
        @@ -old_start,old_count +new_start,new_count @@
         unchanged line
        -line to delete
        +line to add
         unchanged line
        
        Focus on the minimal changes needed to fix the issue. Include enough context lines for accurate patching.
        """
        
        try:
            response = self.llm.invoke(prompt)
            diff_content = response.content.strip()
            
            # Parse the diff patch
            operations = self.patcher.parse_diff_patch(diff_content)
            
            return "SURGICAL_PATCH", operations
            
        except Exception as e:
            logger.error(f"Error generating surgical patch: {e}")
            return "# Surgical patch failed - manual review required", []
    
    def _generate_simple_fix(self, file_path: str, line_num: int, error: str, code_context: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Generate a simple single-line fix."""
        prompt = f"""
        Fix this Python code issue:
        
        FILE: {file_path}
        LINE: {line_num}
        ERROR: {error}
        
        CODE CONTEXT:
        ```python
        {code_context}
        ```
        
        Provide ONLY the corrected line of code. Do not explain, just provide the raw code.
        """
        
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip(), []
        except Exception as e:
            logger.error(f"Error generating simple fix: {e}")
            return "# AI fix failed - manual review required", []

class CodebaseHealer:
    """The core class for the Fix-AI system with enhanced capabilities."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.issues: List[Dict[str, Any]] = []
        self.healing_plan: List[Dict[str, Any]] = []
        self.report: Dict[str, Any] = {"summary": {}, "details": []}
        self.performance_issues: List[Dict[str, Any]] = []
        
        # Initialize enhanced components
        self.phoenix = PhoenixProtocol()
        self.mission_healer = MissionAwareHealer()
        self.performance_optimizer = PerformanceOptimizer()
        self.ai_fixer = SurgicalAIFixer(LLM) if LLM_AVAILABLE else None
        self.surgical_patcher = SurgicalPatcher()
        self.rollback_manager = RollbackManager(BACKUP_DIRECTORY)

        REPORTS_DIRECTORY.mkdir(exist_ok=True, parents=True)
        BACKUP_DIRECTORY.mkdir(exist_ok=True, parents=True)

    def _log_phase(self, phase_name: str):
        logger.info(f"\n{'='*25}\n🚀 PHASE: {phase_name}\n{'='*25}")

    def _get_python_files(self) -> List[Path]:
        """Finds all Python files in the src directory."""
        return list(SRC_DIRECTORY.rglob("*.py"))

    def run(self):
        """Executes the full end-to-end healing process."""
        logger.info("🚀 Initiating Fix-AI: The Sentient Codebase Healer")
        logger.info("🔧 Enhanced with Phoenix Protocol, Mission Awareness, Performance Optimization, Surgical Patching, and Automated Rollback")
        if not LLM_AVAILABLE:
            logger.warning("⚠️ Running in analysis-only mode (no AI fixes available)")
        self.report['start_time'] = datetime.now().isoformat()

        # Validate backup integrity before starting
        if not self.rollback_manager.validate_backup_integrity():
            logger.error("❌ Backup integrity validation failed. Cannot proceed safely.")
            return

        # Create a backup of the source directory first
        logger.info(f"Creating a backup of the 'src' directory at: {BACKUP_DIRECTORY}")
        shutil.copytree(SRC_DIRECTORY, BACKUP_DIRECTORY)
        logger.success("Backup complete. Proceeding with healing process.")

        self.run_diagnosis_phase()
        self.run_performance_analysis_phase()
        
        if not self.issues and not self.performance_issues:
            logger.success("🎉 No issues found. The codebase is already in excellent health!")
            return

        self.run_planning_phase()
        self.run_execution_phase()
        self.run_final_validation_phase()
        self.generate_report()

        logger.info("✅ Fix-AI process complete.")

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
            try:
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
            except FileNotFoundError:
                logger.warning("flake8 not found. Skipping linting checks.")

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
        """Phase 2: Create a healing plan based on diagnosed issues."""
        self._log_phase("TRIAGE & PLANNING")
        
        # Create a simple, prioritized healing plan
        self.healing_plan = []
        
        for issue in self.issues:
            step = {
                "file_path": issue["file_path"],
                "line": issue.get("line", 1),
                "issue_type": issue["type"],
                "description": f"Fix {issue['type']}: {issue['message']}",
                "proposed_action": f"Fix the {issue['type']} on line {issue.get('line', 'N/A')}",
                "priority": "high" if issue.get("severity") in ["critical", "high"] else "medium",
                "estimated_effort": "quick" if issue["type"] == "LintingError" else "moderate"
            }
            self.healing_plan.append(step)
        
        logger.success(f"Created healing plan with {len(self.healing_plan)} steps.")

    def run_execution_phase(self):
        """Phase 3: Execute the healing plan with the self-healing iterative loop."""
        self._log_phase("EXECUTION & SELF-HEALING")

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

                    # Generate fix
                    if self.ai_fixer and step.get("line"):
                        corrected_code, surgical_operations = self.ai_fixer.generate_surgical_fix(
                            step['file_path'], 
                            line_num, 
                            current_error, 
                            code_context
                        )
                    else:
                        # Manual fix suggestions
                        corrected_code = self._generate_manual_fix_suggestion(step, code_context)
                        surgical_operations = []
                    
                    # Apply the fix
                    if corrected_code == "SURGICAL_PATCH" and surgical_operations:
                        # Register file for potential rollback
                        self.rollback_manager.register_file_modification(str(file_path))
                        
                        # Apply surgical patch
                        success = self.surgical_patcher.apply_surgical_patch(str(file_path), surgical_operations)
                        if success:
                            logger.success(f"Successfully applied surgical patch: {step['description']}")
                            step['status'] = 'FIXED'
                            step['fix_type'] = 'surgical_patch'
                            break
                        else:
                            logger.warning(f"Surgical patch failed for: {step['description']}")
                            step['status'] = 'MANUAL_REVIEW_REQUIRED'
                            break
                    elif corrected_code and not corrected_code.startswith("#") and step.get('line'):
                        # Register file for potential rollback
                        self.rollback_manager.register_file_modification(str(file_path))
                        
                        # Apply simple fix
                        lines[step['line'] - 1] = corrected_code + '\n'
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.writelines(lines)

                        # **VALIDATION STEP**
                        with open(file_path, 'r', encoding='utf-8') as f:
                            ast.parse(f.read())
                        
                        logger.success(f"Successfully fixed and validated: {step['description']}")
                        step['status'] = 'FIXED'
                        step['fix_type'] = 'simple_fix'
                        break # Exit the while loop on success
                    else:
                        logger.info(f"Manual review required for: {step['description']}")
                        step['status'] = 'MANUAL_REVIEW_REQUIRED'
                        break

                except Exception as e:
                    retries -= 1
                    current_error = f"Validation after fix failed: {str(e)}"
                    logger.warning(f"Attempt failed. Re-evaluating... ({retries} retries left). New error: {current_error}")
                    
                    # Apply Phoenix Protocol for error recovery
                    recovery_analysis = self.phoenix.analyze_error(current_error, {
                        "file_path": step['file_path'],
                        "description": step['description'],
                        "retries_remaining": retries
                    })
                    
                    if recovery_analysis.get("rollback_required", False) and retries == 0:
                        # Critical failure - perform automated rollback
                        logger.error(f"🔴 CRITICAL FAILURE: {step['description']}")
                        logger.warning("🔄 Initiating automated rollback...")
                        
                        rollback_scope = recovery_analysis.get("rollback_scope", "single_file")
                        
                        if rollback_scope == "full_system":
                            # Full system rollback
                            success = self.rollback_manager.perform_full_rollback(
                                f"Critical failure in {step['file_path']}: {current_error}"
                            )
                            if success:
                                logger.success("Full system rollback completed successfully")
                                step['status'] = 'ROLLED_BACK'
                                step['rollback_scope'] = 'full_system'
                                break
                            else:
                                logger.error("Full system rollback failed!")
                                step['status'] = 'CRITICAL_FAILURE'
                                break
                        else:
                            # Single file rollback
                            success = self.rollback_manager.perform_rollback(
                                step['file_path'],
                                f"Critical failure after {MAX_FIX_RETRIES} attempts: {current_error}"
                            )
                            if success:
                                logger.success(f"Single file rollback completed for {step['file_path']}")
                                step['status'] = 'ROLLED_BACK'
                                step['rollback_scope'] = 'single_file'
                                break
                            else:
                                logger.error(f"Single file rollback failed for {step['file_path']}")
                                step['status'] = 'CRITICAL_FAILURE'
                                break
                    
                    if retries == 0:
                        logger.error(f"Could not fix {step['description']} after {MAX_FIX_RETRIES} attempts.")
                        step['status'] = 'FAILED'
                        step['final_error'] = current_error

    def _generate_manual_fix_suggestion(self, step: Dict[str, Any], code_context: str) -> str:
        """Generate manual fix suggestions for common issues."""
        issue_type = step.get("issue_type", "")
        
        if issue_type == "LintingError":
            # Common linting fixes
            if "unused import" in step.get("message", "").lower():
                return "# Remove unused import - manual review required"
            elif "line too long" in step.get("message", "").lower():
                return "# Line too long - consider breaking into multiple lines"
            elif "missing whitespace" in step.get("message", "").lower():
                return "# Add missing whitespace - manual review required"
        
        return "# Manual review required - AI fix not available"

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
        manual_review_count = sum(1 for step in self.healing_plan if step.get('status') == 'MANUAL_REVIEW_REQUIRED')
        rolled_back_count = sum(1 for step in self.healing_plan if step.get('status') == 'ROLLED_BACK')
        surgical_fixes = sum(1 for step in self.healing_plan if step.get('fix_type') == 'surgical_patch')
        simple_fixes = sum(1 for step in self.healing_plan if step.get('fix_type') == 'simple_fix')

        self.report['summary'] = {
            "total_issues_identified": self.report.get('final_validation', {}).get('initial_issues', 0),
            "issues_attempted": len(self.healing_plan),
            "issues_fixed": fixed_count,
            "issues_failed": failed_count,
            "manual_review_required": manual_review_count,
            "issues_rolled_back": rolled_back_count,
            "surgical_fixes_applied": surgical_fixes,
            "simple_fixes_applied": simple_fixes,
            "remaining_issues_after_fix": self.report.get('final_validation', {}).get('remaining_issues', 0),
            "performance_issues_analyzed": len(self.performance_issues),
            "mission_impact_analysis": "Applied mission-aware prioritization",
            "phoenix_protocol_integration": "Active error recovery and analysis",
            "surgical_patching": "Advanced multi-line fix capabilities",
            "automated_rollback": "Critical failure recovery system",
            "ai_fixes_available": LLM_AVAILABLE
        }
        self.report['details'] = self.healing_plan
        self.report['performance_analysis'] = self.performance_issues
        self.report['rollback_history'] = self.rollback_manager.get_rollback_history()

        report_path = REPORTS_DIRECTORY / f"fix_ai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2)
        
        logger.success(f"Comprehensive report saved to {report_path}")
        
        # Print summary
        logger.info(f"\n{'='*50}")
        logger.info("📊 FIX-AI EXECUTION SUMMARY")
        logger.info(f"{'='*50}")
        logger.info(f"✅ Issues Fixed: {fixed_count}")
        logger.info(f"🔪 Surgical Fixes: {surgical_fixes}")
        logger.info(f"🔧 Simple Fixes: {simple_fixes}")
        logger.info(f"❌ Issues Failed: {failed_count}")
        logger.info(f"🔄 Issues Rolled Back: {rolled_back_count}")
        logger.info(f"🔍 Manual Review Required: {manual_review_count}")
        logger.info(f"🔧 Performance Issues Analyzed: {len(self.performance_issues)}")
        logger.info(f"🎯 Mission Impact Analysis: Applied")
        logger.info(f"🔄 Phoenix Protocol: Active")
        logger.info(f"🔪 Surgical Patching: Active")
        logger.info(f"🛡️ Automated Rollback: Active")
        logger.info(f"🤖 AI Fixes Available: {LLM_AVAILABLE}")
        logger.info(f"📄 Detailed Report: {report_path}")
        logger.info(f"{'='*50}")


if __name__ == "__main__":
    healer = CodebaseHealer(PROJECT_ROOT)
    healer.run() 