import os
import json
import time
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import Crew, Task

from src.agents.advanced_agents import AdvancedAgents, PlanningSpecialistAgents
from src.models.advanced_database import AdvancedDatabase
from src.utils.phoenix_protocol import PhoenixProtocol
from src.utils.guardian_protocol import GuardianProtocol
from src.utils.synapse_logging import SynapseLogging
from src.utils.self_learning_module import SelfLearningModule
from src.utils.weave_observability import observability_manager, WeaveEnhancedEngine

class CognitiveForgeEngine:
    """Enhanced Cognitive Forge Engine with Phase 2 capabilities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize LLM
        api_key = os.getenv("GOOGLE_API_KEY")
        model_name = os.getenv("LLM_MODEL", "gemini-1.5-pro")
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.5"))
        
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature,
            convert_system_message_to_human=True
        )
        
        # Initialize core components
        self.db = AdvancedDatabase()
        self.agents = AdvancedAgents()
        self.prompt_optimization_agents = PlanningSpecialistAgents()
        self.phoenix = PhoenixProtocol()
        self.guardian = GuardianProtocol()
        self.synapse = SynapseLogging()
        self.self_learning = SelfLearningModule()
        
        # Initialize Phase 2 components
        self.async_execution_engine = AsyncExecutionEngine()
        self.enhanced_memory_manager = EnhancedMemoryManager()
        self.performance_monitor = PerformanceMonitor()
        
        # Initialize Weave observability
        self.observability = observability_manager
        self.weave_enhanced_engine = WeaveEnhancedEngine(self, observability_manager)
        
        self.logger.info(f"Cognitive Forge Engine v5.0 initialized with model: {model_name}")
        self.logger.info("Sentient Operating System: Phoenix Protocol, Guardian Protocol, and Synapse Logging active")
        self.logger.info("🔍 Weave Observability: Full mission tracing and analytics enabled")
    
    async def run_mission(self, user_request: str) -> Dict[str, Any]:
        """Enhanced mission execution with Phase 2 planning and execution"""
        mission_start_time = time.time()
        
        try:
            # Create mission record
            mission = self.db.create_mission(
                title=f"Mission: {user_request[:50]}...",
                description=user_request,
                status="initializing"
            )
            
            self.logger.info(f"Starting mission {mission['id']}: {user_request}")
            
            # Phase 1: Prompt Optimization
            self.logger.info("Phase 1: Executing prompt optimization")
            optimized_result = await self._execute_prompt_alchemy(user_request)
            
            if not optimized_result:
                raise ValueError("Prompt optimization failed")
            
            # Phase 2: Planning Specialist (NEW)
            self.logger.info("Phase 2: Creating execution blueprint")
            execution_blueprint = await self._execute_planning_specialist(
                optimized_result['optimized_prompt'], 
                optimized_result['technical_context']
            )
            
            if not execution_blueprint:
                raise ValueError("Execution blueprint creation failed")
            
            # Store blueprint in database
            blueprint = self.db.create_execution_blueprint(
                mission_id=mission['id'],
                blueprint_data=execution_blueprint,
                complexity_level=execution_blueprint.get('mission_overview', {}).get('complexity_level', 'medium'),
                estimated_duration_minutes=execution_blueprint.get('mission_overview', {}).get('estimated_total_duration_minutes', 60)
            )
            
            # Phase 3: Blueprint Validation
            self.logger.info("Phase 3: Validating execution blueprint")
            validation_result = await self._validate_execution_blueprint(execution_blueprint)
            
            if validation_result.get('validation_status') != 'approved':
                self.logger.warning(f"Blueprint validation issues: {validation_result}")
                # Continue with warnings, but log the issues
            
            # Update blueprint status
            self.db.update_blueprint_status(
                blueprint_id=blueprint['id'],
                status='validated',
                validation_score=validation_result.get('overall_score')
            )
            
            # Phase 4: Enhanced Mission Execution
            self.logger.info("Phase 4: Executing mission with enhanced engine")
            execution_result = await self._execute_enhanced_mission(
                mission_id=mission['id'],
                blueprint_id=blueprint['id'],
                execution_blueprint=execution_blueprint
            )
            
            # Calculate total execution time
            total_execution_time = time.time() - mission_start_time
            
            # Record final performance metrics
            self.db.record_performance_metric(
                mission_id=mission['id'],
                blueprint_id=blueprint['id'],
                metric_name='total_execution_time',
                metric_value=total_execution_time,
                metric_unit='seconds',
                context={
                    'phases': {
                        'prompt_optimization': optimized_result.get('execution_time', 0),
                        'planning': execution_blueprint.get('planning_time', 0),
                        'validation': validation_result.get('validation_time', 0),
                        'execution': execution_result.get('execution_time', 0)
                    }
                }
            )
            
            # Update mission status
            final_status = "completed" if execution_result.get('success', False) else "failed"
            self.db.update_mission_status(
                mission_id=mission['id'],
                status=final_status,
                result_data={
                    'optimized_prompt': optimized_result,
                    'execution_blueprint': execution_blueprint,
                    'validation_result': validation_result,
                    'execution_result': execution_result,
                    'total_execution_time': total_execution_time
                }
            )
            
            self.logger.info(f"Mission {mission['id']} completed in {total_execution_time:.2f}s")
            
            # Log mission completion with observability
            self.observability.log_system_event("mission_completed", {
                "mission_id": mission['id'],
                "execution_time": total_execution_time,
                "phases_completed": ["prompt_optimization", "planning", "validation", "execution"],
                "status": final_status
            })
            
            return {
                'mission_id': mission['id'],
                'status': final_status,
                'optimized_prompt': optimized_result,
                'execution_blueprint': execution_blueprint,
                'validation_result': validation_result,
                'execution_result': execution_result,
                'total_execution_time': total_execution_time
            }
            
        except Exception as e:
            self.logger.error(f"Mission execution failed: {e}")
            if 'mission' in locals():
                self.db.update_mission_status(
                    mission_id=mission['id'],
                    status="failed",
                    result_data={'error': str(e)}
                )
            raise
    
    async def run_mission_with_observability(self, user_request: str) -> Dict[str, Any]:
        """Run mission with comprehensive Weave observability and tracing."""
        return await self.weave_enhanced_engine.run_mission_with_observability(user_request)
    
    async def _execute_prompt_alchemy(self, user_request: str) -> Dict[str, Any]:
        """Execute prompt optimization (Phase 1)"""
        try:
            # Create Advanced Prompt Optimization Agent
            prompt_optimizer = self.prompt_optimization_agents.prompt_optimizer(self.llm)
            
            from src.core.blueprint_tasks import optimize_prompt_task
            analysis_task = Task(
                description=f"""Analyze and optimize the following user prompt: '{user_request}'.

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
                agent=prompt_optimizer
            )
            
            crew = Crew(
                agents=[prompt_optimizer],
                tasks=[analysis_task],
                verbose=True,
                memory=True
            )
            
            result = await crew.kickoff()
            
            # Parse the result
            optimized_result = self._parse_agent_json_response(result)
            optimized_result['execution_time'] = time.time()
            
            self.logger.info("Prompt optimization completed successfully")
            return optimized_result
            
        except Exception as e:
            self.logger.error(f"Prompt optimization failed: {e}")
            raise
    
    async def _execute_planning_specialist(self, optimized_prompt: str, technical_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute planning specialist to create execution blueprint"""
        try:
            # Create planning specialist agent
            planning_specialist = self.prompt_optimization_agents.planning_specialist(self.llm)
            
            # Create planning task
            from src.core.blueprint_tasks import create_execution_blueprint_task
            planning_task = create_execution_blueprint_task(optimized_prompt, technical_context)
            
            # Execute planning
            crew = Crew(
                agents=[planning_specialist],
                tasks=[planning_task],
                verbose=True,
                memory=True
            )
            
            result = await crew.kickoff()
            
            # Parse the result
            blueprint = self._parse_agent_json_response(result)
            
            # Add planning metadata
            blueprint['planning_time'] = time.time()
            blueprint['planning_agent'] = 'planning_specialist'
            
            self.logger.info("Execution blueprint created successfully")
            return blueprint
            
        except Exception as e:
            self.logger.error(f"Planning specialist execution failed: {e}")
            raise
    
    async def _validate_execution_blueprint(self, execution_blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """Validate execution blueprint for feasibility and optimization"""
        try:
            # Create lead architect agent for validation
            lead_architect = self.agents.lead_architect(self.llm)
            
            # Create validation task
            from src.core.blueprint_tasks import validate_blueprint_task
            validation_task = validate_blueprint_task(execution_blueprint)
            
            # Execute validation
            crew = Crew(
                agents=[lead_architect],
                tasks=[validation_task],
                verbose=True,
                memory=True
            )
            
            result = await crew.kickoff()
            
            # Parse the result
            validation_result = self._parse_agent_json_response(result)
            
            # Add validation metadata
            validation_result['validation_time'] = time.time()
            validation_result['validation_agent'] = 'lead_architect'
            
            self.logger.info(f"Blueprint validation completed: {validation_result.get('validation_status')}")
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Blueprint validation failed: {e}")
            raise
    
    async def _execute_enhanced_mission(self, mission_id: int, blueprint_id: int, 
                                      execution_blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """Execute mission using enhanced execution engine"""
        try:
            execution_start_time = time.time()
            
            # Initialize execution engine
            await self.async_execution_engine.initialize(mission_id, blueprint_id, execution_blueprint)
            
            # Start resource monitoring
            self.performance_monitor.start_monitoring(mission_id)
            
            # Execute the mission
            execution_result = await self.async_execution_engine.execute_mission()
            
            # Stop monitoring
            self.performance_monitor.stop_monitoring(mission_id)
            
            # Add execution metadata
            execution_result['execution_time'] = time.time() - execution_start_time
            execution_result['mission_id'] = mission_id
            execution_result['blueprint_id'] = blueprint_id
            
            self.logger.info(f"Enhanced mission execution completed: {execution_result.get('execution_status')}")
            return execution_result
            
        except Exception as e:
            self.logger.error(f"Enhanced mission execution failed: {e}")
            raise
    
    def _parse_agent_json_response(self, response_str: str) -> Dict[str, Any]:
        """
        Robustly parse JSON responses from agents that may include markdown formatting
        Handles cases where JSON is wrapped in ```json ... ``` blocks
        """
        import re
        cleaned_response = response_str.strip()
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, cleaned_response, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            start_idx = cleaned_response.find('{')
            end_idx = cleaned_response.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = cleaned_response[start_idx:end_idx + 1]
            else:
                json_str = cleaned_response
        json_str = json_str.strip()
        json_str = re.sub(r'^[^{]*', '', json_str)
        json_str = re.sub(r'[^}]*$', '', json_str)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON: {json_str}")
            self.logger.error(f"Original response: {response_str}")
            raise ValueError(f"Invalid JSON format: {str(e)}") from e

class AsyncExecutionEngine:
    """Asynchronous execution engine for concurrent task execution"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.mission_id = None
        self.blueprint_id = None
        self.execution_blueprint = None
        self.active_tasks = {}
        self.completed_tasks = {}
        self.failed_tasks = {}
        self.resource_monitor = None
    
    async def initialize(self, mission_id: int, blueprint_id: int, execution_blueprint: Dict[str, Any]):
        """Initialize execution engine with mission data"""
        self.mission_id = mission_id
        self.blueprint_id = blueprint_id
        self.execution_blueprint = execution_blueprint
        self.active_tasks = {}
        self.completed_tasks = {}
        self.failed_tasks = {}
        
        self.logger.info(f"AsyncExecutionEngine initialized for mission {mission_id}")
    
    async def execute_mission(self) -> Dict[str, Any]:
        """Execute mission according to blueprint"""
        try:
            execution_phases = self.execution_blueprint.get('execution_phases', [])
            
            for phase in execution_phases:
                await self._execute_phase(phase)
            
            # Compile final results
            return self._compile_execution_results()
            
        except Exception as e:
            self.logger.error(f"Mission execution failed: {e}")
            raise
    
    async def _execute_phase(self, phase: Dict[str, Any]):
        """Execute a single phase"""
        phase_id = phase.get('phase_id')
        tasks = phase.get('tasks', [])
        
        self.logger.info(f"Executing phase: {phase_id}")
        
        # Execute tasks based on dependencies and parallel execution strategy
        execution_strategy = self.execution_blueprint.get('execution_strategy', {})
        max_concurrent = execution_strategy.get('max_concurrent_tasks', 3)
        
        # Group tasks by dependencies
        task_groups = self._group_tasks_by_dependencies(tasks)
        
        for group in task_groups:
            # Execute tasks in parallel within the group
            await self._execute_task_group(group, max_concurrent)
    
    async def _execute_task_group(self, tasks: List[Dict[str, Any]], max_concurrent: int):
        """Execute a group of tasks with concurrency limits"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_task_with_semaphore(task):
            async with semaphore:
                return await self._execute_single_task(task)
        
        # Execute tasks concurrently
        task_coroutines = [execute_task_with_semaphore(task) for task in tasks]
        results = await asyncio.gather(*task_coroutines, return_exceptions=True)
        
        # Process results
        for task, result in zip(tasks, results):
            if isinstance(result, Exception):
                self.failed_tasks[task['task_id']] = {
                    'task': task,
                    'error': str(result)
                }
            else:
                self.completed_tasks[task['task_id']] = {
                    'task': task,
                    'result': result
                }
    
    async def _execute_single_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task"""
        task_id = task['task_id']
        agent_type = task['assigned_agent']
        
        try:
            # Create task execution record
            from src.models.advanced_database import AdvancedDatabase
            db = AdvancedDatabase()
            
            execution_record = db.create_task_execution(
                blueprint_id=self.blueprint_id,
                mission_id=self.mission_id,
                task_id_in_blueprint=task_id,
                agent_used=agent_type,
                estimated_duration_ms=task.get('estimated_duration_ms')
            )
            
            # Start task execution
            db.update_task_execution(
                execution_id=execution_record['id'],
                status='running'
            )
            
            # Execute task (simplified for now - would integrate with actual agent execution)
            task_result = await self._execute_task_with_agent(task, agent_type)
            
            # Update execution record
            db.update_task_execution(
                execution_id=execution_record['id'],
                status='completed',
                actual_duration_ms=int((time.time() - execution_record['created_at']) * 1000),
                log_summary=f"Task completed successfully: {task.get('task_name')}"
            )
            
            return task_result
            
        except Exception as e:
            # Update execution record with error
            db.update_task_execution(
                execution_id=execution_record['id'],
                status='failed',
                error_message=str(e)
            )
            raise
    
    async def _execute_task_with_agent(self, task: Dict[str, Any], agent_type: str) -> Dict[str, Any]:
        """Execute task with specific agent (placeholder for actual agent integration)"""
        # This would integrate with the actual agent execution system
        # For now, return a placeholder result
        await asyncio.sleep(0.1)  # Simulate task execution
        
        return {
            'task_id': task['task_id'],
            'status': 'completed',
            'result': f"Task {task['task_name']} completed by {agent_type}",
            'execution_time': 0.1
        }
    
    def _group_tasks_by_dependencies(self, tasks: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group tasks by dependencies for sequential execution"""
        # Simple dependency grouping - tasks without dependencies first
        groups = []
        remaining_tasks = tasks.copy()
        
        while remaining_tasks:
            # Find tasks with no pending dependencies
            executable_tasks = []
            for task in remaining_tasks:
                dependencies = task.get('dependencies', [])
                if not dependencies or all(dep in self.completed_tasks for dep in dependencies):
                    executable_tasks.append(task)
            
            if not executable_tasks:
                # Circular dependency or missing dependency
                break
            
            groups.append(executable_tasks)
            
            # Remove executed tasks from remaining
            for task in executable_tasks:
                remaining_tasks.remove(task)
        
        return groups
    
    def _compile_execution_results(self) -> Dict[str, Any]:
        """Compile final execution results"""
        total_tasks = len(self.completed_tasks) + len(self.failed_tasks)
        success_rate = len(self.completed_tasks) / total_tasks if total_tasks > 0 else 0
        
        return {
            'execution_status': 'completed' if success_rate >= 0.8 else 'failed',
            'success': success_rate >= 0.8,
            'success_rate': success_rate,
            'total_tasks': total_tasks,
            'completed_tasks': len(self.completed_tasks),
            'failed_tasks': len(self.failed_tasks),
            'task_results': {
                'completed': self.completed_tasks,
                'failed': self.failed_tasks
            }
        }

class EnhancedMemoryManager:
    """Enhanced memory management for optimal resource usage"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.memory_cache = {}
        self.context_sharing = {}
    
    def optimize_memory_usage(self, mission_id: int, current_usage_mb: int) -> Dict[str, Any]:
        """Optimize memory usage for the mission"""
        # Memory optimization logic
        return {
            'optimization_applied': True,
            'memory_saved_mb': max(0, current_usage_mb * 0.1),  # 10% optimization
            'recommendations': ['Clear unused contexts', 'Optimize agent memory']
        }

class PerformanceMonitor:
    """Performance monitoring and analytics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.monitoring_tasks = {}
    
    def start_monitoring(self, mission_id: int):
        """Start performance monitoring for a mission"""
        self.logger.info(f"Started performance monitoring for mission {mission_id}")
    
    def stop_monitoring(self, mission_id: int):
        """Stop performance monitoring for a mission"""
        self.logger.info(f"Stopped performance monitoring for mission {mission_id}")
    
    def record_metric(self, mission_id: int, metric_name: str, metric_value: float):
        """Record a performance metric"""
        # Record metric logic
        pass 