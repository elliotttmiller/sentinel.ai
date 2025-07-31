#!/usr/bin/env python3
"""
Fix-AI: The Sentient Codebase Healer
A sophisticated, self-healing diagnostic and repair system for the Cognitive Forge codebase.
"""

import os
import sys
import json
import time
import ast
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from loguru import logger
from crewai import Agent, Task, Crew, Process

# --- CONFIGURATION ---
PROJECT_ROOT = Path(__file__).parent
SRC_DIRECTORY = PROJECT_ROOT / "src"
REPORTS_DIRECTORY = PROJECT_ROOT / "logs" / "fix_ai_reports"
BACKUP_DIRECTORY = PROJECT_ROOT / "backups" / f"fix_ai_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
MAX_FIX_RETRIES = 3  # The number of times the self-healing loop will re-attempt a fix

# --- INITIALIZE LLM ---
try:
    from dotenv import load_dotenv
    load_dotenv()
    from src.utils.google_ai_wrapper import create_google_ai_llm
    LLM = create_google_ai_llm(
        model_name=os.getenv("LLM_MODEL", "gemini-1.5-pro"),
        temperature=0.5
    )
except ImportError:
    print("Warning: dotenv is not installed. Make sure your environment variables are set.")
    LLM = None


class CodebaseHealer:
    """The core class for the Fix-AI system."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.issues: List[Dict[str, Any]] = []
        self.healing_plan: List[Dict[str, Any]] = []
        self.report: Dict[str, Any] = {"summary": {}, "details": []}

        REPORTS_DIRECTORY.mkdir(exist_ok=True, parents=True)
        BACKUP_DIRECTORY.mkdir(exist_ok=True, parents=True)

    def _log_phase(self, phase_name: str):
        logger.info(f"\n{'='*25}\n[PHASE] {phase_name}\n{'='*25}")

    def _get_python_files(self) -> List[Path]:
        """Finds all Python files in the src directory."""
        return list(SRC_DIRECTORY.rglob("*.py"))

    def run(self):
        """Executes the full end-to-end healing process."""
        logger.info("[START] Initiating Fix-AI: The Sentient Codebase Healer")
        self.report['start_time'] = datetime.now().isoformat()

        # Create a backup of the source directory first
        logger.info(f"Creating a backup of the 'src' directory at: {BACKUP_DIRECTORY}")
        shutil.copytree(SRC_DIRECTORY, BACKUP_DIRECTORY)
        logger.success("Backup complete. Proceeding with healing process.")

        self.run_diagnosis_phase()
        if not self.issues:
            logger.success("[SUCCESS] No issues found. The codebase is already in excellent health!")
            return

        self.run_planning_phase()
        self.run_execution_phase()
        self.run_final_validation_phase()
        self.generate_report()

        logger.info("[COMPLETE] Fix-AI process complete.")

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
                self.issues.append({
                    "file_path": str(file),
                    "line": e.lineno,
                    "type": "SyntaxError",
                    "message": str(e)
                })

            # 2. Linting Check (using flake8 if available)
            try:
                result = subprocess.run(['flake8', str(file)], capture_output=True, text=True, timeout=30)
                if result.stdout:
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            parts = line.split(':')
                            if len(parts) >= 4:
                                try:
                                    line_num = int(parts[1])
                                    self.issues.append({
                                        "file_path": parts[0],
                                        "line": line_num,
                                        "type": "LintingError",
                                        "message": f"{parts[3].strip()} ({parts[2].strip()})"
                                    })
                                except (ValueError, IndexError):
                                    # Skip malformed lines
                                    continue
            except (subprocess.TimeoutExpired, FileNotFoundError):
                # flake8 not available or timed out, skip linting
                pass

        logger.success(f"Diagnosis complete. Found {len(self.issues)} issues.")

    def run_planning_phase(self):
        """Phase 2: Use an AI Architect to triage issues and create a healing plan."""
        self._log_phase("TRIAGE & PLANNING")
        if not LLM:
            logger.error("LLM not initialized. Cannot proceed with AI-driven planning.")
            return

        architect = Agent(
            role="Lead Software Architect & Codebase Strategist",
            goal="Analyze a list of diagnosed codebase issues. Prioritize them by severity and create a logical, step-by-step JSON healing plan to resolve them.",
            backstory="You are a master architect who specializes in refactoring and healing complex codebases. You can instantly see the connections between disparate errors and devise the most efficient plan to restore a system to perfect health.",
            llm=LLM, verbose=True
        )

        planning_task = Task(
            description=f"""Analyze the following list of diagnosed codebase issues. Create a prioritized, step-by-step healing plan in a raw JSON format.
            
            ISSUES:
            {json.dumps(self.issues, indent=2)}
            
            Your plan should be an array of steps. Each step must include 'file_path', 'line', 'issue_type', 'message' (renamed from 'description'), and a 'proposed_action'.
            Prioritize critical SyntaxErrors first, then other errors.
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
            backstory="You are a surgical code fixer. You can instantly understand the context of an error and provide the minimal, correct change to fix it without introducing new problems.",
            llm=LLM, verbose=True
        )

        for i, step in enumerate(self.healing_plan):
            logger.info(f"Attempting to fix Step {i+1}/{len(self.healing_plan)}: {step['message']} in {step['file_path']}:{step['line']}")
            retries = MAX_FIX_RETRIES
            current_error = step['message']
            
            while retries > 0:
                try:
                    file_path = Path(step['file_path'])
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # Provide context around the error line
                    start = max(0, step['line'] - 5)
                    end = min(len(lines), step['line'] + 5)
                    code_context = "".join(lines[start:end])

                    fix_task = Task(
                        description=f"""Your previous attempt to fix this issue failed with a new error, or this is the first attempt.
                        Re-evaluate and provide a new, corrected code block.
                        
                        FILE: {step['file_path']}
                        LINE: {step['line']}
                        CURRENT ERROR: {current_error}
                        CODE CONTEXT:
                        ```python
                        {code_context}
                        ```
                        Provide ONLY the corrected code block for the problematic line(s). Do not explain, just provide the raw code.
                        """,
                        expected_output="The raw, corrected block of code.",
                        agent=fixer_agent
                    )
                    
                    crew = Crew(agents=[fixer_agent], tasks=[fix_task], process=Process.sequential)
                    corrected_code = crew.kickoff()
                    
                    # Apply the fix (this is a simple line replacement, could be more sophisticated)
                    lines[step['line'] - 1] = corrected_code + '\n'
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)

                    # **VALIDATION STEP**
                    with open(file_path, 'r', encoding='utf-8') as f:
                        ast.parse(f.read())
                    
                    logger.success(f"Successfully fixed and validated: {step['message']}")
                    step['status'] = 'FIXED'
                    break  # Exit the while loop on success

                except Exception as e:
                    retries -= 1
                    current_error = f"Validation after fix failed: {str(e)}"
                    logger.warning(f"Attempt failed. Re-evaluating... ({retries} retries left). New error: {current_error}")
                    if retries == 0:
                        logger.error(f"Could not fix {step['message']} after {MAX_FIX_RETRIES} attempts.")
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
            "remaining_issues": len(self.issues)
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
            "remaining_issues_after_fix": self.report.get('final_validation', {}).get('remaining_issues', 0)
        }
        self.report['details'] = self.healing_plan

        report_path = REPORTS_DIRECTORY / f"fix_ai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2)
        
        logger.success(f"Comprehensive report saved to {report_path}")


if __name__ == "__main__":
    if not LLM:
        logger.error("Could not start Fix-AI. The GOOGLE_API_KEY environment variable is not set.")
        sys.exit(1)
        
    healer = CodebaseHealer(PROJECT_ROOT)
    healer.run() 