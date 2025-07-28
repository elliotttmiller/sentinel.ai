from typing import Dict, Any, List
from loguru import logger
from agents.agent_factory import AgentFactory
from tools.tool_manager import ToolManager

class CrewManager:
    """Manages the execution of missions using real AI agents."""
    
    def __init__(self, agent_factory: AgentFactory, tool_manager: ToolManager):
        self.agent_factory = agent_factory
        self.tool_manager = tool_manager
        logger.info("CrewManager initialized for engine")
    
    async def execute_mission(self, execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a mission using the provided execution plan."""
        try:
            mission_id = execution_plan.get("mission_id")
            steps = execution_plan.get("steps", [])
            
            logger.info(f"ENGINE: Starting real agent execution for mission {mission_id}")
            logger.info(f"ENGINE: Mission has {len(steps)} steps")
            
            step_results = []
            overall_success = True
            
            for i, step in enumerate(steps):
                step_id = step.get("step_id", f"step_{i+1}")
                agent_type = step.get("agent_type", "file_manager")
                task_description = step.get("task_description", "Execute task")
                parameters = step.get("parameters", {})
                
                logger.info(f"ENGINE: Executing step {step_id} with agent {agent_type}")
                
                # Create the appropriate agent
                agent = self.agent_factory.create_agent(agent_type)
                if not agent:
                    logger.error(f"ENGINE: Failed to create agent {agent_type} for step {step_id}")
                    step_result = {
                        "step_id": step_id,
                        "status": "failed",
                        "error": f"Failed to create agent {agent_type}",
                        "agent": "unknown"
                    }
                    overall_success = False
                else:
                    # Execute the task with the agent
                    result = await agent.execute_task(task_description, parameters)
                    
                    step_result = {
                        "step_id": step_id,
                        "status": "completed" if result.get("success", False) else "failed",
                        "output": result.get("message", result.get("error", "Unknown error")),
                        "agent": agent.name,
                        "task_type": result.get("task_type", "unknown"),
                        "details": result
                    }
                    
                    if not result.get("success", False):
                        overall_success = False
                
                step_results.append(step_result)
                logger.info(f"ENGINE: Step {step_id} completed with status: {step_result['status']}")
            
            # Create mission summary
            summary = self._create_mission_summary(mission_id, step_results, overall_success)
            
            return {
                "success": overall_success,
                "mission_id": mission_id,
                "summary": summary,
                "step_results": step_results,
                "total_steps": len(steps),
                "completed_steps": len([r for r in step_results if r["status"] == "completed"]),
                "failed_steps": len([r for r in step_results if r["status"] == "failed"])
            }
            
        except Exception as e:
            logger.error(f"ENGINE: Mission execution failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "mission_id": execution_plan.get("mission_id", "unknown")
            }
    
    def _create_mission_summary(self, mission_id: str, step_results: List[Dict], overall_success: bool) -> str:
        """Create a summary of the mission execution."""
        completed_count = len([r for r in step_results if r["status"] == "completed"])
        failed_count = len([r for r in step_results if r["status"] == "failed"])
        
        summary = f"""Mission Execution Summary
Mission ID: {mission_id}
Overall Status: {'SUCCESS' if overall_success else 'FAILED'}
Total Steps: {len(step_results)}
Completed Steps: {completed_count}
Failed Steps: {failed_count}

Step Details:
"""
        
        for result in step_results:
            summary += f"- Step {result['step_id']}: {result['status'].upper()} ({result['agent']})\n"
            if result.get("output"):
                summary += f"  Output: {result['output']}\n"
        
        return summary 