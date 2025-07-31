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
from crewai import Task, Crew, Process, Agent
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

    def _create_quality_agent(self) -> Agent:
        """Create the quality assurance agent"""
        return Agent(
            role="Quality Assurance Specialist",
            goal="Analyze code quality, identify issues, and recommend improvements",
            backstory="You are an expert in code quality and best practices. You can identify potential issues, performance problems, and architectural concerns.",
            llm=self.llm,
            verbose=True
        )

    def _create_test_agent(self) -> Agent:
        """Create the testing agent"""
        return Agent(
            role="Testing Specialist",
            goal="Create comprehensive tests and validate system functionality",
            backstory="You are a testing expert who ensures code reliability and functionality through comprehensive testing strategies.",
            llm=self.llm,
            verbose=True
        )

    async def run_quality_assurance(self, code_content: str, context: str = "") -> Dict[str, Any]:
        """Run quality assurance analysis on code"""
        try:
            quality_task = Task(
                description=f"""
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
                """,
                expected_output="JSON analysis of code quality",
                agent=self.quality_agent
            )

            crew = Crew(agents=[self.quality_agent], tasks=[quality_task], process=Process.sequential)
            result = crew.kickoff()
            
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
            test_task = Task(
                description=f"""
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
                """,
                expected_output="JSON validation results",
                agent=self.test_agent
            )

            crew = Crew(agents=[self.test_agent], tasks=[test_task], process=Process.sequential)
            result = crew.kickoff()
            
            try:
                validation = json.loads(result)
                return {"status": "success", "validation": validation}
            except json.JSONDecodeError:
                return {"status": "success", "validation": {"raw_result": result}}

        except Exception as e:
            logger.error(f"Agent validation failed: {e}")
            return {"status": "error", "error": str(e)}

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