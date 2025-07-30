"""
Cognitive Forge Engine - The Core AI Orchestration System
Implements advanced multi-agent workflows with memory, learning, and observability
"""

import json
import time
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from crewai import Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from loguru import logger
from dotenv import load_dotenv

from ..agents.advanced_agents import PlannerAgents, WorkerAgents, MemoryAgents
from ..models.advanced_database import db_manager
from ..tools.advanced_tools import SystemTools

# Load environment variables
load_dotenv()


class CognitiveForgeEngine:
    """
    The main engine for Project Sentinel, implementing the Cognitive Forge architecture.
    This class handles mission planning, crew assembly, execution, and observability.
    """

    def __init__(self):
        # Initialize LLM with environment configuration
        model_name = os.getenv("LLM_MODEL", "gemini-1.5-pro-latest")
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))

        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)

        # Initialize agent factories
        self.planner_agents = PlannerAgents()
        self.worker_agents = WorkerAgents()
        self.memory_agents = MemoryAgents()

        # Initialize database manager
        self.db_manager = db_manager

        logger.info(f"Cognitive Forge Engine initialized with model: {model_name}")

    def run_mission(
        self,
        user_prompt: str,
        mission_id_str: str,
        agent_type: str,
        update_callback: Callable[[str], None],
    ) -> Dict[str, Any]:
        """
        The main entry point for running a complete mission from planning to execution.
        Implements the full Cognitive Forge workflow with memory and learning.
        """
        start_time = time.time()

        try:
            # Update mission status to planning
            self.db_manager.update_mission_status(mission_id_str, "planning")
            update_callback("🚀 Phase 1: Orchestration - Engaging Planning Crew...")

            # Phase 1: Planning with Memory Integration
            plan = self._generate_execution_plan(user_prompt, mission_id_str, update_callback)

            # Store the plan in database
            self.db_manager.update_mission_status(mission_id_str, "planning", plan=plan)

            # Phase 2: Crew Assembly & Execution
            update_callback("⚡ Phase 2: Execution - Assembling and deploying Worker Crew...")
            worker_result = self._execute_worker_crew(plan, mission_id_str, update_callback)

            # Phase 3: Memory Synthesis
            update_callback("🧠 Phase 3: Memory Synthesis - Storing mission learnings...")
            self._synthesize_memory(mission_id_str, user_prompt, worker_result, True)

            # Calculate execution time
            execution_time = round(time.time() - start_time, 2)

            # Final result
            final_output = {
                "mission_id": mission_id_str,
                "status": "completed",
                "execution_time": execution_time,
                "result": worker_result,
                "plan": plan,
            }

            # Update database with final result
            self.db_manager.update_mission_status(
                mission_id_str,
                "completed",
                result=str(worker_result),
                execution_time=execution_time,
            )

            update_callback(f"✅ Mission completed successfully in {execution_time}s!")
            return final_output

        except Exception as e:
            execution_time = round(time.time() - start_time, 2)
            error_msg = str(e)

            logger.error(f"Mission {mission_id_str} failed: {error_msg}", exc_info=True)
            update_callback(f"❌ Mission failed: {error_msg}")

            # Store failure in memory
            self._synthesize_memory(mission_id_str, user_prompt, error_msg, False)

            # Update database with failure
            self.db_manager.update_mission_status(
                mission_id_str, "failed", error_message=error_msg, execution_time=execution_time
            )

            return {
                "mission_id": mission_id_str,
                "status": "failed",
                "execution_time": execution_time,
                "error": error_msg,
            }

    def _generate_execution_plan(
        self, user_prompt: str, mission_id_str: str, update_callback: Callable[[str], None]
    ) -> Dict[str, Any]:
        """
        Generate a sophisticated execution plan using the Lead Architect and Plan Validator.
        Includes memory integration for learning from past missions.
        """
        update_callback("  🏗️ Agent [Lead Architect]: Analyzing user goal and context...")

        # Search for relevant past experiences
        past_memories = self.db_manager.search_memory(user_prompt, limit=3)
        memory_context = ""
        if past_memories:
            memory_context = "\n\nRelevant Past Experiences:\n"
            for memory in past_memories:
                memory_context += f"- {memory['content'][:200]}...\n"

        # Create the Lead Architect agent
        architect = self.planner_agents.lead_architect(self.llm)

        planning_task = Task(
            description=f"""User's high-level goal: '{user_prompt}'
            
            {memory_context}
            
            Your task is to generate a JSON execution plan. The JSON must have a 'steps' array. 
            Each step object in the array must have the following keys: 
            - 'step_id': A unique identifier for the step
            - 'agent_role': The role to execute this step ('senior_developer', 'qa_tester', 'code_analyzer', 'system_integrator')
            - 'task_description': A crystal-clear description of what this step should accomplish
            - 'expected_output': A precise description of what this step should produce
            
            Available agent roles: 'senior_developer', 'qa_tester', 'code_analyzer', 'system_integrator'
            
            Consider the complexity of the task and assign the most appropriate agent for each step.
            Respond ONLY with the raw JSON object.""",
            expected_output="A valid JSON object representing the execution plan.",
            agent=architect,
        )

        # Create the Plan Validator agent
        validator = self.planner_agents.plan_validator(self.llm)

        validation_task = Task(
            description="""Review the generated JSON plan for:
            1. Valid JSON syntax
            2. Required fields: 'steps', 'agent_role', 'task_description', 'expected_output'
            3. Logical sequence and flow
            4. Appropriate agent assignments
            
            If valid, output the JSON as-is. If invalid, provide clear correction instructions.""",
            expected_output="The validated JSON plan or correction instructions.",
            agent=validator,
        )

        # Execute planning crew with validation
        planning_crew = Crew(
            agents=[architect, validator],
            tasks=[planning_task, validation_task],
            process=Process.sequential,
            verbose=True,
        )

        update_callback("  🔍 Agent [Plan Validator]: Validating execution plan...")
        plan_str = planning_crew.kickoff()

        # Parse the plan
        try:
            plan = json.loads(plan_str)
            update_callback(
                f"  ✅ Execution plan generated successfully with {len(plan.get('steps', []))} steps"
            )
            return plan
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract JSON from the response
            logger.warning("Failed to parse plan as JSON, attempting to extract...")
            # This is a fallback - in production, you'd want more robust JSON extraction
            raise ValueError("Generated plan is not valid JSON")

    def _execute_worker_crew(
        self, plan: Dict[str, Any], mission_id_str: str, update_callback: Callable[[str], None]
    ) -> str:
        """
        Assembles and runs a worker crew based on the generated plan.
        Implements real-time observability and progress tracking.
        """

        # Create agent instances
        agents_map = {
            "senior_developer": self.worker_agents.senior_developer(self.llm),
            "qa_tester": self.worker_agents.qa_tester(self.llm),
            "code_analyzer": self.worker_agents.code_analyzer(self.llm),
            "system_integrator": self.worker_agents.system_integrator(self.llm),
        }

        # Create tasks from the plan
        tasks = []
        for i, step in enumerate(plan.get("steps", [])):
            agent_role = step.get("agent_role")
            if agent_role in agents_map:
                step_number = i + 1
                update_callback(
                    f"  📋 Step {step_number}: Assigning task to [{agent_role.replace('_', ' ').title()}]"
                )
                update_callback(f"     Task: {step['task_description']}")

                # Create task with enhanced description
                task_description = f"""Step {step_number}: {step['task_description']}
                
                Mission Context: This is part of a larger mission. Ensure your work integrates well with other components.
                Expected Output: {step['expected_output']}
                
                Use your available tools effectively and provide clear, actionable results."""

                task = Task(
                    description=task_description,
                    expected_output=step["expected_output"],
                    agent=agents_map[agent_role],
                )
                tasks.append(task)

                # Log the task assignment
                self.db_manager.add_mission_update(
                    mission_id_str,
                    f"Step {step_number} assigned to {agent_role}",
                    "info",
                    agent_role,
                    step_number,
                )

        if not tasks:
            raise ValueError("No valid tasks could be created from the plan.")

        # Update mission status to executing
        self.db_manager.update_mission_status(mission_id_str, "executing")
        update_callback(f"  🚀 Deploying Worker Crew with {len(tasks)} tasks...")

        # Execute the worker crew
        worker_crew = Crew(
            agents=list(agents_map.values()), tasks=tasks, process=Process.sequential, verbose=True
        )

        result = worker_crew.kickoff()

        update_callback("  ✅ Worker crew execution completed successfully")
        return result

    def _synthesize_memory(
        self, mission_id_str: str, prompt: str, result: str, success: bool
    ) -> None:
        """
        Synthesize mission outcomes into long-term memory for future learning.
        """
        try:
            # Create memory synthesizer agent
            synthesizer = self.memory_agents.memory_synthesizer(self.llm)

            synthesis_task = Task(
                description=f"""Analyze this completed mission and extract key learnings:
                
                Mission ID: {mission_id_str}
                Prompt: {prompt}
                Success: {success}
                Result: {result}
                
                Create a concise summary that includes:
                1. Key learnings and patterns
                2. Successful strategies (if successful)
                3. Failure points and lessons (if failed)
                4. Recommendations for future similar missions
                
                Format your response as a structured summary suitable for long-term storage.""",
                expected_output="A structured summary of mission learnings and insights.",
                agent=synthesizer,
            )

            # Execute memory synthesis
            synthesis_crew = Crew(
                agents=[synthesizer],
                tasks=[synthesis_task],
                process=Process.sequential,
                verbose=False,
            )

            synthesis_result = synthesis_crew.kickoff()

            # Store in ChromaDB
            self.db_manager.store_memory(
                mission_id_str,
                prompt,
                synthesis_result,
                success,
                metadata={
                    "synthesis_type": "mission_outcome",
                    "agent_type": "cognitive_forge",
                    "success": success,
                },
            )

            logger.info(f"Memory synthesis completed for mission: {mission_id_str}")

        except Exception as e:
            logger.error(f"Error in memory synthesis: {e}")
            # Don't fail the mission if memory synthesis fails
            pass

    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            # Get database stats
            db_stats = self.db_manager.get_system_stats()

            # Get system information
            system_info = SystemTools.get_system_info()

            return {
                "database_stats": db_stats,
                "system_info": system_info,
                "engine_status": "operational",
                "model": os.getenv("LLM_MODEL", "gemini-1.5-pro-latest"),
                "last_updated": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            # Return a valid structure even when there are errors
            return {
                "database_stats": {
                    "total_missions": 0,
                    "completed_missions": 0,
                    "failed_missions": 0,
                    "pending_missions": 0,
                    "success_rate": 0,
                    "memory_entries": 0,
                    "last_updated": datetime.utcnow().isoformat(),
                    "error": str(e)
                },
                "system_info": "System information unavailable",
                "engine_status": "error",
                "model": os.getenv("LLM_MODEL", "gemini-1.5-pro-latest"),
                "last_updated": datetime.utcnow().isoformat(),
            }


# Global instance of the Cognitive Forge Engine
cognitive_forge_engine = CognitiveForgeEngine()
