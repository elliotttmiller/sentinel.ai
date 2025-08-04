"""
Phoenix Protocol - Self-Healing Debug & Resolve System
Transforms failures into opportunities for system improvement
"""

import json
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger
from crewai import Task, Crew, Process
from .crewai_bypass import DirectAIAgent, DirectAICrew


class PhoenixProtocol:
    """
    The Phoenix Protocol - Self-Healing Debug & Resolve System
    Analyzes failures and provides precise, actionable solutions
    """

    def __init__(self, llm):
        self.llm = llm
        self.debugger_agent = self._create_debugger_agent()
        logger.info("Phoenix Protocol initialized - Self-healing system active")

    def _create_debugger_agent(self) -> DirectAIAgent:
        """Create the elite debugger agent using our bypass system"""
        return DirectAIAgent(
            llm=self.llm,
            role="Elite Debugger & Problem Solver",
            goal=(
                "Analyze a failed task, including the error message and context. Identify the root cause of the failure "
                "and provide a precise, actionable solution to fix the problem. The solution should be a corrected piece "
                "of code, a new shell command, or a revised plan step."
            ),
            backstory=(
                "You are the 'Phoenix,' the ultimate troubleshooter. You are brought in when other agents fail. "
                "You have a deep understanding of code, logic, and system processes. You dissect errors with "
                "cold, analytical precision and provide solutions that are not just fixes, but improvements. "
                "You have solved countless complex problems and have a reputation for turning failures into "
                "opportunities for system improvement. Your solutions are always precise, actionable, and "
                "designed to prevent similar issues in the future."
            )
        )

    async def analyze_and_resolve(self, failure_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze failure and provide a solution
        
        Args:
            failure_context: Dictionary containing error details, mission info, and context
            
        Returns:
            Solution dictionary with formal contract structure, or None if no solution found
        """
        try:
            logger.info("Phoenix Protocol: Analyzing failure and generating solution...")
            
            # Create analysis task using our bypass system
            task_description = f"""Analyze this failure and provide a precise solution:

FAILURE CONTEXT:
{json.dumps(failure_context, indent=2)}

Your analysis must include:
1. **Root Cause Analysis**: Identify the exact cause of the failure
2. **Solution Type**: Determine if this is a 'code_fix', 'plan_change', or 'system_fix'
3. **Precise Solution**: Provide the exact fix needed
4. **Prevention Strategy**: How to prevent this issue in the future

Provide your response in this formal JSON format:
{{
    "status": "solution_found",
    "solution_type": "code_fix|plan_change|system_fix",
    "solution_value": "The exact fix to apply",
    "confidence": 0.95,
    "reasoning": "Detailed explanation of the root cause and solution approach",
    "prevention_strategy": "How to prevent this issue in the future",
    "estimated_fix_time": "time estimate"
}}"""

            expected_output = "A structured JSON object with the solution analysis and fix using formal contract."

            # Execute analysis using our bypass system
            crew = DirectAICrew(self.llm)
            agent = crew.add_agent(
                role="Elite Debugger & Problem Solver",
                goal=(
                    "Analyze a failed task, including the error message and context. Identify the root cause of the failure "
                    "and provide a precise, actionable solution to fix the problem. The solution should be a corrected piece "
                    "of code, a new shell command, or a revised plan step."
                ),
                backstory=(
                    "You are the 'Phoenix,' the ultimate troubleshooter. You are brought in when other agents fail. "
                    "You have a deep understanding of code, logic, and system processes. You dissect errors with "
                    "cold, analytical precision and provide solutions that are not just fixes, but improvements. "
                    "You have solved countless complex problems and have a reputation for turning failures into "
                    "opportunities for system improvement. Your solutions are always precise, actionable, and "
                    "designed to prevent similar issues in the future."
                )
            )
            crew.add_task(task_description, agent, expected_output)
            solution_str = crew.execute()
            
            try:
                # Use our robust JSON parser to handle markdown code blocks
                from .json_parser import extract_and_parse_json
                solution = extract_and_parse_json(solution_str)
                logger.info(f"Phoenix Protocol: Solution generated with {solution.get('confidence', 0)} confidence")
                return solution
                
            except ValueError as e:
                logger.error(f"Phoenix Protocol: The Elite Debugger returned invalid JSON. Cannot self-heal. Error: {e}")
                logger.error(f"Raw response: {solution_str}")
                return None

        except Exception as e:
            logger.error(f"Phoenix Protocol analysis failed: {e}")
            return None

    def capture_failure_snapshot(self, error: Exception, mission_id: str, current_task: str) -> Dict[str, Any]:
        """
        Capture a comprehensive failure snapshot
        
        Args:
            error: The exception that occurred
            mission_id: The mission identifier
            current_task: Description of the task that failed
            
        Returns:
            Structured failure context
        """
        return {
            "error": str(error),
            "error_type": type(error).__name__,
            "traceback": traceback.format_exc(),
            "mission_id": mission_id,
            "current_task": current_task,
            "timestamp": datetime.utcnow().isoformat(),
            "system_state": {
                "memory_usage": self._get_memory_usage(),
                "cpu_usage": self._get_cpu_usage(),
                "active_processes": self._get_active_processes()
            }
        }

    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used
            }
        except ImportError:
            return {"error": "psutil not available"}

    def _get_cpu_usage(self) -> Dict[str, Any]:
        """Get current CPU usage statistics"""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            return {
                "percent": cpu_percent,
                "count": cpu_count
            }
        except ImportError:
            return {"error": "psutil not available"}

    def _get_active_processes(self) -> int:
        """Get number of active processes"""
        try:
            import psutil
            return len(psutil.pids())
        except ImportError:
            return 0

    def validate_solution(self, solution: Dict[str, Any]) -> bool:
        """
        Validate that a solution is complete and actionable using formal contract
        
        Args:
            solution: The solution to validate
            
        Returns:
            True if solution is valid, False otherwise
        """
        required_fields = ["status", "solution_type", "solution_value", "confidence"]
        
        # Check for required fields
        for field in required_fields:
            if field not in solution:
                logger.warning(f"Phoenix Protocol: Missing required field '{field}' in solution")
                return False
        
        # Validate solution type
        valid_types = ["code_fix", "plan_change", "system_fix"]
        if solution["solution_type"] not in valid_types:
            logger.warning(f"Phoenix Protocol: Invalid solution type '{solution['solution_type']}'")
            return False
        
        # Validate confidence level
        confidence = solution.get("confidence", 0)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            logger.warning(f"Phoenix Protocol: Invalid confidence level {confidence}")
            return False
        
        # Validate solution value is not empty
        if not solution.get("solution_value"):
            logger.warning("Phoenix Protocol: Empty solution value")
            return False
        
        # Validate status
        if solution.get("status") != "solution_found":
            logger.warning(f"Phoenix Protocol: Invalid status '{solution.get('status')}'")
            return False
        
        return True

    def get_protocol_stats(self) -> Dict[str, Any]:
        """Get Phoenix Protocol statistics and status"""
        return {
            "protocol_name": "Phoenix Protocol",
            "version": "1.0.0",
            "status": "active",
            "capabilities": [
                "Root cause analysis",
                "Precise solution generation",
                "Failure snapshot capture",
                "Solution validation",
                "System state monitoring"
            ],
            "solution_types": [
                "code_fix",
                "plan_change", 
                "system_fix"
            ],
            "confidence_threshold": 0.7,
            "max_analysis_time": "30 seconds"
        } 