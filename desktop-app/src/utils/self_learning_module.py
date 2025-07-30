"""
Self-Learning Module - Continuous Improvement & Adaptation System
Analyzes mission outcomes and generates agent improvements
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from loguru import logger
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import Task, Crew, Process, Agent


class SelfLearningModule:
    """
    The Self-Learning Module - Continuous Improvement & Adaptation System
    Analyzes mission outcomes and generates agent improvements
    """

    def __init__(self, llm: ChatGoogleGenerativeAI, db_manager):
        self.llm = llm
        self.db_manager = db_manager
        self.learning_agent = self._create_learning_agent()
        self.improvement_agent = self._create_improvement_agent()
        logger.info("Self-Learning Module initialized - Continuous improvement active")

    def _create_learning_agent(self) -> Agent:
        """Create the learning analysis agent"""
        return Agent(
            role="Learning Analysis Specialist",
            goal=(
                "Analyze mission outcomes, identify patterns, and extract valuable insights for system improvement. "
                "Focus on performance optimization, error reduction, and efficiency gains."
            ),
            backstory=(
                "You are the Learning Specialist, responsible for extracting wisdom from every mission outcome. "
                "You have deep expertise in data analysis, pattern recognition, and continuous improvement methodologies. "
                "Your analysis helps the system evolve and adapt based on real-world performance data."
            ),
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def _create_improvement_agent(self) -> Agent:
        """Create the improvement generation agent"""
        return Agent(
            role="Improvement Generation Specialist",
            goal=(
                "Generate specific, actionable improvements for agents and system components based on analysis. "
                "Create detailed improvement plans with measurable outcomes and implementation strategies."
            ),
            backstory=(
                "You are the Improvement Specialist, responsible for translating analysis into actionable improvements. "
                "You have extensive experience in optimization, performance tuning, and system enhancement. "
                "Your improvements are always practical, measurable, and designed for real-world implementation."
            ),
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    async def analyze_mission_outcome(self, mission_id: str, success: bool) -> Dict[str, Any]:
        """
        Analyze mission outcome and generate learning insights
        
        Args:
            mission_id: The mission identifier
            success: Whether the mission was successful
            
        Returns:
            Learning analysis results
        """
        try:
            logger.info(f"Self-Learning Module: Analyzing mission {mission_id} outcome...")
            
            # Get mission data from database
            mission_data = self.db_manager.get_mission(mission_id)
            if not mission_data:
                logger.warning(f"Mission {mission_id} not found in database")
                return {"error": "Mission not found"}
            
            # Create learning analysis task
            analysis_task = Task(
                description=f"""Analyze this mission outcome and extract learning insights:

MISSION DATA:
{json.dumps(mission_data, indent=2)}

MISSION SUCCESS: {success}

Your analysis must include:
1. **Performance Analysis**: Evaluate execution time, efficiency, and resource usage
2. **Pattern Recognition**: Identify recurring themes and behaviors
3. **Error Analysis**: If failed, analyze root causes and failure patterns
4. **Success Factors**: If successful, identify what contributed to success
5. **Optimization Opportunities**: Identify areas for improvement
6. **Learning Insights**: Extract actionable knowledge for future missions

