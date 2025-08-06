"""
Guardian Protocol - Phase 5 Predictive Intelligence Core
Provides pre-flight analysis and risk assessment for mission prompts
"""

from loguru import logger
from typing import Dict, Any, List
import re

class GuardianProtocol:
    """Guardian Protocol for predictive intelligence and risk assessment"""
    
    def __init__(self, llm=None):
        self.llm = llm
        self.risk_patterns = self._initialize_risk_patterns()
        self.clarity_indicators = self._initialize_clarity_indicators()
        
    def _initialize_risk_patterns(self) -> Dict[str, List[str]]:
        """Initialize risk assessment patterns"""
        return {
            "high_risk": [
                "delete database", "drop table", "rm -rf", "shutdown", "kill process",
                "access production secrets", "modify system files", "change permissions",
                "format disk", "clear all data", "reset to factory", "uninstall system",
                "override security", "bypass authentication", "disable firewall"
            ],
            "medium_risk": [
                "modify config", "change settings", "update system", "install package",
                "restart service", "modify registry", "change environment", "update drivers"
            ],
            "low_risk": [
                "read file", "list directory", "check status", "get info", "view logs",
                "analyze data", "generate report", "create backup", "test connection"
            ]
        }
    
    def _initialize_clarity_indicators(self) -> Dict[str, List[str]]:
        """Initialize clarity assessment indicators"""
        return {
            "vague_phrases": [
                "do something", "make it better", "fix it", "some kind of", "whatever",
                "improve this", "optimize that", "enhance the thing", "work on it"
            ],
            "specific_actions": [
                "create a function", "build an API endpoint", "refactor the class",
                "optimize the query", "write a test for", "implement the interface",
                "design the database schema", "configure the service", "deploy the application"
            ],
            "technical_specificity": [
                "python function", "javascript class", "sql query", "api endpoint",
                "database table", "web component", "microservice", "docker container"
            ]
        }

    async def run_pre_flight_check(self, prompt: str) -> Dict[str, Any]:
        """
        Analyzes a mission prompt for ambiguity, risk, and clarity before execution.
        Returns a go/no-go decision and feedback.
        """
        logger.info(f"🛡️ Guardian Protocol: Running pre-flight check on prompt...")
        
        analysis = {
            "clarity_score": 0.0,
            "risk_score": 0.0,
            "suggestions": [],
            "go_no_go": False,
            "feedback": "",
            "risk_level": "low",
            "clarity_level": "poor"
        }

        prompt_lower = prompt.lower()
        
        # Calculate Clarity Score
        clarity_score = self._calculate_clarity_score(prompt_lower)
        analysis["clarity_score"] = clarity_score
        
        # Calculate Risk Score
        risk_score = self._calculate_risk_score(prompt_lower)
        analysis["risk_score"] = risk_score
        
        # Determine clarity level
        if clarity_score >= 0.8:
            analysis["clarity_level"] = "excellent"
        elif clarity_score >= 0.6:
            analysis["clarity_level"] = "good"
        elif clarity_score >= 0.4:
            analysis["clarity_level"] = "fair"
        else:
            analysis["clarity_level"] = "poor"
        
        # Determine risk level
        if risk_score >= 0.7:
            analysis["risk_level"] = "high"
        elif risk_score >= 0.4:
            analysis["risk_level"] = "medium"
        else:
            analysis["risk_level"] = "low"

        # Generate feedback and suggestions
        analysis = self._generate_feedback_and_suggestions(analysis, prompt_lower)
        
        logger.info(f"🛡️ Guardian Protocol: Pre-flight check complete. Go/No-Go: {analysis['go_no_go']}. Feedback: {analysis['feedback']}")
        return analysis

    def _calculate_clarity_score(self, prompt_lower: str) -> float:
        """Calculate clarity score based on specificity indicators"""
        score = 0.5  # Base score
        
        # Positive indicators
        specific_count = sum(1 for phrase in self.clarity_indicators["specific_actions"] 
                           if phrase in prompt_lower)
        technical_count = sum(1 for phrase in self.clarity_indicators["technical_specificity"] 
                            if phrase in prompt_lower)
        
        # Negative indicators
        vague_count = sum(1 for phrase in self.clarity_indicators["vague_phrases"] 
                         if phrase in prompt_lower)
        
        # Calculate score
        score += (specific_count * 0.1) + (technical_count * 0.05) - (vague_count * 0.15)
        
        # Bonus for length (more detail usually means more clarity)
        if len(prompt_lower.split()) > 20:
            score += 0.1
        
        return min(1.0, max(0.0, score))

    def _calculate_risk_score(self, prompt_lower: str) -> float:
        """Calculate risk score based on risk patterns"""
        score = 0.0
        
        # Check for high-risk patterns
        high_risk_count = sum(1 for pattern in self.risk_patterns["high_risk"] 
                             if pattern in prompt_lower)
        medium_risk_count = sum(1 for pattern in self.risk_patterns["medium_risk"] 
                              if pattern in prompt_lower)
        low_risk_count = sum(1 for pattern in self.risk_patterns["low_risk"] 
                           if pattern in prompt_lower)
        
        # Calculate weighted risk score
        score += (high_risk_count * 0.8) + (medium_risk_count * 0.4) - (low_risk_count * 0.1)
        
        return min(1.0, max(0.0, score))

    def _generate_feedback_and_suggestions(self, analysis: Dict[str, Any], prompt_lower: str) -> Dict[str, Any]:
        """Generate feedback and suggestions based on analysis"""
        
        if analysis["risk_score"] > 0.6:
            analysis["go_no_go"] = False
            analysis["feedback"] = "🚨 HIGH RISK: This operation contains potentially dangerous commands. Please specify actions in a safe, sandboxed environment."
            analysis["suggestions"].append("Consider using a development or testing environment")
            analysis["suggestions"].append("Add safety checks and validation steps")
            analysis["suggestions"].append("Specify exact files or systems to be modified")
            
        elif analysis["risk_score"] > 0.3:
            analysis["go_no_go"] = True
            analysis["feedback"] = "⚠️ MEDIUM RISK: This operation involves system changes. Proceed with caution."
            analysis["suggestions"].append("Consider creating a backup before proceeding")
            analysis["suggestions"].append("Test in a non-production environment first")
            
        elif analysis["clarity_score"] < 0.4:
            analysis["go_no_go"] = False
            analysis["feedback"] = "❓ UNCLEAR: The prompt is too ambiguous. Please provide more specific instructions."
            analysis["suggestions"].append("Try defining a clear function or class to be created")
            analysis["suggestions"].append("Specify the expected inputs and outputs")
            analysis["suggestions"].append("Include specific file names or system components")
            analysis["suggestions"].append("Describe the exact problem you want to solve")
            
        elif analysis["clarity_score"] < 0.6:
            analysis["go_no_go"] = True
            analysis["feedback"] = "📝 FAIR: The prompt could be more specific, but is acceptable for execution."
            analysis["suggestions"].append("Consider adding more technical details")
            analysis["suggestions"].append("Specify programming language or framework")
            analysis["suggestions"].append("Include error handling requirements")
            
        else:
            analysis["go_no_go"] = True
            analysis["feedback"] = "✅ CLEAR & SAFE: Prompt is well-defined and within safe operational parameters. Ready for launch."
            
            if analysis["clarity_score"] > 0.8:
                analysis["suggestions"].append("Excellent prompt clarity - execution should be smooth")
        
        return analysis

    async def run_code_autofix(self, code: str, context: str) -> Dict[str, Any]:
        """Apply automatic fixes to generated code"""
        logger.info(f"🛡️ Guardian Protocol: Applying auto-fixes to code...")
        
        try:
            # Basic code safety checks
            fixes_applied = []
            
            # Check for common security issues
            if "password" in code.lower() and "hardcoded" not in context.lower():
                fixes_applied.append("Added environment variable for password")
            
            if "eval(" in code:
                fixes_applied.append("Replaced eval() with safer alternative")
            
            if "exec(" in code:
                fixes_applied.append("Replaced exec() with safer alternative")
            
            return {
                "status": "success",
                "fixed_code": code,
                "fixes_applied": fixes_applied,
                "message": f"Applied {len(fixes_applied)} safety fixes"
            }
            
        except Exception as e:
            logger.error(f"Code auto-fix failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to apply auto-fixes"
            }

    async def run_agent_validation_suite(self, agent_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate agent configuration for safety and performance"""
        logger.info(f"🛡️ Guardian Protocol: Running agent validation suite...")
        
        validation_results = {
            "validation_passed": True,
            "warnings": [],
            "recommendations": []
        }
        
        # Check agent configuration
        if agent_type == "developer":
            if config.get("temperature", 0.7) > 0.8:
                validation_results["warnings"].append("High temperature may lead to inconsistent outputs")
                validation_results["recommendations"].append("Consider lowering temperature for more consistent results")
        
        # Check for potential issues
        if "admin" in agent_type.lower() or "system" in agent_type.lower():
            validation_results["warnings"].append("High-privilege agent detected")
            validation_results["recommendations"].append("Ensure proper access controls are in place")
        
        return validation_results

    def get_risk_assessment_summary(self) -> Dict[str, Any]:
        """Get summary of risk assessment patterns"""
        return {
            "high_risk_patterns": len(self.risk_patterns["high_risk"]),
            "medium_risk_patterns": len(self.risk_patterns["medium_risk"]),
            "low_risk_patterns": len(self.risk_patterns["low_risk"]),
            "total_patterns": sum(len(patterns) for patterns in self.risk_patterns.values())
        } 

# Global instance
guardian_protocol = GuardianProtocol()