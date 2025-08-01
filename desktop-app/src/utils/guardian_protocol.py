"""
Guardian Protocol - Proactive Quality Assurance & Auto-Fixing System
Ensures code quality and validates agent improvements
"""

import json
import re
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional
from loguru import logger
from crewai import Task, Crew, Process
from .crewai_bypass import DirectAIAgent, DirectAICrew
from pathlib import Path
import sys
import os

# Add the project root to the path to import Fix-AI
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))


class GuardianProtocol:
    """
    Guardian Protocol - Proactive Quality Assurance & Auto-Fixing System
    Implements Fix-AI integration for sentient codebase healing
    """

    def __init__(self, llm):
        self.llm = llm
        self.quality_agent = self._create_quality_agent()
        self.test_agent = self._create_test_agent()
        self.fix_ai_available = self._check_fix_ai_availability()
        logger.info("Guardian Protocol initialized - Quality assurance system active")

    def _check_fix_ai_availability(self) -> bool:
        """Check if Fix-AI is available for use"""
        try:
            fix_ai_path = project_root / "Fix-AI.py"
            return fix_ai_path.exists()
        except Exception as e:
            logger.warning(f"Fix-AI availability check failed: {e}")
            return False

    def _create_quality_agent(self) -> DirectAIAgent:
        """Create the quality assurance agent using our bypass system"""
        return DirectAIAgent(
            llm=self.llm,
            role="Quality Assurance Specialist",
            goal="Analyze code quality, identify issues, and recommend improvements",
            backstory="You are an expert in code quality and best practices. You can identify potential issues, performance problems, and architectural concerns."
        )

    def _create_test_agent(self) -> DirectAIAgent:
        """Create the testing agent using our bypass system"""
        return DirectAIAgent(
            llm=self.llm,
            role="Testing Specialist",
            goal="Create comprehensive tests and validate system functionality",
            backstory="You are a testing expert who ensures code reliability and functionality through comprehensive testing strategies."
        )

    async def run_quality_assurance(self, code_content: str, context: str = "") -> Dict[str, Any]:
        """Run quality assurance analysis on code"""
        try:
            task_description = f"""
                Analyze the following code for quality issues, potential problems, and improvement opportunities.
                
                CODE CONTEXT: {context}
                CODE CONTENT:
                ```python
                {code_content}
                ```
                
                Provide a comprehensive analysis including:
                1. Code quality assessment
                2. Potential issues or bugs
                3. Performance considerations
                4. Security concerns
                5. Best practices recommendations
                6. Overall score (1-10)
                
                Return your analysis in JSON format.
                """
            
            expected_output = "JSON analysis of code quality"

            # Use our bypass system
            crew = DirectAICrew(self.llm)
            agent = crew.add_agent(
                role="Quality Assurance Specialist",
                goal="Analyze code quality, identify issues, and recommend improvements",
                backstory="You are an expert in code quality and best practices. You can identify potential issues, performance problems, and architectural concerns."
            )
            crew.add_task(task_description, agent, expected_output)
            result = crew.execute()
            
            try:
                analysis = json.loads(result)
                return {"status": "success", "analysis": analysis}
            except json.JSONDecodeError:
                return {"status": "success", "analysis": {"raw_result": result}}

        except Exception as e:
            logger.error(f"Quality assurance failed: {e}")
            return {"status": "error", "error": str(e)}

    async def run_codebase_healing(self, trigger_reason: str = "scheduled_maintenance") -> Dict[str, Any]:
        """Run Fix-AI for sentient codebase healing"""
        if not self.fix_ai_available:
            return {
                "status": "error", 
                "error": "Fix-AI not available", 
                "message": "Fix-AI.py not found in project root"
            }

        try:
            logger.info(f"[GUARDIAN] Initiating Fix-AI codebase healing. Trigger: {trigger_reason}")
            
            # Import and run Fix-AI
            import importlib.util
            spec = importlib.util.spec_from_file_location("Fix_AI", project_root / "Fix-AI.py")
            Fix_AI = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(Fix_AI)
            CodebaseHealer = Fix_AI.CodebaseHealer
            
            healer = CodebaseHealer(project_root)
            healer.run()
            
            # Get the latest report
            reports_dir = project_root / "logs" / "fix_ai_reports"
            if reports_dir.exists():
                report_files = list(reports_dir.glob("fix_ai_report_*.json"))
                if report_files:
                    latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
                    with open(latest_report, 'r') as f:
                        report_data = json.load(f)
                    
                    return {
                        "status": "success",
                        "message": "Fix-AI codebase healing completed",
                        "report": report_data,
                        "report_file": str(latest_report)
                    }
            
            return {
                "status": "success",
                "message": "Fix-AI codebase healing completed",
                "report": "No detailed report available"
            }

        except Exception as e:
            logger.error(f"Fix-AI execution failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Fix-AI codebase healing failed"
            }

    async def validate_agent_improvements(self, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate agent configuration and improvements"""
        try:
            # Use our bypass system instead of CrewAI
            from .crewai_bypass import DirectAICrew
            
            crew = DirectAICrew(self.llm)
            agent = crew.add_agent(
                role="Agent Configuration Validator",
                goal="Validate agent configurations for issues and improvements",
                backstory="You are an expert at analyzing agent configurations for potential issues."
            )
            
            task_description = f"""
            Validate the following agent configuration for potential issues and improvements.
            
            AGENT CONFIG:
            {json.dumps(agent_config, indent=2)}
            
            Analyze for:
            1. Configuration completeness
            2. Potential conflicts
            3. Performance implications
            4. Security considerations
            5. Best practices compliance
            
            Return validation results in JSON format.
            """
            
            crew.add_task(task_description, agent, "JSON validation results")
            result = crew.execute()
            
            try:
                validation = json.loads(result)
                return {"status": "success", "validation": validation}
            except json.JSONDecodeError:
                return {"status": "success", "validation": {"raw_result": result}}

        except Exception as e:
            logger.error(f"Agent validation failed: {e}")
            return {"status": "error", "error": str(e)}

    async def run_agent_validation_suite(self, agent_role: str, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run comprehensive agent validation suite"""
        try:
            # Use our bypass system instead of CrewAI
            from .crewai_bypass import DirectAICrew
            
            crew = DirectAICrew(self.llm)
            agent = crew.add_agent(
                role="Agent Validation Specialist",
                goal="Run comprehensive validation tests on agent configurations",
                backstory="You are an expert at validating agent configurations and identifying potential issues."
            )
            
            task_description = f"""
            Run a comprehensive validation suite for the following agent:
            
            AGENT ROLE: {agent_role}
            AGENT CONFIG:
            {json.dumps(agent_config, indent=2)}
            
            Perform the following validation tests:
            1. Configuration validation
            2. Tool compatibility check
            3. Performance assessment
            4. Security audit
            5. Integration testing
            6. Error handling validation
            7. Memory usage analysis
            8. Response quality assessment
            
            Return a comprehensive validation report in JSON format with:
            - Overall validation score (1-10)
            - Passed tests list
            - Failed tests list
            - Recommendations for improvement
            - Critical issues (if any)
            """
            
            crew.add_task(task_description, agent, "JSON validation report")
            result = crew.execute()
            
            try:
                validation_report = json.loads(result)
                return {"status": "success", "validation_report": validation_report}
            except json.JSONDecodeError:
                return {"status": "success", "validation_report": {"raw_result": result}}

        except Exception as e:
            logger.error(f"Agent validation suite failed: {e}")
            return {"status": "error", "error": str(e)}

    async def run_code_autofix(self, code_content: str, context: str = "") -> Dict[str, Any]:
        """Run automatic code fixing using Fix-AI or LLM-based fixes"""
        try:
            task_description = f"""
                Analyze and automatically fix issues in the following code.
                
                CODE CONTEXT: {context}
                CODE CONTENT:
                ```python
                {code_content}
                ```
                
                Identify and fix:
                1. Syntax errors
                2. Logic issues
                3. Performance problems
                4. Security vulnerabilities
                5. Code style issues
                6. Best practices violations
                
                Return the fixed code and a summary of changes in JSON format.
                """
            
            expected_output = "JSON with fixed code and change summary"

            # Use our bypass system
            crew = DirectAICrew(self.llm)
            agent = crew.add_agent(
                role="Code Fixing Specialist",
                goal="Automatically identify and fix code issues",
                backstory="You are an expert at identifying and fixing code issues automatically. You can spot syntax errors, logic problems, and performance issues."
            )
            crew.add_task(task_description, agent, expected_output)
            result = crew.execute()
            
            try:
                analysis = json.loads(result)
                return {"status": "success", "fixed_code": analysis.get("fixed_code", code_content), "changes": analysis.get("changes", [])}
            except json.JSONDecodeError:
                return {"status": "error", "message": "Failed to parse autofix result", "raw_result": result}
        except Exception as e:
            logger.error(f"Code autofix failed: {e}")
            return {"status": "error", "message": str(e)}

    async def run_comprehensive_quality_check(self) -> Dict[str, Any]:
        """Run a comprehensive quality check including Fix-AI"""
        logger.info("[GUARDIAN] Running comprehensive quality check")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "quality_checks": {},
            "fix_ai_results": None
        }

        # Run Fix-AI codebase healing
        fix_ai_result = await self.run_codebase_healing("comprehensive_quality_check")
        results["fix_ai_results"] = fix_ai_result

        # Additional quality checks can be added here
        results["quality_checks"]["fix_ai_available"] = self.fix_ai_available
        
        logger.info("[GUARDIAN] Comprehensive quality check completed")
        return results

    def get_system_status(self) -> Dict[str, Any]:
        """Get Guardian Protocol system status"""
        return {
            "status": "active",
            "fix_ai_available": self.fix_ai_available,
            "agents": {
                "quality_agent": "active",
                "test_agent": "active"
            },
            "capabilities": [
                "quality_assurance",
                "codebase_healing",
                "agent_validation",
                "comprehensive_quality_check"
            ]
        } 