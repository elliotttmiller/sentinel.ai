"""
Dependency-Free File System Tools for Real Agent Execution
Provides the same functionality as the original tools but without external dependencies
"""

import os
import subprocess
import sys
from datetime import datetime

# Simple replacement for pydantic BaseModel
class SimpleBaseModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class SimpleLogger:
    @staticmethod
    def info(msg): print(f"[INFO] {msg}")
    @staticmethod 
    def success(msg): print(f"[SUCCESS] ✅ {msg}")
    @staticmethod
    def warning(msg): print(f"[WARNING] ⚠️ {msg}")
    @staticmethod
    def error(msg): print(f"[ERROR] ❌ {msg}")

logger = SimpleLogger()

# Simple replacement for CrewAI BaseTool
class SimpleBaseTool:
    def __init__(self):
        self.name = getattr(self, 'name', 'Simple Tool')
        self.description = getattr(self, 'description', 'Simple tool description')
    
    def _run(self, **kwargs):
        return "Tool execution not implemented"

# Import the standalone sandbox executor
try:
    from .sandbox_executor import SandboxExecutor
    sandbox = SandboxExecutor()
except ImportError:
    # Create a simple sandbox if the main one isn't available
    class SimpleSandbox:
        def __init__(self):
            self.workspace_dir = os.path.abspath("workspace")
            os.makedirs(self.workspace_dir, exist_ok=True)
        
        def create_file(self, file_path: str, content: str) -> str:
            file_path = file_path.lstrip('/')
            host_path = os.path.join(self.workspace_dir, file_path)
            abs_host_path = os.path.abspath(host_path)
            abs_workspace = os.path.abspath(self.workspace_dir)
            
            if not abs_host_path.startswith(abs_workspace):
                return f"Error: Path traversal detected. Attempted path: {file_path}"
                
            try:
                os.makedirs(os.path.dirname(abs_host_path), exist_ok=True)
                with open(abs_host_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return f"Successfully created file: {file_path} ({len(content)} characters)"
            except Exception as e:
                return f"Failed to create file '{file_path}': {str(e)}"
        
        def execute_command(self, command: str) -> str:
            safe_commands = ['ls', 'cat', 'python', 'pip', 'mkdir', 'echo', 'pwd', 'find']
            command_parts = command.split()
            
            if not command_parts or command_parts[0] not in safe_commands:
                return f"Error: Command '{command_parts[0] if command_parts else 'empty'}' not allowed."
            
            try:
                result = subprocess.run(command, shell=True, cwd=self.workspace_dir,
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    return f"Command executed successfully:\n{result.stdout or 'No output'}"
                else:
                    return f"Command failed:\n{result.stderr or 'Unknown error'}"
            except Exception as e:
                return f"Execution error: {str(e)}"
    
    sandbox = SimpleSandbox()

class CreateFileTool(SimpleBaseTool):
    name = "Create File"
    description = "Creates a new file with specified content in the workspace."
    
    def _run(self, file_path: str, content: str) -> str:
        """Create a file using the sandbox executor"""
        logger.info(f"🔧 Creating file: {file_path}")
        result = sandbox.create_file(file_path, content)
        logger.success(f"✅ File creation result: {result}")
        return result

class ExecutePythonFileTool(SimpleBaseTool):
    name = "Execute Python File"
    description = "Executes a Python file in the sandboxed environment."
    
    def _run(self, file_path: str) -> str:
        """Execute a Python file using the sandbox executor"""
        logger.info(f"🔧 Executing Python file: {file_path}")
        result = sandbox.execute_command(f"python {file_path}")
        logger.success(f"✅ Python execution result: {result[:200]}...")
        return result

class ListDirectoryTool(SimpleBaseTool):
    name = "List Directory"
    description = "Lists the contents of a specified directory in the workspace."
    
    def _run(self, path: str) -> str:
        """List directory contents using the sandbox executor"""
        logger.info(f"🔧 Listing directory: {path}")
        result = sandbox.execute_command(f"ls -la {path}")
        logger.success(f"✅ Directory listing result: {result[:200]}...")
        return result

class ReadFileTool(SimpleBaseTool):
    name = "Read File"
    description = "Reads the contents of a file in the workspace."
    
    def _run(self, file_path: str) -> str:
        """Read a file using the sandbox executor"""
        logger.info(f"🔧 Reading file: {file_path}")
        result = sandbox.execute_command(f"cat {file_path}")
        logger.success(f"✅ File read result: {result[:200]}...")
        return result

class InstallPackageTool(SimpleBaseTool):
    name = "Install Python Package"
    description = "Installs a Python package using pip in the sandboxed environment."
    
    def _run(self, package_name: str) -> str:
        """Install a Python package using the sandbox executor"""
        logger.info(f"🔧 Installing package: {package_name}")
        result = sandbox.execute_command(f"pip install {package_name}")
        logger.success(f"✅ Package installation result: {result[:200]}...")
        return result

class CreateDirectoryTool(SimpleBaseTool):
    name = "Create Directory"
    description = "Creates a new directory in the workspace."
    
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

# Test function to verify tools work
def test_tools():
    """Test that all tools are working"""
    print("🧪 Testing File System Tools...")
    
    # Test file creation
    create_tool = CreateFileTool()
    result = create_tool._run("test_tools_output.txt", "This file was created by the file system tools test!")
    print(f"File creation: {result}")
    
    # Test directory listing
    list_tool = ListDirectoryTool()
    result = list_tool._run(".")
    print(f"Directory listing: {result[:100]}...")
    
    # Test file reading
    read_tool = ReadFileTool()
    result = read_tool._run("test_tools_output.txt")
    print(f"File reading: {result}")
    
    print("✅ Tools test completed!")

if __name__ == "__main__":
    test_tools()