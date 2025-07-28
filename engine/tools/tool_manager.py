from typing import Dict, Any, List
from loguru import logger
import os
import subprocess
import platform
from datetime import datetime
import json

class FileIOTool:
    """Tool for file operations on the desktop."""
    
    def __init__(self):
        self.name = "file_io_tool"
        self.description = "Create, read, write, and delete files on the desktop"
    
    def create_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Create a new file with the specified content."""
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "message": f"File created successfully: {file_path}",
                "file_path": file_path,
                "file_size": len(content)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read the contents of a file."""
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File does not exist: {file_path}"
                }
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "file_path": file_path,
                "file_size": len(content)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """Delete a file."""
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File does not exist: {file_path}"
                }
            
            os.remove(file_path)
            return {
                "success": True,
                "message": f"File deleted successfully: {file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class ShellCommandTool:
    """Tool for executing shell commands on the desktop."""
    
    def __init__(self):
        self.name = "shell_command_tool"
        self.description = "Execute shell commands on the desktop"
    
    def execute_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute a shell command."""
        try:
            if platform.system() == "Windows":
                # Use PowerShell for Windows
                result = subprocess.run(
                    ["powershell", "-Command", command],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
            else:
                # Use bash for Unix-like systems
                result = subprocess.run(
                    ["bash", "-c", command],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "command": command
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds",
                "command": command
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command
            }

class SystemInfoTool:
    """Tool for getting system information."""
    
    def __init__(self):
        self.name = "system_info_tool"
        self.description = "Get system information and status"
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get basic system information."""
        try:
            info = {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "architecture": platform.architecture()[0],
                "processor": platform.processor(),
                "current_time": datetime.now().isoformat(),
                "current_directory": os.getcwd(),
                "user_home": os.path.expanduser("~")
            }
            
            return {
                "success": True,
                "system_info": info
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_desktop_path(self) -> Dict[str, Any]:
        """Get the desktop path."""
        try:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            return {
                "success": True,
                "desktop_path": desktop_path,
                "exists": os.path.exists(desktop_path)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class ToolManager:
    """Manages all available tools for the engine agents."""
    
    def __init__(self):
        self.tools = {
            "file_io": FileIOTool(),
            "shell_command": ShellCommandTool(),
            "system_info": SystemInfoTool()
        }
        logger.info("ToolManager initialized with desktop tools")
    
    def get_tool(self, tool_name: str):
        """Get a specific tool by name."""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """List all available tools."""
        return list(self.tools.keys())
    
    def execute_tool(self, tool_name: str, method: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool method."""
        tool = self.get_tool(tool_name)
        if not tool:
            return {
                "success": False,
                "error": f"Tool not found: {tool_name}"
            }
        
        if not hasattr(tool, method):
            return {
                "success": False,
                "error": f"Method not found: {method} on tool {tool_name}"
            }
        
        try:
            result = getattr(tool, method)(**kwargs)
            logger.info(f"Tool {tool_name}.{method} executed successfully")
            return result
        except Exception as e:
            logger.error(f"Tool {tool_name}.{method} failed: {e}")
            return {
                "success": False,
                "error": str(e)
            } 