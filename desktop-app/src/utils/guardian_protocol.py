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


class GuardianProtocol:
    """
    The Guardian Protocol - Proactive Quality Assurance & Auto-Fixing System
    Validates code quality and agent improvements with automated fixes
    """

    def __init__(self, llm):
        self.llm = llm
        self.quality_agent = self._create_quality_agent()
        self.test_agent = self._create_test_agent()
        logger.info("Guardian Protocol initialized - Quality assurance system active")

    def _create_quality_agent(self) -> Agent:
        """Create the quality assurance agent"""
        return Agent(
            role="Code Quality Guardian & Auto-Fix Specialist",
            goal=(
                "Analyze code for quality issues, security vulnerabilities, and performance problems. "
                "Provide automated fixes and improvements while maintaining code functionality. "
                "Ensure all code meets production standards."
            ),
            backstory=(
                "You are the Guardian, a master of code quality and automated improvement. "
                "You have deep expertise in static analysis, security auditing, and performance optimization. "
                "Your role is to ensure that all code meets the highest standards before it reaches production. "
                "You can automatically fix common issues while preserving functionality and improving code quality."
            ),
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def _create_test_agent(self) -> Agent:
        """Create the testing and validation agent"""
        return Agent(
            role="Test Strategy Guardian & Validation Specialist",
            goal=(
                "Design comprehensive test strategies and validate agent improvements. "
                "Create test cases, execute validation suites, and ensure all improvements meet quality standards. "
                "Provide detailed validation reports with actionable feedback."
            ),
            backstory=(
                "You are the Test Guardian, responsible for ensuring that all system improvements are thoroughly validated. "
                "You have extensive experience in test automation, quality assurance, and validation methodologies. "
                "Your validation ensures that improvements enhance system performance without introducing regressions."
            ),
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    async def run_code_autofix(self, code_content: str) -> str:
        """
        Analyze code and apply automatic fixes
        
        Args:
            code_content: The code to analyze and fix
            
        Returns:
            Improved code with fixes applied
        """
        try:
            logger.info("Guardian Protocol: Running code auto-fix analysis...")
            
            # Create auto-fix task
            autofix_task = Task(
                description=f"""Analyze and improve this code:

CODE TO ANALYZE:
```python
{code_content}
```

Your analysis must include:
1. **Code Quality Issues**: Identify style, structure, and best practice violations
2. **Security Vulnerabilities**: Check for potential security issues
3. **Performance Optimizations**: Identify performance improvements
4. **Automated Fixes**: Apply fixes automatically where safe
5. **Documentation**: Add or improve comments and docstrings

Provide your response as the improved code with fixes applied. 
Include a brief summary of changes made at the top as a comment.

Focus on:
- PEP 8 compliance
- Error handling improvements
- Security best practices
- Performance optimizations
- Code readability and maintainability""",
                expected_output="Improved code with fixes applied and change summary.",
                agent=self.quality_agent
            )

            # Execute auto-fix
            crew = Crew(
                agents=[self.quality_agent],
                tasks=[autofix_task],
                process=Process.sequential,
                verbose=True
            )

            improved_code = crew.kickoff()
            
            # Extract the code from the response (remove any markdown formatting)
            cleaned_code = self._extract_code_from_response(improved_code)
            
            logger.info("Guardian Protocol: Code auto-fix completed successfully")
            return cleaned_code

        except Exception as e:
            logger.error(f"Guardian Protocol auto-fix failed: {e}")
            return code_content  # Return original code if fix fails

    async def run_agent_validation_suite(self, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate agent configuration and improvements
        
        Args:
            agent_config: The agent configuration to validate
            
        Returns:
            Validation results with detailed feedback
        """
        try:
            logger.info("Guardian Protocol: Running agent validation suite...")
            
            # Create validation task
            validation_task = Task(
                description=f"""Validate this agent configuration:

AGENT CONFIGURATION:
{json.dumps(agent_config, indent=2)}

Your validation must include:
1. **Configuration Completeness**: Check if all required fields are present
2. **Agent Role Validation**: Verify agent roles are appropriate and well-defined
3. **Performance Assessment**: Evaluate expected performance characteristics
4. **Integration Compatibility**: Check compatibility with existing system
5. **Risk Assessment**: Identify potential issues or conflicts
6. **Improvement Suggestions**: Provide specific recommendations

Provide your response in this JSON format:
{{
    "validation_passed": true/false,
    "completeness_score": 0.95,
    "performance_score": 0.90,
    "compatibility_score": 0.85,
    "risk_level": "low/medium/high",
    "issues_found": [
        "Issue 1 description",
        "Issue 2 description"
    ],
    "recommendations": [
        "Recommendation 1",
        "Recommendation 2"
    ],
    "overall_score": 0.92
}}""",
                expected_output="A structured JSON object with validation results and recommendations.",
                agent=self.test_agent
            )

            # Execute validation
            crew = Crew(
                agents=[self.test_agent],
                tasks=[validation_task],
                process=Process.sequential,
                verbose=True
            )

            validation_result_str = crew.kickoff()
            
            try:
                validation_result = json.loads(validation_result_str)
                logger.info(f"Guardian Protocol: Validation completed with score {validation_result.get('overall_score', 0)}")
                return validation_result
                
            except json.JSONDecodeError as e:
                logger.error(f"Guardian Protocol: Invalid JSON response: {validation_result_str}")
                return {
                    "validation_passed": False,
                    "error": "Invalid validation response format",
                    "overall_score": 0.0
                }

        except Exception as e:
            logger.error(f"Guardian Protocol validation failed: {e}")
            return {
                "validation_passed": False,
                "error": str(e),
                "overall_score": 0.0
            }

    def _extract_code_from_response(self, response: str) -> str:
        """Extract code from agent response, removing markdown formatting"""
        # Remove markdown code blocks
        code_pattern = r"```(?:python)?\n?(.*?)\n?```"
        matches = re.findall(code_pattern, response, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # If no code blocks found, return the response as-is
        return response.strip()

    def validate_code_syntax(self, code_content: str) -> Dict[str, Any]:
        """
        Validate Python code syntax
        
        Args:
            code_content: The code to validate
            
        Returns:
            Validation results
        """
        try:
            # Write code to temporary file
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code_content)
                temp_file = f.name
            
            try:
                # Run syntax check
                result = subprocess.run(
                    ['python', '-m', 'py_compile', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    return {
                        "syntax_valid": True,
                        "errors": [],
                        "warnings": []
                    }
                else:
                    return {
                        "syntax_valid": False,
                        "errors": result.stderr.split('\n') if result.stderr else [],
                        "warnings": []
                    }
                    
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    
        except Exception as e:
            return {
                "syntax_valid": False,
                "errors": [str(e)],
                "warnings": []
            }

    def check_security_vulnerabilities(self, code_content: str) -> List[str]:
        """
        Check for common security vulnerabilities
        
        Args:
            code_content: The code to check
            
        Returns:
            List of security issues found
        """
        vulnerabilities = []
        
        # Check for common security issues
        security_patterns = {
            "SQL Injection": r"execute\(.*\+.*\)",
            "Command Injection": r"os\.system\(.*\+.*\)",
            "Path Traversal": r"open\(.*\.\./",
            "Hardcoded Credentials": r"password\s*=\s*['\"][^'\"]+['\"]",
            "Unsafe Deserialization": r"pickle\.loads\(",
            "Weak Random": r"random\.randint\(",
        }
        
        for issue_name, pattern in security_patterns.items():
            if re.search(pattern, code_content, re.IGNORECASE):
                vulnerabilities.append(f"{issue_name}: Potential security vulnerability detected")
        
        return vulnerabilities

    def get_protocol_stats(self) -> Dict[str, Any]:
        """Get Guardian Protocol statistics and status"""
        return {
            "protocol_name": "Guardian Protocol",
            "version": "1.0.0",
            "status": "active",
            "capabilities": [
                "Code quality analysis",
                "Automated code fixes",
                "Security vulnerability detection",
                "Agent validation",
                "Performance optimization",
                "Syntax validation"
            ],
            "validation_types": [
                "code_quality",
                "security_audit",
                "performance_analysis",
                "agent_configuration",
                "integration_compatibility"
            ],
            "auto_fix_capabilities": [
                "PEP 8 compliance",
                "Error handling improvements",
                "Security best practices",
                "Performance optimizations",
                "Documentation enhancement"
            ],
            "quality_threshold": 0.8,
            "max_validation_time": "60 seconds"
        } 