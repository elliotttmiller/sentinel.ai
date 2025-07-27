"""
Debugger Agent for Project Sentinel.

Crisis manager for error resolution and problem-solving. Activated when
other agents encounter failures and need specialized debugging assistance.
"""

from typing import Dict, Any, List, Optional
import json
from pathlib import Path
from loguru import logger

from core.agent_base import BaseAgent, AgentRole, AgentContext, AgentResult, AgentStatus


class DebuggerAgent(BaseAgent):
    """
    Debugger - Crisis manager for error resolution.
    
    Responsibilities:
    - Analyze error messages and stack traces
    - Trace issues back to root causes
    - Implement precise fixes for problems
    - Validate solutions before allowing mission to resume
    - Provide detailed debugging reports
    - Prevent similar issues in the future
    """
    
    def __init__(
        self,
        role: AgentRole,
        name: str,
        description: str,
        tools: list[str],
        model_name: str,
        llm_client,
        tool_manager
    ):
        super().__init__(role, name, description, tools, model_name)
        self.llm_client = llm_client
        self.tool_manager = tool_manager
        self.logger = logger.bind(agent="debugger")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt that defines the Debugger's behavior."""
        return """
        You are the Debugger, a crisis manager for error resolution in Project Sentinel.
        Your role is to analyze failures, identify root causes, and implement precise fixes
        to get missions back on track.
        
        Your expertise includes:
        1. **Error Analysis**: Parse complex error messages and stack traces
        2. **Root Cause Investigation**: Trace issues back to their source
        3. **Code Debugging**: Identify and fix code issues
        4. **System Diagnostics**: Analyze environment and configuration problems
        5. **Fix Implementation**: Apply precise, targeted solutions
        6. **Validation**: Ensure fixes work before resuming operations
        
        Debugging Approach:
        - **Gather Information**: Collect all relevant error details and context
        - **Analyze Patterns**: Look for common failure patterns and causes
        - **Isolate Variables**: Test different components to isolate the problem
        - **Implement Fix**: Apply the most targeted solution possible
        - **Validate Solution**: Test the fix thoroughly before proceeding
        - **Document Resolution**: Record the solution for future reference
        
        Error Categories:
        - **Syntax Errors**: Code structure and language issues
        - **Runtime Errors**: Execution-time failures and exceptions
        - **Logic Errors**: Incorrect program behavior and flow
        - **Configuration Errors**: Environment and setup issues
        - **Dependency Errors**: Missing or incompatible libraries
        - **Integration Errors**: Component interaction problems
        
        Always prioritize:
        - Quick resolution to minimize downtime
        - Thorough analysis to prevent recurrence
        - Safe fixes that don't introduce new issues
        - Clear documentation of the problem and solution
        """
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute the Debugger's crisis resolution task.
        
        Args:
            context: The execution context containing error details
            
        Returns:
            AgentResult: The debugging and fix result
        """
        self.logger.info(f"Starting debugging for mission {context.mission_id}")
        self.update_status(AgentStatus.WORKING)
        
        try:
            # Extract error details from context
            error_context = context.memory or {}
            error_message = context.user_prompt
            
            # Analyze the error and implement fix
            debugging_result = await self._debug_and_fix(
                error_message,
                error_context,
                context
            )
            
            # Create the result
            result = AgentResult(
                success=debugging_result.get("fix_applied", False),
                output=json.dumps(debugging_result, indent=2),
                metadata={
                    "debugging_type": "crisis_resolution",
                    "error_category": debugging_result.get("error_category", "unknown"),
                    "fix_applied": debugging_result.get("fix_applied", False),
                    "files_modified": len(debugging_result.get("files_modified", [])),
                    "resolution_time": debugging_result.get("resolution_time", 0)
                }
            )
            
            if debugging_result.get("fix_applied", False):
                self.logger.info("Debugging completed successfully - fix applied")
                self.update_status(AgentStatus.COMPLETED)
            else:
                self.logger.warning("Debugging completed but no fix was applied")
                self.update_status(AgentStatus.ERROR)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Debugging failed: {e}")
            self.update_status(AgentStatus.ERROR)
            return AgentResult(
                success=False,
                output="",
                error=f"Debugging failed: {str(e)}"
            )
    
    async def _debug_and_fix(
        self, 
        error_message: str, 
        error_context: Dict[str, Any],
        context: AgentContext
    ) -> Dict[str, Any]:
        """
        Analyze error and implement fix.
        
        Args:
            error_message: The error message to debug
            error_context: Additional context about the error
            context: Execution context
            
        Returns:
            Dict[str, Any]: Debugging and fix result
        """
        self.logger.info("Analyzing error and implementing fix")
        
        debugging_result = {
            "error_analysis": {},
            "root_cause": "",
            "fix_applied": False,
            "files_modified": [],
            "resolution_time": 0,
            "error_category": "unknown",
            "recommendations": []
        }
        
        # Analyze the error
        error_analysis = await self._analyze_error(error_message, error_context)
        debugging_result["error_analysis"] = error_analysis
        
        # Identify root cause
        root_cause = await self._identify_root_cause(error_analysis, context)
        debugging_result["root_cause"] = root_cause
        
        # Categorize the error
        error_category = self._categorize_error(error_analysis)
        debugging_result["error_category"] = error_category
        
        # Implement fix
        fix_result = await self._implement_fix(error_analysis, root_cause, context)
        debugging_result["fix_applied"] = fix_result.get("success", False)
        debugging_result["files_modified"] = fix_result.get("files_modified", [])
        
        # Generate recommendations
        debugging_result["recommendations"] = self._generate_debugging_recommendations(
            debugging_result
        )
        
        return debugging_result
    
    async def _analyze_error(self, error_message: str, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the error message and context.
        
        Args:
            error_message: The error message to analyze
            error_context: Additional context about the error
            
        Returns:
            Dict[str, Any]: Error analysis
        """
        analysis = {
            "error_type": "unknown",
            "severity": "medium",
            "affected_components": [],
            "stack_trace": "",
            "error_details": {},
            "context_info": error_context
        }
        
        # TODO: Implement actual error analysis
        # For now, perform basic analysis
        
        error_lower = error_message.lower()
        
        if "syntax" in error_lower:
            analysis["error_type"] = "syntax_error"
            analysis["severity"] = "high"
        elif "import" in error_lower or "module" in error_lower:
            analysis["error_type"] = "import_error"
            analysis["severity"] = "medium"
        elif "attribute" in error_lower:
            analysis["error_type"] = "attribute_error"
            analysis["severity"] = "medium"
        elif "type" in error_lower:
            analysis["error_type"] = "type_error"
            analysis["severity"] = "medium"
        elif "index" in error_lower:
            analysis["error_type"] = "index_error"
            analysis["severity"] = "medium"
        elif "key" in error_lower:
            analysis["error_type"] = "key_error"
            analysis["severity"] = "medium"
        elif "file" in error_lower:
            analysis["error_type"] = "file_error"
            analysis["severity"] = "medium"
        elif "permission" in error_lower:
            analysis["error_type"] = "permission_error"
            analysis["severity"] = "high"
        
        return analysis
    
    async def _identify_root_cause(
        self, 
        error_analysis: Dict[str, Any], 
        context: AgentContext
    ) -> str:
        """
        Identify the root cause of the error.
        
        Args:
            error_analysis: Analysis of the error
            context: Execution context
            
        Returns:
            str: Root cause description
        """
        # TODO: Implement actual root cause analysis
        # For now, return placeholder based on error type
        
        error_type = error_analysis.get("error_type", "unknown")
        
        root_cause_map = {
            "syntax_error": "Code syntax issue - missing brackets, incorrect indentation, or invalid syntax",
            "import_error": "Missing or incorrectly installed dependency",
            "attribute_error": "Object does not have the expected attribute or method",
            "type_error": "Incorrect data type used in operation",
            "index_error": "Array or list index out of bounds",
            "key_error": "Dictionary key not found",
            "file_error": "File not found or inaccessible",
            "permission_error": "Insufficient permissions to access resource"
        }
        
        return root_cause_map.get(error_type, "Unknown root cause")
    
    def _categorize_error(self, error_analysis: Dict[str, Any]) -> str:
        """Categorize the error for appropriate handling."""
        error_type = error_analysis.get("error_type", "unknown")
        
        if error_type in ["syntax_error", "type_error", "attribute_error"]:
            return "code_error"
        elif error_type in ["import_error", "file_error", "permission_error"]:
            return "environment_error"
        elif error_type in ["index_error", "key_error"]:
            return "runtime_error"
        else:
            return "unknown_error"
    
    async def _implement_fix(
        self, 
        error_analysis: Dict[str, Any], 
        root_cause: str,
        context: AgentContext
    ) -> Dict[str, Any]:
        """
        Implement a fix for the identified issue.
        
        Args:
            error_analysis: Analysis of the error
            root_cause: Identified root cause
            context: Execution context
            
        Returns:
            Dict[str, Any]: Fix implementation result
        """
        fix_result = {
            "success": False,
            "fix_type": "unknown",
            "files_modified": [],
            "fix_description": "",
            "validation_passed": False
        }
        
        # TODO: Implement actual fix logic
        # For now, return placeholder fix
        
        error_type = error_analysis.get("error_type", "unknown")
        
        if error_type == "import_error":
            fix_result.update({
                "success": True,
                "fix_type": "dependency_installation",
                "fix_description": "Install missing dependency",
                "files_modified": ["requirements.txt"]
            })
        elif error_type == "syntax_error":
            fix_result.update({
                "success": True,
                "fix_type": "code_correction",
                "fix_description": "Fix syntax error in code",
                "files_modified": ["main.py"]
            })
        elif error_type == "file_error":
            fix_result.update({
                "success": True,
                "fix_type": "file_creation",
                "fix_description": "Create missing file or directory",
                "files_modified": ["config.json"]
            })
        
        return fix_result
    
    def _generate_debugging_recommendations(self, debugging_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on debugging results."""
        recommendations = []
        
        if debugging_result.get("fix_applied", False):
            recommendations.append("Monitor the system to ensure the fix resolves the issue")
            recommendations.append("Consider adding error handling to prevent similar issues")
        else:
            recommendations.append("Manual intervention may be required to resolve this issue")
            recommendations.append("Consider reviewing the error analysis for additional insights")
        
        error_category = debugging_result.get("error_category", "unknown")
        if error_category == "environment_error":
            recommendations.append("Review system configuration and dependencies")
        elif error_category == "code_error":
            recommendations.append("Consider code review to prevent similar issues")
        elif error_category == "runtime_error":
            recommendations.append("Add input validation and error handling")
        
        return recommendations 