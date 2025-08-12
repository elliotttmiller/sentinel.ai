"""
Real Mission Executor - Executes actual tasks based on user prompts
Combines AI task parsing with real system operations
"""

import asyncio
import os
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from loguru import logger

# Import components
try:
    from .ai_task_parser import AITaskParser
    from .executable_agent import ExecutableAgent
    from ..utils.agent_observability import agent_observability, LiveStreamEvent
    from ..models.advanced_database import db_manager
except ImportError:
    from ai_task_parser import AITaskParser
    from executable_agent import ExecutableAgent
    from utils.agent_observability import agent_observability, LiveStreamEvent
    from models.advanced_database import db_manager


class RealMissionExecutor:
    """Executes real missions that perform actual tasks"""
    
    def __init__(self, workspace_root: str = None):
        self.workspace_root = workspace_root or os.path.join(os.getcwd(), "sentinel_workspace")
        Path(self.workspace_root).mkdir(parents=True, exist_ok=True)
        
        self.task_parser = AITaskParser()
        self.db_manager = db_manager
        
        logger.info(f"RealMissionExecutor initialized - Workspace: {self.workspace_root}")
    
    async def execute_mission(
        self, 
        user_prompt: str, 
        mission_id: str, 
        agent_type: str = "developer"
    ) -> Dict[str, Any]:
        """Execute a real mission that performs actual tasks"""
        try:
            # Update mission status to running
            self.db_manager.update_mission_status(mission_id, "running", progress=10)
            
            # Broadcast mission start
            agent_observability.push_event(LiveStreamEvent(
                event_type="mission_update",
                source="real_mission_executor",
                severity="INFO",
                message=f"Starting real mission execution: {mission_id}",
                payload={
                    "mission_id": mission_id,
                    "prompt": user_prompt,
                    "agent_type": agent_type,
                    "workspace": self.workspace_root
                }
            ))
            
            # Phase 1: Parse the user prompt into executable tasks
            logger.info(f"Phase 1: Parsing prompt for mission {mission_id}")
            agent_observability.push_event(LiveStreamEvent(
                event_type="agent_action",
                source="task_parser",
                severity="INFO",
                message="Analyzing user request and generating execution plan",
                payload={"mission_id": mission_id, "phase": "task_parsing"}
            ))
            
            task_plan = await self.task_parser.parse_prompt_to_task_plan(user_prompt, mission_id)
            self.db_manager.update_mission_status(mission_id, "running", progress=25)
            
            logger.info(f"Task plan generated: {task_plan.get('task_type', 'unknown')}")
            agent_observability.push_event(LiveStreamEvent(
                event_type="agent_action",
                source="task_parser",
                severity="SUCCESS",
                message=f"Task plan generated: {task_plan.get('name', 'unnamed')}",
                payload={
                    "mission_id": mission_id,
                    "task_plan": task_plan,
                    "phase": "task_parsing_complete"
                }
            ))
            
            # Phase 2: Create executable agent for the specific mission
            logger.info(f"Phase 2: Creating executable agent for mission {mission_id}")
            mission_workspace = os.path.join(self.workspace_root, f"mission_{mission_id}")
            executable_agent = ExecutableAgent(agent_type, mission_workspace)
            executable_agent.set_mission_context(mission_id)
            
            agent_observability.push_event(LiveStreamEvent(
                event_type="agent_action",
                source="executable_agent",
                severity="INFO",
                message=f"Agent initialized for {task_plan.get('task_type', 'generic')} task",
                payload={
                    "mission_id": mission_id,
                    "agent_type": agent_type,
                    "workspace": mission_workspace,
                    "phase": "agent_initialization"
                }
            ))
            
            self.db_manager.update_mission_status(mission_id, "running", progress=40)
            
            # Phase 3: Execute the task plan
            logger.info(f"Phase 3: Executing task plan for mission {mission_id}")
            agent_observability.push_event(LiveStreamEvent(
                event_type="agent_action",
                source="executable_agent",
                severity="INFO",
                message="Starting task execution",
                payload={
                    "mission_id": mission_id,
                    "phase": "task_execution_start"
                }
            ))
            
            execution_result = await executable_agent.execute_task_plan(task_plan.get("executable_plan", {}))
            self.db_manager.update_mission_status(mission_id, "running", progress=80)
            
            # Phase 4: Finalize and report results
            logger.info(f"Phase 4: Finalizing mission {mission_id}")
            
            if execution_result.get("success", False):
                # Mission completed successfully
                final_message = f"Mission '{mission_id}' completed successfully!"
                final_status = "completed"
                
                # Create summary of what was created
                results_summary = self._create_results_summary(execution_result, task_plan, mission_workspace)
                
                agent_observability.push_event(LiveStreamEvent(
                    event_type="mission_complete",
                    source="real_mission_executor",
                    severity="SUCCESS",
                    message=final_message,
                    payload={
                        "mission_id": mission_id,
                        "execution_result": execution_result,
                        "results_summary": results_summary,
                        "workspace": mission_workspace
                    }
                ))
                
                self.db_manager.update_mission_status(
                    mission_id, 
                    final_status, 
                    progress=100, 
                    result=results_summary
                )
                
                logger.info(f"Mission {mission_id} completed successfully")
                return {
                    "status": "completed",
                    "mission_id": mission_id,
                    "execution_result": execution_result,
                    "results_summary": results_summary,
                    "workspace": mission_workspace
                }
            else:
                # Mission failed
                error_message = execution_result.get("error", "Unknown execution error")
                final_message = f"Mission '{mission_id}' failed: {error_message}"
                
                agent_observability.push_event(LiveStreamEvent(
                    event_type="mission_error",
                    source="real_mission_executor",
                    severity="ERROR",
                    message=final_message,
                    payload={
                        "mission_id": mission_id,
                        "error": error_message,
                        "execution_result": execution_result
                    }
                ))
                
                self.db_manager.update_mission_status(
                    mission_id, 
                    "failed", 
                    error_message=error_message
                )
                
                logger.error(f"Mission {mission_id} failed: {error_message}")
                return {
                    "status": "failed",
                    "mission_id": mission_id,
                    "error": error_message,
                    "execution_result": execution_result
                }
                
        except Exception as e:
            error_message = str(e)
            logger.error(f"Mission {mission_id} encountered an error: {error_message}")
            
            agent_observability.push_event(LiveStreamEvent(
                event_type="mission_error",
                source="real_mission_executor",
                severity="ERROR",
                message=f"Mission '{mission_id}' encountered an error: {error_message}",
                payload={
                    "mission_id": mission_id,
                    "error": error_message,
                    "error_type": type(e).__name__
                }
            ))
            
            self.db_manager.update_mission_status(
                mission_id, 
                "failed", 
                error_message=error_message
            )
            
            return {
                "status": "failed",
                "mission_id": mission_id,
                "error": error_message,
                "error_type": type(e).__name__
            }
    
    def _create_results_summary(self, execution_result: Dict[str, Any], task_plan: Dict[str, Any], workspace: str) -> str:
        """Create a human-readable summary of mission results"""
        summary_parts = []
        
        # Basic info
        task_type = task_plan.get("task_type", "generic")
        task_name = task_plan.get("name", "unnamed")
        
        summary_parts.append(f"✅ **Mission Completed**: {task_name}")
        summary_parts.append(f"📋 **Task Type**: {task_type}")
        summary_parts.append(f"📁 **Workspace**: {workspace}")
        
        # Results details
        if execution_result.get("project_path"):
            summary_parts.append(f"🎯 **Created Project**: {execution_result['project_path']}")
        
        if execution_result.get("created_items"):
            summary_parts.append("📄 **Files Created**:")
            for item in execution_result["created_items"][:10]:  # Limit to first 10 items
                summary_parts.append(f"   - {item}")
        
        if execution_result.get("file_path"):
            summary_parts.append(f"📄 **File Created**: {execution_result['file_path']}")
        
        # Expected outputs
        expected_outputs = task_plan.get("expected_outputs", [])
        if expected_outputs:
            summary_parts.append("🎯 **Expected Outputs**:")
            for output in expected_outputs:
                summary_parts.append(f"   - {output}")
        
        # Timestamp
        summary_parts.append(f"⏰ **Completed At**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        
        return "\\n".join(summary_parts)
    
    def get_mission_workspace(self, mission_id: str) -> str:
        """Get the workspace path for a specific mission"""
        return os.path.join(self.workspace_root, f"mission_{mission_id}")
    
    def list_workspace_contents(self, mission_id: str) -> Dict[str, Any]:
        """List the contents of a mission's workspace"""
        workspace = self.get_mission_workspace(mission_id)
        
        if not os.path.exists(workspace):
            return {"exists": False, "path": workspace}
        
        contents = {"exists": True, "path": workspace, "items": []}
        
        try:
            for root, dirs, files in os.walk(workspace):
                rel_root = os.path.relpath(root, workspace)
                if rel_root == ".":
                    rel_root = ""
                
                for d in dirs:
                    contents["items"].append({
                        "type": "directory",
                        "name": d,
                        "path": os.path.join(rel_root, d) if rel_root else d
                    })
                
                for f in files:
                    file_path = os.path.join(root, f)
                    rel_path = os.path.join(rel_root, f) if rel_root else f
                    
                    contents["items"].append({
                        "type": "file",
                        "name": f,
                        "path": rel_path,
                        "size": os.path.getsize(file_path)
                    })
        
        except Exception as e:
            contents["error"] = str(e)
        
        return contents
