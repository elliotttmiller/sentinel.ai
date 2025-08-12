"""
Secure File System Tools for Real Agent Execution
Each tool provides a controlled interface for agents to interact with the environment
"""

from typing import Type, Any
from pydantic import BaseModel, Field
import os
from loguru import logger

# Import CrewAI tools with fallback
try:
    # Corrected import path for BaseTool
    from crewai_tools.tools.base_tool import BaseTool
    CREWAI_TOOLS_AVAILABLE = True
    logger.info("CrewAI tools imported successfully")
except ImportError:
    logger.warning(f"CrewAI tools import failed. Creating fallback BaseTool.")
    CREWAI_TOOLS_AVAILABLE = False
    
    # Simple fallback BaseTool that matches CrewAI interface
    class BaseTool:
        name: str = "Fallback Tool"
        description: str = "Fallback tool implementation"
        args_schema: Type[BaseModel] = None
        
        def __init__(self, **kwargs):
            # Set defaults if not already set by subclass
            if not hasattr(self.__class__, 'name') or self.__class__.name == "Fallback Tool":
                self.name = getattr(self, 'name', 'Fallback Tool')
            if not hasattr(self.__class__, 'description') or self.__class__.description == "Fallback tool implementation":
                self.description = getattr(self, 'description', 'Fallback tool implementation')
            if not hasattr(self.__class__, 'args_schema'):
                self.args_schema = getattr(self, 'args_schema', None)
        
        def _run(self, **kwargs):
            # Fallback implementation - just log the action
            logger.info(f"Fallback tool execution: {self.name} with args: {kwargs}")
            return f"Fallback execution of {self.name}: {kwargs}"

# Import our sandboxed executor
from src.core.sandbox_executor import SandboxExecutor

# Initialize the sandbox once to be reused by all tools
sandbox = SandboxExecutor()

class CreateFileToolInput(BaseModel):
    """Input for creating a file."""
    file_path: str = Field(description="The path to the file to be created, relative to the workspace.")
    content: str = Field(description="The content to write into the file.")

class CreateFileTool(BaseTool):
    name: str = "Create File"
    description: str = "Creates a new file with specified content in the workspace."
    args_schema: Type[BaseModel] = CreateFileToolInput
    
    def _run(self, file_path: str, content: str) -> str:
        """Create a file using the sandbox executor"""
        logger.info(f"🔧 Creating file: {file_path}")
        result = sandbox.create_file(file_path, content)
        logger.success(f"✅ File creation result: {result}")
        return result

class ExecutePythonFileToolInput(BaseModel):
    """Input for executing a Python file."""
    file_path: str = Field(description="The path to the Python file to be executed, relative to the workspace.")

class ExecutePythonFileTool(BaseTool):
    name: str = "Execute Python File"
    description: str = "Executes a Python file in the sandboxed environment."
    args_schema: Type[BaseModel] = ExecutePythonFileToolInput

    def _run(self, file_path: str) -> str:
        """Execute a Python file using the sandbox executor"""
        logger.info(f"🔧 Executing Python file: {file_path}")
        result = sandbox.execute_command(f"python {file_path}")
        logger.success(f"✅ Python execution result: {result[:200]}...")
        return result

class ListDirectoryToolInput(BaseModel):
    """Input for listing directory contents."""
    path: str = Field(description="The path of the directory to list, relative to the workspace. Use '.' for the root.")

class ListDirectoryTool(BaseTool):
    name: str = "List Directory"
    description: str = "Lists the contents of a specified directory in the workspace."
    args_schema: Type[BaseModel] = ListDirectoryToolInput

    def _run(self, path: str) -> str:
        """List directory contents using the sandbox executor"""
        logger.info(f"🔧 Listing directory: {path}")
        result = sandbox.execute_command(f"ls -la {path}")
        logger.success(f"✅ Directory listing result: {result[:200]}...")
        return result

class ReadFileToolInput(BaseModel):
    """Input for reading a file."""
    file_path: str = Field(description="The path to the file to be read, relative to the workspace.")

class ReadFileTool(BaseTool):
    name: str = "Read File"
    description: str = "Reads the contents of a file in the workspace."
    args_schema: Type[BaseModel] = ReadFileToolInput

    def _run(self, file_path: str) -> str:
        """Read a file using the sandbox executor"""
        logger.info(f"🔧 Reading file: {file_path}")
        result = sandbox.execute_command(f"cat {file_path}")
        logger.success(f"✅ File read result: {result[:200]}...")
        return result

class InstallPackageToolInput(BaseModel):
    """Input for installing a Python package."""
    package_name: str = Field(description="The name of the Python package to install (e.g., 'flask', 'requests').")

class InstallPackageTool(BaseTool):
    name: str = "Install Python Package"
    description: str = "Installs a Python package using pip in the sandboxed environment."
    args_schema: Type[BaseModel] = InstallPackageToolInput

    def _run(self, package_name: str) -> str:
        """Install a Python package using the sandbox executor"""
        logger.info(f"🔧 Installing package: {package_name}")
        result = sandbox.execute_command(f"pip install {package_name}")
        logger.success(f"✅ Package installation result: {result[:200]}...")
        return result

class CreateDirectoryToolInput(BaseModel):
    """Input for creating a directory."""
    dir_path: str = Field(description="The path of the directory to create, relative to the workspace.")

class CreateDirectoryTool(BaseTool):
    name: str = "Create Directory"
    description: str = "Creates a new directory in the workspace."
    args_schema: Type[BaseModel] = CreateDirectoryToolInput

    def _run(self, dir_path: str) -> str:
        """Create a directory using the sandbox executor"""
        logger.info(f"🔧 Creating directory: {dir_path}")
        result = sandbox.execute_command(f"mkdir -p {dir_path}")
        logger.success(f"✅ Directory creation result: {result}")
        return result

# Export all available tools
ALL_TOOLS = [
    CreateFileTool(),
    ExecutePythonFileTool(),
    ListDirectoryTool(),
    ReadFileTool(),
    InstallPackageTool(),
    CreateDirectoryTool()
]
