from crewai import Task
from typing import Dict, Any, List
import json

def optimize_prompt_task(optimized_prompt: str) -> Task:
    """Task for prompt optimization"""
    return Task(
        description=f"""Analyze and optimize the following user prompt: '{optimized_prompt}'.

                Your transformation process must include:
                1. **Ambiguity Resolution**: Clarify any vague terms
                2. **Contextual Enrichment**: Add implicit technical constraints or context
                3. **Define Success Criteria**: Create a list of measurable outcomes
                4. **Recommend Agent Roles**: Suggest the primary agent roles needed for the task
                5. **Structure the Output**: Return a single, raw JSON object containing the 'optimized_prompt', 'success_criteria', and 'recommended_agents' 

                Provide your response in the following JSON format:
                {{
                    "optimized_prompt": "The enhanced, detailed version of the user's request",
                    "technical_context": {{
                        "programming_languages": ["list", "of", "relevant", "languages"],
                        "frameworks": ["list", "of", "relevant", "frameworks"],
                        "tools_required": ["list", "of", "required", "tools"],
                        "complexity_level": "low/medium/high",
                        "estimated_duration": "time estimate"
                    }},
                    "success_criteria": [
                        "Specific, measurable criteria 1",
                        "Specific, measurable criteria 2"
                    ],
                    "recommended_agents": [
                        "agent_role_1",
                        "agent_role_2"
                    ],
                    "risk_factors": [
                        "potential risk 1 with mitigation",
                        "potential risk 2 with mitigation"
                    ],
                    "optimization_notes": [
                        "optimization suggestion 1",
                        "optimization suggestion 2"
                    ]
                }}""",
        agent="prompt_optimizer"
    )

def create_execution_blueprint_task(optimized_prompt: str, technical_context: Dict[str, Any]) -> Task:
    """Task for creating comprehensive execution blueprints"""
    return Task(
        description=f"""Create a comprehensive execution blueprint for the following optimized prompt: '{optimized_prompt}'

                Technical Context: {json.dumps(technical_context, indent=2)}

                Your blueprint must include:
                1. **Mission Analysis**: Break down the request into logical phases
                2. **Task Decomposition**: Create detailed subtasks with dependencies
                3. **Agent Assignment**: Match each task to the most suitable agent
                4. **Resource Planning**: Estimate memory, CPU, and time requirements
                5. **Risk Assessment**: Identify potential failure points and mitigation strategies
                6. **Timeline Creation**: Develop realistic execution timeline
                7. **Quality Gates**: Define checkpoints for validation and review

                Provide your response in the following JSON format:
                {{
                    "mission_overview": {{
                        "title": "Mission title",
                        "description": "Mission description",
                        "complexity_level": "low/medium/high",
                        "estimated_total_duration": "time estimate",
                        "priority": "high/medium/low"
                    }},
                    "execution_phases": [
                        {{
                            "phase_id": "phase_1",
                            "phase_name": "Phase Name",
                            "description": "Phase description",
                            "estimated_duration": "time estimate",
                            "dependencies": ["previous_phase_ids"],
                            "tasks": [
                                {{
                                    "task_id": "task_1",
                                    "task_name": "Task Name",
                                    "description": "Task description",
                                    "assigned_agent": "agent_type",
                                    "estimated_duration": "time estimate",
                                    "resource_requirements": {{
                                        "memory_mb": 100,
                                        "cpu_percent": 10,
                                        "tools_required": ["tool1", "tool2"]
                                    }},
                                    "success_criteria": ["criteria1", "criteria2"],
                                    "risk_factors": ["risk1", "risk2"],
                                    "dependencies": ["previous_task_ids"]
                                }}
                            ]
                        }}
                    ],
                    "resource_allocation": {{
                        "total_estimated_memory_mb": 500,
                        "total_estimated_cpu_percent": 50,
                        "concurrent_tasks_limit": 3,
                        "memory_buffer_percent": 20
                    }},
                    "risk_mitigation": [
                        {{
                            "risk_id": "risk_1",
                            "risk_description": "Risk description",
                            "probability": "low/medium/high",
                            "impact": "low/medium/high",
                            "mitigation_strategy": "Mitigation approach"
                        }}
                    ],
                    "quality_gates": [
                        {{
                            "gate_id": "gate_1",
                            "gate_name": "Quality Gate Name",
                            "description": "Gate description",
                            "validation_criteria": ["criteria1", "criteria2"],
                            "trigger_phase": "phase_id"
                        }}
                    ],
                    "execution_strategy": {{
                        "parallel_execution": true,
                        "max_concurrent_tasks": 3,
                        "retry_policy": "exponential_backoff",
                        "timeout_handling": "graceful_degradation"
                    }}
                }}""",
        agent="planning_specialist"
    )