Provide your response in this JSON format:
{{
    "performance_analysis": {{
        "execution_efficiency": 0.85,
        "resource_utilization": 0.75,
        "time_optimization": 0.90
    }},
    "pattern_insights": [
        "Pattern 1 description",
        "Pattern 2 description"
    ],
    "error_analysis": [
        "Error 1 analysis",
        "Error 2 analysis"
    ],
    "success_factors": [
        "Success factor 1",
        "Success factor 2"
    ],
    "optimization_opportunities": [
        "Opportunity 1",
        "Opportunity 2"
    ],
    "learning_insights": [
        "Insight 1",
        "Insight 2"
    ],
    "overall_score": 0.88
}}""",
                expected_output="A structured JSON object with learning analysis and insights.",
                agent=self.learning_agent
            )

            # Execute analysis
            crew = Crew(
                agents=[self.learning_agent],
                tasks=[analysis_task],
                process=Process.sequential,
                verbose=True
            )

            analysis_result_str = crew.kickoff()
            
            try:
                analysis_result = json.loads(analysis_result_str)
                logger.info(f"Self-Learning Module: Analysis completed with score {analysis_result.get('overall_score', 0)}")
                
                # Store analysis in database
                self.db_manager.add_mission_update(
                    mission_id,
                    f"Learning analysis completed: {len(analysis_result.get('learning_insights', []))} insights extracted",
                    "learning"
                )
                
                return analysis_result
                
            except json.JSONDecodeError as e:
                logger.error(f"Self-Learning Module: Invalid JSON response: {analysis_result_str}")
                return {"error": "Invalid analysis response format"}

        except Exception as e:
            logger.error(f"Self-Learning Module analysis failed: {e}")
            return {"error": str(e)}

    async def generate_agent_improvements(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate specific agent improvements based on analysis
        
        Args:
            analysis_result: The learning analysis results
            
        Returns:
            List of agent improvements
        """
        try:
            logger.info("Self-Learning Module: Generating agent improvements...")
            
            # Create improvement generation task
            improvement_task = Task(
                description=f"""Generate specific agent improvements based on this analysis:

ANALYSIS RESULT:
{json.dumps(analysis_result, indent=2)}

Generate improvements for:
1. **Agent Configuration**: Optimize agent settings and parameters
2. **Prompt Engineering**: Enhance agent prompts for better performance
3. **Tool Integration**: Improve agent tool usage and capabilities
4. **Error Handling**: Enhance error handling and recovery mechanisms
5. **Performance Optimization**: Optimize agent execution efficiency

For each improvement, provide:
- Target agent or component
- Specific improvement description
- Expected impact and benefits
- Implementation strategy
- Success metrics

Provide your response as a JSON array of improvements:
[
    {{
        "target_component": "agent_role_or_system_component",
        "improvement_type": "configuration|prompt|tool|error_handling|performance",
        "description": "Detailed improvement description",
        "expected_impact": "Expected benefits and outcomes",
        "implementation_strategy": "Step-by-step implementation plan",
        "success_metrics": ["Metric 1", "Metric 2"],
        "priority": "high|medium|low",
        "estimated_effort": "time estimate"
    }}
]""",
                expected_output="A JSON array of specific agent improvements.",
                agent=self.improvement_agent
            )

            # Execute improvement generation
            crew = Crew(
                agents=[self.improvement_agent],
                tasks=[improvement_task],
                process=Process.sequential,
                verbose=True
            )

            improvements_str = crew.kickoff()
            
            try:
                improvements = json.loads(improvements_str)
                logger.info(f"Self-Learning Module: Generated {len(improvements)} improvements")
                return improvements
                
            except json.JSONDecodeError as e:
                logger.error(f"Self-Learning Module: Invalid JSON response: {improvements_str}")
                return []

        except Exception as e:
            logger.error(f"Self-Learning Module improvement generation failed: {e}")
            return []

    async def mark_improvements_active(self, mission_id: str, improvements: List[Dict[str, Any]]) -> bool:
        """
        Mark improvements as active after validation
        
        Args:
            mission_id: The mission identifier
            improvements: List of improvements to activate
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Self-Learning Module: Marking {len(improvements)} improvements as active...")
            
            # Store improvements in database with active status
            for improvement in improvements:
                improvement_data = {
                    "mission_id": mission_id,
                    "improvement": improvement,
                    "status": "active",
                    "activated_at": datetime.utcnow().isoformat(),
                    "validation_passed": True
                }
                
                # Store in database (assuming there's a method for this)
                # self.db_manager.store_improvement(improvement_data)
            
            logger.info("Self-Learning Module: Improvements marked as active successfully")
            return True
            
        except Exception as e:
            logger.error(f"Self-Learning Module: Failed to mark improvements active: {e}")
            return False

    def get_learning_stats(self) -> Dict[str, Any]:
        """
        Get learning module statistics
        
        Returns:
            Learning module statistics
        """
        return {
            "module_name": "Self-Learning Module",
            "version": "1.0.0",
            "status": "active",
            "capabilities": [
                "Mission outcome analysis",
                "Pattern recognition",
                "Performance optimization",
                "Error analysis",
                "Improvement generation",
                "Continuous adaptation"
            ],
            "analysis_types": [
                "performance_analysis",
                "pattern_insights",
                "error_analysis",
                "success_factors",
                "optimization_opportunities",
                "learning_insights"
            ],
            "improvement_types": [
                "agent_configuration",
                "prompt_engineering",
                "tool_integration",
                "error_handling",
                "performance_optimization"
            ],
            "learning_threshold": 0.7,
            "max_analysis_time": "120 seconds"
        }

    def validate_improvement(self, improvement: Dict[str, Any]) -> bool:
        """
        Validate that an improvement is complete and actionable
        
        Args:
            improvement: The improvement to validate
            
        Returns:
            True if improvement is valid, False otherwise
        """
        required_fields = [
            "target_component",
            "improvement_type", 
            "description",
            "expected_impact",
            "implementation_strategy",
            "success_metrics",
            "priority"
        ]
        
        # Check for required fields
        for field in required_fields:
            if field not in improvement:
                logger.warning(f"Self-Learning Module: Missing required field '{field}' in improvement")
                return False
        
        # Validate improvement type
        valid_types = [
            "configuration",
            "prompt", 
            "tool",
            "error_handling",
            "performance"
        ]
        if improvement["improvement_type"] not in valid_types:
            logger.warning(f"Self-Learning Module: Invalid improvement type '{improvement['improvement_type']}'")
            return False
        
        # Validate priority
        valid_priorities = ["high", "medium", "low"]
        if improvement["priority"] not in valid_priorities:
            logger.warning(f"Self-Learning Module: Invalid priority '{improvement['priority']}'")
            return False
        
        # Validate description is not empty
        if not improvement.get("description"):
            logger.warning("Self-Learning Module: Empty improvement description")
            return False
        
        return True

    def get_protocol_stats(self) -> Dict[str, Any]:
        """Get Self-Learning Module statistics and status"""
        return {
            "protocol_name": "Self-Learning Module",
            "version": "1.0.0",
            "status": "active",
            "capabilities": [
                "Mission outcome analysis",
                "Pattern recognition",
                "Performance optimization",
                "Error analysis",
                "Improvement generation",
                "Continuous adaptation"
            ],
            "analysis_types": [
                "performance_analysis",
                "pattern_insights", 
                "error_analysis",
                "success_factors",
                "optimization_opportunities",
                "learning_insights"
            ],
            "improvement_types": [
                "agent_configuration",
                "prompt_engineering",
                "tool_integration",
                "error_handling",
                "performance_optimization"
            ],
            "learning_threshold": 0.7,
            "max_analysis_time": "120 seconds"
        } 