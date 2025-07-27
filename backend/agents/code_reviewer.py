"""
Code Reviewer Agent for Project Sentinel.

Quality gatekeeper that analyzes code for issues, best practices,
and potential improvements. Acts as a second pair of eyes to prevent
flawed code from progressing.
"""

from typing import Dict, Any, List, Optional
import json
from pathlib import Path
from loguru import logger

from core.agent_base import BaseAgent, AgentRole, AgentContext, AgentResult, AgentStatus


class CodeReviewerAgent(BaseAgent):
    """
    Code Reviewer - Quality gatekeeper and code analyzer.
    
    Responsibilities:
    - Analyze code for logical errors and bugs
    - Check for style guide violations
    - Identify potential security vulnerabilities
    - Review code structure and architecture
    - Suggest improvements and optimizations
    - Ensure best practices are followed
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
        self.logger = logger.bind(agent="code_reviewer")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt that defines the Code Reviewer's behavior."""
        return """
        You are the Code Reviewer, a quality gatekeeper for Project Sentinel.
        Your role is to meticulously analyze code written by the Developer Agent
        and provide comprehensive feedback to ensure high-quality, maintainable code.
        
        Your expertise includes:
        1. **Code Quality Analysis**: Identify logical errors, bugs, and issues
        2. **Style Guide Compliance**: Check for coding standards and conventions
        3. **Security Review**: Identify potential security vulnerabilities
        4. **Performance Analysis**: Suggest optimizations and improvements
        5. **Architecture Review**: Evaluate code structure and design patterns
        6. **Best Practices**: Ensure industry standards are followed
        
        Review Criteria:
        - **Functionality**: Does the code work as intended?
        - **Readability**: Is the code clear and well-documented?
        - **Maintainability**: Is the code easy to modify and extend?
        - **Performance**: Are there efficiency concerns?
        - **Security**: Are there potential vulnerabilities?
        - **Testing**: Is the code testable and tested?
        
        Code Review Principles:
        - Be constructive and helpful in feedback
        - Focus on the code, not the developer
        - Provide specific, actionable suggestions
        - Consider the broader context and requirements
        - Balance perfection with practicality
        - Prioritize critical issues over minor style points
        
        Always provide clear, specific feedback that helps improve
        the code quality and maintainability.
        """
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute the Code Reviewer's analysis task.
        
        Args:
            context: The execution context containing the code to review
            
        Returns:
            AgentResult: The code review result
        """
        self.logger.info(f"Starting code review for mission {context.mission_id}")
        self.update_status(AgentStatus.WORKING)
        
        try:
            # Extract review details from context
            review_target = context.user_prompt
            
            # Analyze the codebase for review
            codebase_files = await self._identify_files_to_review(context.workspace_path)
            
            # Perform comprehensive code review
            review_result = await self._perform_code_review(
                codebase_files,
                review_target,
                context
            )
            
            # Create the result
            result = AgentResult(
                success=True,
                output=json.dumps(review_result, indent=2),
                metadata={
                    "review_type": "comprehensive_code_review",
                    "files_reviewed": len(review_result.get("files_reviewed", [])),
                    "issues_found": len(review_result.get("issues", [])),
                    "suggestions_made": len(review_result.get("suggestions", [])),
                    "overall_quality_score": review_result.get("quality_score", 0)
                }
            )
            
            self.logger.info("Code review completed successfully")
            self.update_status(AgentStatus.COMPLETED)
            return result
            
        except Exception as e:
            self.logger.error(f"Code review failed: {e}")
            self.update_status(AgentStatus.ERROR)
            return AgentResult(
                success=False,
                output="",
                error=f"Code review failed: {str(e)}"
            )
    
    async def _identify_files_to_review(self, workspace_path: Path) -> List[Path]:
        """
        Identify files that need to be reviewed.
        
        Args:
            workspace_path: Path to the workspace
            
        Returns:
            List[Path]: Files to review
        """
        self.logger.info("Identifying files for code review")
        
        files_to_review = []
        
        try:
            # Look for recently modified files or new files
            for file_path in workspace_path.rglob("*"):
                if file_path.is_file() and self._is_code_file(file_path):
                    # TODO: Implement logic to identify recently modified files
                    # For now, review all code files
                    files_to_review.append(file_path)
            
        except Exception as e:
            self.logger.warning(f"Error identifying files to review: {e}")
        
        return files_to_review
    
    def _is_code_file(self, file_path: Path) -> bool:
        """Check if a file is a code file that should be reviewed."""
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.cs',
            '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala'
        }
        return file_path.suffix.lower() in code_extensions
    
    async def _perform_code_review(
        self, 
        files_to_review: List[Path], 
        review_target: str,
        context: AgentContext
    ) -> Dict[str, Any]:
        """
        Perform comprehensive code review.
        
        Args:
            files_to_review: List of files to review
            review_target: Specific focus of the review
            context: Execution context
            
        Returns:
            Dict[str, Any]: Code review result
        """
        self.logger.info(f"Performing code review on {len(files_to_review)} files")
        
        review_result = {
            "files_reviewed": [],
            "issues": [],
            "suggestions": [],
            "quality_score": 0,
            "summary": "",
            "recommendations": []
        }
        
        total_issues = 0
        total_suggestions = 0
        
        for file_path in files_to_review:
            try:
                file_review = await self._review_single_file(file_path, review_target)
                review_result["files_reviewed"].append(file_review)
                
                total_issues += len(file_review.get("issues", []))
                total_suggestions += len(file_review.get("suggestions", []))
                
            except Exception as e:
                self.logger.warning(f"Error reviewing file {file_path}: {e}")
        
        # Aggregate issues and suggestions
        review_result["issues"] = self._aggregate_issues(review_result["files_reviewed"])
        review_result["suggestions"] = self._aggregate_suggestions(review_result["files_reviewed"])
        
        # Calculate quality score
        review_result["quality_score"] = self._calculate_quality_score(
            total_issues, 
            total_suggestions, 
            len(files_to_review)
        )
        
        # Generate summary and recommendations
        review_result["summary"] = self._generate_review_summary(review_result)
        review_result["recommendations"] = self._generate_recommendations(review_result)
        
        return review_result
    
    async def _review_single_file(self, file_path: Path, review_target: str) -> Dict[str, Any]:
        """
        Review a single file for issues and improvements.
        
        Args:
            file_path: Path to the file to review
            review_target: Specific focus of the review
            
        Returns:
            Dict[str, Any]: File review result
        """
        file_review = {
            "file_path": str(file_path),
            "language": self._detect_language(file_path),
            "issues": [],
            "suggestions": [],
            "quality_metrics": {}
        }
        
        try:
            # Read file content
            content = file_path.read_text(encoding='utf-8')
            
            # Perform various analyses
            file_review["issues"] = await self._analyze_issues(content, file_path)
            file_review["suggestions"] = await self._analyze_suggestions(content, file_path)
            file_review["quality_metrics"] = await self._calculate_metrics(content, file_path)
            
        except Exception as e:
            file_review["issues"].append({
                "type": "error",
                "severity": "high",
                "message": f"Could not read file: {e}",
                "line": 0
            })
        
        return file_review
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect the programming language of a file."""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala'
        }
        return extension_map.get(file_path.suffix.lower(), 'unknown')
    
    async def _analyze_issues(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """
        Analyze code content for issues.
        
        Args:
            content: File content to analyze
            file_path: Path to the file
            
        Returns:
            List[Dict[str, Any]]: List of issues found
        """
        issues = []
        
        # TODO: Implement actual code analysis
        # For now, return placeholder issues
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Simple checks for demonstration
            if 'TODO' in line:
                issues.append({
                    "type": "todo",
                    "severity": "low",
                    "message": "TODO comment found - should be addressed",
                    "line": i,
                    "suggestion": "Complete the TODO or remove if no longer needed"
                })
            
            if len(line) > 120:
                issues.append({
                    "type": "style",
                    "severity": "medium",
                    "message": "Line too long",
                    "line": i,
                    "suggestion": "Break long line into multiple lines"
                })
        
        return issues
    
    async def _analyze_suggestions(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """
        Analyze code content for improvement suggestions.
        
        Args:
            content: File content to analyze
            file_path: Path to the file
            
        Returns:
            List[Dict[str, Any]]: List of suggestions
        """
        suggestions = []
        
        # TODO: Implement actual suggestion analysis
        # For now, return placeholder suggestions
        
        if 'print(' in content:
            suggestions.append({
                "type": "logging",
                "message": "Consider using proper logging instead of print statements",
                "priority": "medium"
            })
        
        if 'except:' in content:
            suggestions.append({
                "type": "error_handling",
                "message": "Consider specifying exception types instead of bare except",
                "priority": "high"
            })
        
        return suggestions
    
    async def _calculate_metrics(self, content: str, file_path: Path) -> Dict[str, Any]:
        """
        Calculate quality metrics for the code.
        
        Args:
            content: File content to analyze
            file_path: Path to the file
            
        Returns:
            Dict[str, Any]: Quality metrics
        """
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        return {
            "total_lines": len(lines),
            "code_lines": len(non_empty_lines),
            "comment_ratio": 0.1,  # TODO: Calculate actual ratio
            "complexity": "low",  # TODO: Calculate actual complexity
            "maintainability_index": 85  # TODO: Calculate actual index
        }
    
    def _aggregate_issues(self, file_reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aggregate issues from all file reviews."""
        all_issues = []
        for review in file_reviews:
            all_issues.extend(review.get("issues", []))
        return all_issues
    
    def _aggregate_suggestions(self, file_reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aggregate suggestions from all file reviews."""
        all_suggestions = []
        for review in file_reviews:
            all_suggestions.extend(review.get("suggestions", []))
        return all_suggestions
    
    def _calculate_quality_score(self, total_issues: int, total_suggestions: int, file_count: int) -> int:
        """Calculate overall quality score."""
        if file_count == 0:
            return 100
        
        # Simple scoring algorithm
        base_score = 100
        issue_penalty = total_issues * 5
        suggestion_bonus = min(total_suggestions * 2, 20)
        
        score = base_score - issue_penalty + suggestion_bonus
        return max(0, min(100, score))
    
    def _generate_review_summary(self, review_result: Dict[str, Any]) -> str:
        """Generate a summary of the code review."""
        files_count = len(review_result["files_reviewed"])
        issues_count = len(review_result["issues"])
        suggestions_count = len(review_result["suggestions"])
        quality_score = review_result["quality_score"]
        
        return f"""
        Code Review Summary:
        - Files reviewed: {files_count}
        - Issues found: {issues_count}
        - Suggestions made: {suggestions_count}
        - Quality score: {quality_score}/100
        
        Overall assessment: {'Good' if quality_score >= 80 else 'Needs improvement' if quality_score >= 60 else 'Poor'}
        """
    
    def _generate_recommendations(self, review_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on the review."""
        recommendations = []
        
        if len(review_result["issues"]) > 0:
            recommendations.append("Address all identified issues before proceeding")
        
        if len(review_result["suggestions"]) > 0:
            recommendations.append("Consider implementing the suggested improvements")
        
        if review_result["quality_score"] < 80:
            recommendations.append("Consider additional code review and refactoring")
        
        return recommendations 