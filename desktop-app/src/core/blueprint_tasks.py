"""
Blueprint System Tasks for Cognitive Forge Engine
Specialized tasks for prompt optimization and blueprint planning
"""

from typing import Any, Dict

from crewai import Task


class PromptOptimizationTasks:
    """Specialized tasks for prompt optimization and blueprint planning"""

    @staticmethod
    def optimize_prompt_task(user_prompt: str, mission_id: str) -> Task:
        """Task for Phase 1: Advanced Prompt Optimization"""
        return Task(
            description=(
                f"OPTIMIZE PROMPT FOR MAXIMUM CLARITY AND COMPREHENSION\n\n"
                f"Original User Request: {user_prompt}\n\n"
                f"Your mission is to transform this raw request into a perfectly optimized, "
                f"structured prompt that will be crystal clear for AI worker agents. You must:\n\n"
                f"1. ANALYZE the original request for clarity, completeness, and ambiguity\n"
                f"2. DECONSTRUCT complex requirements into clear, actionable components\n"
                f"3. IDENTIFY missing context and add necessary background information\n"
                f"4. RESTRUCTURE the prompt for optimal AI comprehension\n"
                f"5. ADD specific success criteria and measurable outcomes\n"
                f"6. DEFINE constraints, limitations, and technical requirements\n"
                f"7. ENSURE technical accuracy and completeness\n\n"
                f"Your output must be a comprehensive JSON structure containing:\n"
                f"- optimized_prompt: The enhanced, structured prompt\n"
                f"- success_criteria: Specific, measurable success indicators\n"
                f"- constraints: Technical and operational limitations\n"
                f"- context: Background information and assumptions\n"
                f"- requirements: Detailed technical requirements\n"
                f"- priority: Mission priority level (high/medium/low)\n"
                f"- complexity: Estimated complexity level\n"
                f"- estimated_duration: Expected execution time\n\n"
                f"Remember: The quality of this optimization determines the success of the entire mission. "
                f"Leave no room for ambiguity or misinterpretation."
            ),
            expected_output=(
                "A comprehensive JSON object containing the optimized prompt and all associated metadata. "
                "The structure should be clear, complete, and ready for the Blueprint Planning Specialist."
            ),
            agent="prompt_optimizer",
        )

    @staticmethod
    def create_blueprint_task(
        optimized_prompt: Dict[str, Any], mission_id: str
    ) -> Task:
        """Task for Phase 2: Blueprint Planning and Strategic Architecture"""
        return Task(
            description=(
                f"CREATE COMPREHENSIVE EXECUTION BLUEPRINT\n\n"
                f"Optimized Prompt Data: {optimized_prompt}\n\n"
                f"Your mission is to create a sophisticated, end-to-end execution blueprint that "
                f"transforms the optimized prompt into a detailed, professional roadmap. You must:\n\n"
                f"1. ANALYZE the optimized prompt and extract all requirements\n"
                f"2. DECOMPOSE the mission into manageable, sequential tasks\n"
                f"3. IDENTIFY dependencies and create critical path analysis\n"
                f"4. ALLOCATE resources and estimate timelines\n"
                f"5. ASSESS risks and create mitigation strategies\n"
                f"6. DESIGN quality assurance checkpoints\n"
                f"7. DEFINE performance metrics and success measurement\n"
                f"8. CREATE contingency plans for potential failures\n\n"
                f"Your blueprint must include:\n"
                f"- mission_overview: High-level mission description\n"
                f"- task_decomposition: Detailed breakdown of all required tasks\n"
                f"- dependencies: Task dependencies and critical path\n"
                f"- timeline: Estimated duration for each task and phase\n"
                f"- resource_allocation: Required agents, tools, and resources\n"
                f"- risk_assessment: Identified risks and mitigation strategies\n"
                f"- quality_checkpoints: Validation points throughout execution\n"
                f"- success_metrics: Measurable indicators of success\n"
                f"- contingency_plans: Backup strategies for potential issues\n"
                f"- execution_phases: Clear phases with specific objectives\n\n"
                f"Your blueprint will be the foundation for successful mission execution. "
                f"Make it comprehensive, actionable, and optimized for success."
            ),
            expected_output=(
                "A comprehensive JSON blueprint containing all execution details, timelines, "
                "dependencies, and quality assurance measures. The blueprint should be ready "
                "for immediate execution by the worker agents."
            ),
            agent="blueprint_planner",
        )


class BlueprintValidationTasks:
    """Tasks for validating and refining blueprints"""

    @staticmethod
    def validate_blueprint_task(blueprint: Dict[str, Any], mission_id: str) -> Task:
        """Task for validating the created blueprint"""
        return Task(
            description=(
                f"VALIDATE BLUEPRINT FOR FEASIBILITY AND COMPLETENESS\n\n"
                f"Blueprint Data: {blueprint}\n\n"
                f"Your mission is to critically evaluate the created blueprint for:\n\n"
                f"1. FEASIBILITY: Are all tasks realistically achievable?\n"
                f"2. COMPLETENESS: Are all requirements addressed?\n"
                f"3. LOGIC: Are dependencies and sequences logical?\n"
                f"4. RESOURCES: Are resource allocations appropriate?\n"
                f"5. TIMELINE: Are time estimates realistic?\n"
                f"6. RISKS: Are risk assessments comprehensive?\n"
                f"7. QUALITY: Are quality checkpoints sufficient?\n"
                f"8. SUCCESS: Are success metrics measurable?\n\n"
                f"Provide detailed feedback on:\n"
                f"- Strengths of the blueprint\n"
                f"- Areas that need improvement\n"
                f"- Potential issues or gaps\n"
                f"- Recommendations for enhancement\n"
                f"- Overall feasibility assessment\n\n"
                f"Your validation ensures the blueprint is ready for execution."
            ),
            expected_output=(
                "A detailed validation report with specific feedback, recommendations, "
                "and an overall assessment of blueprint quality and feasibility."
            ),
            agent="plan_validator",
        )


class BlueprintExecutionTasks:
    """Tasks for executing blueprint phases"""

    @staticmethod
    def execute_phase_task(phase_data: Dict[str, Any], mission_id: str) -> Task:
        """Task for executing a specific blueprint phase"""
        return Task(
            description=(
                f"EXECUTE BLUEPRINT PHASE\n\n"
                f"Phase Data: {phase_data}\n\n"
                f"Execute this specific phase of the blueprint with precision and attention to detail. "
                f"Follow all instructions, meet quality checkpoints, and document progress. "
                f"Report any issues or deviations from the plan immediately."
            ),
            expected_output=(
                "Detailed execution results including completed tasks, outcomes, "
                "quality checkpoint results, and any issues encountered."
            ),
            agent="senior_developer",  # This will be dynamically assigned based on phase requirements
        )