def validate_blueprint_task(execution_blueprint: Dict[str, Any]) -> Task:
    """Task for validating execution blueprints"""
    return Task(
        description=f"""Validate the following execution blueprint for feasibility, completeness, and optimization:

                Blueprint: {json.dumps(execution_blueprint, indent=2)}

                Your validation must include:
                1. **Feasibility Check**: Verify all tasks are achievable with available resources
                2. **Completeness Review**: Ensure all requirements are covered
                3. **Dependency Validation**: Check for circular dependencies or missing prerequisites
                4. **Resource Optimization**: Identify opportunities for better resource allocation
                5. **Risk Assessment**: Evaluate risk mitigation strategies
                6. **Timeline Validation**: Verify timeline estimates are realistic

                Provide your response in the following JSON format:
                {{
                    "validation_status": "approved/rejected/needs_revision",
                    "overall_score": 85,
                    "validation_details": {{
                        "feasibility": {{
                            "status": "pass/fail",
                            "score": 90,
                            "issues": ["issue1", "issue2"],
                            "recommendations": ["rec1", "rec2"]
                        }},
                        "completeness": {{
                            "status": "pass/fail",
                            "score": 85,
                            "missing_elements": ["element1", "element2"],
                            "recommendations": ["rec1", "rec2"]
                        }},
                        "dependencies": {{
                            "status": "pass/fail",
                            "score": 95,
                            "issues": ["issue1", "issue2"],
                            "recommendations": ["rec1", "rec2"]
                        }},
                        "resource_optimization": {{
                            "status": "pass/fail",
                            "score": 80,
                            "optimization_opportunities": ["opp1", "opp2"],
                            "recommendations": ["rec1", "rec2"]
                        }},
                        "risk_assessment": {{
                            "status": "pass/fail",
                            "score": 88,
                            "risk_level": "low/medium/high",
                            "recommendations": ["rec1", "rec2"]
                        }},
                        "timeline": {{
                            "status": "pass/fail",
                            "score": 82,
                            "timeline_issues": ["issue1", "issue2"],
                            "recommendations": ["rec1", "rec2"]
                        }}
                    }},
                    "optimization_suggestions": [
                        {{
                            "suggestion_type": "resource/timeline/dependency",
                            "description": "Suggestion description",
                            "impact": "high/medium/low",
                            "implementation_effort": "high/medium/low"
                        }}
                    ],
                    "final_recommendation": "proceed/revise/reject"
                }}""",
        agent="lead_architect"
    )

def execute_mission_task(execution_blueprint: Dict[str, Any], mission_id: str) -> Task:
    """Task for executing missions based on blueprints"""
    return Task(
        description=f"""Execute the mission based on the following validated blueprint:

                Mission ID: {mission_id}
                Blueprint: {json.dumps(execution_blueprint, indent=2)}

                Your execution must:
                1. **Follow the Blueprint**: Execute tasks according to the planned sequence
                2. **Monitor Progress**: Track task completion and resource usage
                3. **Handle Deviations**: Adapt to unexpected issues while maintaining quality
                4. **Quality Assurance**: Ensure each task meets success criteria
                5. **Resource Management**: Optimize resource usage during execution
                6. **Progress Reporting**: Provide regular status updates

                Provide your response in the following JSON format:
                {{
                    "execution_status": "in_progress/completed/failed",
                    "current_phase": "phase_id",
                    "completed_tasks": ["task_id1", "task_id2"],
                    "active_tasks": ["task_id3", "task_id4"],
                    "pending_tasks": ["task_id5", "task_id6"],
                    "resource_usage": {{
                        "current_memory_mb": 300,
                        "current_cpu_percent": 45,
                        "peak_memory_mb": 400,
                        "peak_cpu_percent": 60
                    }},
                    "execution_metrics": {{
                        "tasks_completed": 5,
                        "tasks_failed": 0,
                        "total_execution_time": "2h 30m",
                        "estimated_remaining_time": "1h 15m"
                    }},
                    "quality_gates_passed": ["gate_id1", "gate_id2"],
                    "issues_encountered": [
                        {{
                            "task_id": "task_id",
                            "issue_description": "Issue description",
                            "resolution": "Resolution applied",
                            "impact": "low/medium/high"
                        }}
                    ],
                    "final_results": {{
                        "success": true,
                        "quality_score": 92,
                        "deliverables": ["deliverable1", "deliverable2"],
                        "lessons_learned": ["lesson1", "lesson2"]
                    }}
                }}""",
        agent="lead_architect"
    ) 