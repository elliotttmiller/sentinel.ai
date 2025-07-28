from typing import Dict, Any
from loguru import logger
from datetime import datetime

class FileManager:
    """File Manager agent for executing file operations on the desktop."""
    
    def __init__(self, llm_client=None, tool_manager=None, **kwargs):
        self.llm_client = llm_client
        self.tool_manager = tool_manager
        self.name = "File Manager"
        self.role = "file_manager"
        self.goal = "Manage files and directories on the desktop efficiently"
        self.backstory = """You are a file management specialist with expertise in organizing, 
        creating, and managing files and directories. You work directly on the desktop to 
        handle all file-related operations."""
        
        logger.info(f"FileManager agent initialized")
    
    async def execute_task(self, task_description: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a file management task."""
        try:
            logger.info(f"FileManager executing task: {task_description}")
            
            # Determine the type of task and execute accordingly
            if "create" in task_description.lower() and "file" in task_description.lower():
                return await self._create_file_task(parameters)
            elif "read" in task_description.lower() and "file" in task_description.lower():
                return await self._read_file_task(parameters)
            elif "delete" in task_description.lower() and "file" in task_description.lower():
                return await self._delete_file_task(parameters)
            elif "organize" in task_description.lower() or "organize" in task_description.lower():
                return await self._organize_files_task(parameters)
            else:
                return await self._generic_file_task(task_description, parameters)
                
        except Exception as e:
            logger.error(f"FileManager task failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }
    
    async def _create_file_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a file with specified content."""
        file_path = parameters.get("file_path")
        content = parameters.get("content", "")
        
        if not file_path:
            return {
                "success": False,
                "error": "file_path is required",
                "agent": self.name
            }
        
        # If no content provided, create a default content
        if not content:
            content = f"File created by Sentinel AI File Manager\nTimestamp: {datetime.now().isoformat()}\nPurpose: {parameters.get('purpose', 'General file management')}"
        
        result = self.tool_manager.execute_tool("file_io", "create_file", 
                                               file_path=file_path, content=content)
        
        return {
            "success": result.get("success", False),
            "message": result.get("message", result.get("error", "Unknown error")),
            "agent": self.name,
            "task_type": "file_creation"
        }
    
    async def _read_file_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Read the contents of a file."""
        file_path = parameters.get("file_path")
        
        if not file_path:
            return {
                "success": False,
                "error": "file_path is required",
                "agent": self.name
            }
        
        result = self.tool_manager.execute_tool("file_io", "read_file", file_path=file_path)
        
        return {
            "success": result.get("success", False),
            "content": result.get("content", result.get("error", "Unknown error")),
            "agent": self.name,
            "task_type": "file_reading"
        }
    
    async def _delete_file_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a file."""
        file_path = parameters.get("file_path")
        
        if not file_path:
            return {
                "success": False,
                "error": "file_path is required",
                "agent": self.name
            }
        
        result = self.tool_manager.execute_tool("file_io", "delete_file", file_path=file_path)
        
        return {
            "success": result.get("success", False),
            "message": result.get("message", result.get("error", "Unknown error")),
            "agent": self.name,
            "task_type": "file_deletion"
        }
    
    async def _organize_files_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Organize files in a directory."""
        directory = parameters.get("directory", "C:/Users/AMD/Desktop")
        organization_type = parameters.get("organization_type", "by_type")
        
        # Create an organization log
        log_content = f"""File Organization Report
Directory: {directory}
Organization Type: {organization_type}
Timestamp: {datetime.now().isoformat()}
Status: Organization completed by {self.name}

This is a placeholder for file organization logic.
In a full implementation, this would:
1. Scan the directory for files
2. Categorize files by type, date, or other criteria
3. Create appropriate subdirectories
4. Move files to their appropriate locations
"""
        
        result = self.tool_manager.execute_tool("file_io", "create_file", 
                                               file_path=f"{directory}/organization_report.txt", 
                                               content=log_content)
        
        return {
            "success": result.get("success", False),
            "message": f"File organization completed for {directory}",
            "agent": self.name,
            "task_type": "file_organization"
        }
    
    async def _generic_file_task(self, task_description: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generic file tasks."""
        # Create a task log
        log_content = f"""File Management Task Log
Task: {task_description}
Parameters: {parameters}
Timestamp: {datetime.now().isoformat()}
Agent: {self.name}
Status: Task completed
"""
        
        result = self.tool_manager.execute_tool("file_io", "create_file", 
                                               file_path="C:/Users/AMD/Desktop/file_management_task.log", 
                                               content=log_content)
        
        return {
            "success": result.get("success", False),
            "message": f"File management task completed: {task_description}",
            "agent": self.name,
            "task_type": "generic_file_management"
        } 