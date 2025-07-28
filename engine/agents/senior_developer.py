from typing import Dict, Any
from loguru import logger

class SeniorDeveloper:
    """Senior Developer agent for executing development tasks on the desktop."""
    
    def __init__(self, llm_client=None, tool_manager=None, **kwargs):
        self.llm_client = llm_client
        self.tool_manager = tool_manager
        self.name = "Senior Developer"
        self.role = "senior_developer"
        self.goal = "Execute development tasks, create code files, and manage development workflows"
        self.backstory = """You are a senior software developer with 10+ years of experience. 
        You excel at writing clean, efficient code and can handle complex development tasks. 
        You work directly on the desktop to create, modify, and manage code files."""
        
        logger.info(f"SeniorDeveloper agent initialized")
    
    async def execute_task(self, task_description: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a development task."""
        try:
            logger.info(f"SeniorDeveloper executing task: {task_description}")
            
            # Determine the type of task and execute accordingly
            if "create" in task_description.lower() and "file" in task_description.lower():
                return await self._create_file_task(parameters)
            elif "code" in task_description.lower() or "script" in task_description.lower():
                return await self._create_code_task(parameters)
            elif "modify" in task_description.lower() or "edit" in task_description.lower():
                return await self._modify_file_task(parameters)
            else:
                return await self._generic_development_task(task_description, parameters)
                
        except Exception as e:
            logger.error(f"SeniorDeveloper task failed: {e}")
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
        
        result = self.tool_manager.execute_tool("file_io", "create_file", 
                                               file_path=file_path, content=content)
        
        return {
            "success": result.get("success", False),
            "message": result.get("message", result.get("error", "Unknown error")),
            "agent": self.name,
            "task_type": "file_creation"
        }
    
    async def _create_code_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a code file with proper structure."""
        file_path = parameters.get("file_path")
        language = parameters.get("language", "python")
        content = parameters.get("content", "")
        
        if not file_path:
            return {
                "success": False,
                "error": "file_path is required",
                "agent": self.name
            }
        
        # Add language-specific headers if needed
        if language == "python" and not content.startswith("#"):
            content = f"# {file_path}\n# Created by Sentinel AI Senior Developer\n\n{content}"
        elif language == "javascript" and not content.startswith("//"):
            content = f"// {file_path}\n// Created by Sentinel AI Senior Developer\n\n{content}"
        
        result = self.tool_manager.execute_tool("file_io", "create_file", 
                                               file_path=file_path, content=content)
        
        return {
            "success": result.get("success", False),
            "message": result.get("message", result.get("error", "Unknown error")),
            "agent": self.name,
            "task_type": "code_creation",
            "language": language
        }
    
    async def _modify_file_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Modify an existing file."""
        file_path = parameters.get("file_path")
        new_content = parameters.get("content", "")
        
        if not file_path:
            return {
                "success": False,
                "error": "file_path is required",
                "agent": self.name
            }
        
        result = self.tool_manager.execute_tool("file_io", "create_file", 
                                               file_path=file_path, content=new_content)
        
        return {
            "success": result.get("success", False),
            "message": result.get("message", result.get("error", "Unknown error")),
            "agent": self.name,
            "task_type": "file_modification"
        }
    
    async def _generic_development_task(self, task_description: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generic development tasks."""
        # For now, create a log file with the task description
        log_content = f"Task: {task_description}\nParameters: {parameters}\nStatus: Completed by {self.name}"
        
        result = self.tool_manager.execute_tool("file_io", "create_file", 
                                               file_path="C:/Users/AMD/Desktop/development_task.log", 
                                               content=log_content)
        
        return {
            "success": result.get("success", False),
            "message": f"Development task logged: {task_description}",
            "agent": self.name,
            "task_type": "generic_development"
        } 