"""
Real Mission Executor - Bridges cognitive engine to executable agents
Now uses CrewAI-based ExecutionWorkflow for true task execution
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

# Import the new execution workflow
from src.core.execution_workflow import ExecutionWorkflow
from src.utils.agent_observability import agent_observability, LiveStreamEvent


class RealMissionExecutor:
    """
    Executes real AI agent missions using the CrewAI-based ExecutionWorkflow
    This replaces the simulation-based approach with actual task execution
    """
    
    def __init__(self):
        self.execution_workflow = ExecutionWorkflow()
        self.active_missions = {}
        logger.info("RealMissionExecutor initialized with ExecutionWorkflow")
    
    async def execute_mission(self, mission_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a mission using real AI agents that perform actual tasks
        """
        mission_id = mission_data.get('id', f"mission_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
        
        try:
            # Set mission context for observability
            self.execution_workflow.set_mission_context(mission_id)
            
            # Extract mission details
            user_request = mission_data.get('objective', 'No objective specified')
            agent_type = mission_data.get('agent_type', 'general')
            complexity = mission_data.get('complexity', 'medium')
            
            # Broadcast mission start
            agent_observability.push_event(LiveStreamEvent(
                event_type="mission_started",
                source="real_mission_executor", 
                severity="INFO",
                message=f"Starting real mission execution: {mission_id}",
                payload={
                    "mission_id": mission_id,
                    "objective": user_request,
                    "agent_type": agent_type,
                    "complexity": complexity,
                    "timestamp": datetime.utcnow().isoformat()
                }
            ))
            
            # Store mission as active
            self.active_missions[mission_id] = {
                "status": "executing",
                "start_time": datetime.utcnow(),
                "mission_data": mission_data
            }
            
            # Create mission context for the workflow
            mission_context = {
                "mission_id": mission_id,
                "agent_type": agent_type,  
                "complexity": complexity,
                "metadata": mission_data.get('metadata', {})
            }
            
            # Execute the mission using the ExecutionWorkflow
            logger.info(f"Executing real mission {mission_id}: {user_request}")
            execution_result = await self.execution_workflow.execute_mission(
                user_request=user_request,
                mission_context=mission_context
            )
            
            # Update mission status
            self.active_missions[mission_id].update({
                "status": "completed" if execution_result.get("success") else "failed",
                "end_time": datetime.utcnow(),
                "result": execution_result
            })
            
            # Create comprehensive result
            result = {
                "mission_id": mission_id,
                "success": execution_result.get("success", False),
                "objective": user_request,
                "agent_type": agent_type,
                "execution_details": execution_result,
                "planning_output": execution_result.get("planning_output", "Planning completed"),
                "execution_output": execution_result.get("execution_output", "Execution completed"), 
                "supervision_output": execution_result.get("supervision_output", "Supervision completed"),
                "crew_result": execution_result.get("crew_result", "Mission processed"),
                "real_world_changes": True,  # This is key - we actually perform tasks
                "timestamp": datetime.utcnow().isoformat(),
                "message": execution_result.get("message", "Mission processing completed")
            }
            
            # Broadcast mission completion
            agent_observability.push_event(LiveStreamEvent(
                event_type="mission_completed",
                source="real_mission_executor",
                severity="SUCCESS" if result["success"] else "ERROR",
                message=f"Mission {mission_id} {'completed successfully' if result['success'] else 'failed'}",
                payload=result
            ))
            
            logger.success(f"Real mission {mission_id} executed: {result['success']}")
            return result
            
        except Exception as e:
            # Update mission status on error
            if mission_id in self.active_missions:
                self.active_missions[mission_id].update({
                    "status": "error",
                    "end_time": datetime.utcnow(),
                    "error": str(e)
                })
            
            error_result = {
                "mission_id": mission_id,
                "success": False,
                "error": str(e),
                "objective": mission_data.get('objective', 'Unknown'),
                "agent_type": mission_data.get('agent_type', 'unknown'),
                "message": f"Mission execution failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Broadcast error
            agent_observability.push_event(LiveStreamEvent(
                event_type="mission_error",
                source="real_mission_executor",
                severity="ERROR", 
                message=f"Mission {mission_id} failed: {str(e)}",
                payload=error_result
            ))
            
            logger.error(f"Real mission {mission_id} failed: {e}")
            return error_result
    
    async def execute_simple_task(self, task_description: str) -> Dict[str, Any]:
        """
        Execute a simple task without full mission orchestration
        """
        try:
            task_id = f"task_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Broadcast task start
            agent_observability.push_event(LiveStreamEvent(
                event_type="task_started",
                source="real_mission_executor",
                severity="INFO",
                message=f"Starting simple task: {task_description}",
                payload={
                    "task_id": task_id,
                    "description": task_description,
                    "timestamp": datetime.utcnow().isoformat()
                }
            ))
            
            # Execute using the workflow
            result = await self.execution_workflow.execute_simple_task(task_description)
            
            # Add task metadata
            result.update({
                "task_id": task_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Broadcast completion
            agent_observability.push_event(LiveStreamEvent(
                event_type="task_completed",
                source="real_mission_executor",
                severity="SUCCESS" if result.get("success") else "ERROR",
                message=f"Task {task_id} {'completed' if result.get('success') else 'failed'}",
                payload=result
            ))
            
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "task_description": task_description,
                "message": f"Task execution failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.error(f"Simple task failed: {e}")
            return error_result
    
    def get_mission_status(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of an active or completed mission"""
        return self.active_missions.get(mission_id)
    
    def list_active_missions(self) -> Dict[str, Any]:
        """List all active missions"""
        return {
            mission_id: {
                "status": mission_info["status"],
                "start_time": mission_info["start_time"].isoformat(),
                "objective": mission_info["mission_data"].get("objective", "Unknown")
            }
            for mission_id, mission_info in self.active_missions.items()
            if mission_info["status"] == "executing"
        }
