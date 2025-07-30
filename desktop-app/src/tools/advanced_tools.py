"""
Advanced Tools System for Cognitive Forge
Provides real file I/O, shell execution, and system interaction capabilities
"""

import os
import subprocess
import json
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger
from crewai_tools import BaseTool


class FileTools:
    """Advanced file system operations with safety checks"""
    
    ALLOWED_EXTENSIONS = {'.py', '.js', '.html', '.css', '.json', '.txt', '.md', '.yml', '.yaml'}
    
    @staticmethod
    def write_file(file_path: str, content: str) -> str:
        """Safely write content to a file with directory creation"""
        try:
            # Ensure the file has an allowed extension
            if not any(file_path.endswith(ext) for ext in FileTools.ALLOWED_EXTENSIONS):
                return f"Error: File extension not allowed. Allowed: {FileTools.ALLOWED_EXTENSIONS}"
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            logger.info(f"File written successfully: {file_path}")
            return f"File '{file_path}' has been written successfully with {len(content)} characters."
            
        except Exception as e:
            error_msg = f"Error writing file '{file_path}': {str(e)}"
            logger.error(error_msg)
            return error_msg

    @staticmethod
    def read_file(file_path: str) -> str:
        """Safely read content from a file"""
        try:
            if not os.path.exists(file_path):
                return f"Error: File '{file_path}' not found."
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            logger.info(f"File read successfully: {file_path}")
            return f"File content for '{file_path}':\n\n{content}"
            
        except Exception as e:
            error_msg = f"Error reading file '{file_path}': {str(e)}"
            logger.error(error_msg)
            return error_msg

    @staticmethod
    def list_files(directory: str = ".") -> str:
        """List files in a directory with details"""
        try:
            if not os.path.exists(directory):
                return f"Error: Directory '{directory}' not found."
            
            files = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path)
                    files.append(f"📄 {item} ({size} bytes)")
                else:
                    files.append(f"📁 {item}/")
            
            result = f"Contents of '{directory}':\n" + "\n".join(files)
            logger.info(f"Directory listed: {directory}")
            return result
            
        except Exception as e:
            error_msg = f"Error listing directory '{directory}': {str(e)}"
            logger.error(error_msg)
            return error_msg


class ShellTools:
    """Safe shell execution with command whitelisting"""
    
    ALLOWED_COMMANDS = {
        "ls", "dir", "pwd", "echo", "cat", "head", "tail", "grep", "find",
        "python", "pip", "node", "npm", "git", "mkdir", "touch", "cp", "mv",
        "python -m py_compile", "python -c", "pip list", "pip show"
    }
    
    @staticmethod
    def execute_shell_command(command: str) -> str:
        """Execute a shell command with safety checks"""
        try:
            # Extract the base command (first word)
            base_command = command.split()[0] if command.strip() else ""
            
            # Check if command is allowed
            if not any(command.startswith(allowed) for allowed in ShellTools.ALLOWED_COMMANDS):
                return f"Error: Command '{base_command}' is not permitted. Allowed commands: {list(ShellTools.ALLOWED_COMMANDS)}"
            
            # Execute with timeout and capture output
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True,
                timeout=60  # 60 second timeout
            )
            
            output = f"Command executed successfully:\nSTDOUT:\n{result.stdout}"
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"
            
            logger.info(f"Shell command executed: {command}")
            return output
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed with exit code {e.returncode}:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
            logger.error(f"Shell command failed: {command} - {error_msg}")
            return error_msg
            
        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out after 60 seconds: {command}"
            logger.error(f"Shell command timeout: {command}")
            return error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error executing command '{command}': {str(e)}"
            logger.error(error_msg)
            return error_msg


class SystemTools:
    """System information and monitoring tools"""
    
    @staticmethod
    def get_system_info() -> str:
        """Get comprehensive system information"""
        try:
            import psutil
            
            # CPU Info
            cpu_count = psutil.cpu_count()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory Info
            memory = psutil.virtual_memory()
            memory_total = memory.total / (1024**3)  # GB
            memory_used = memory.used / (1024**3)   # GB
            memory_percent = memory.percent
            
            # Disk Info
            disk = psutil.disk_usage('/')
            disk_total = disk.total / (1024**3)     # GB
            disk_used = disk.used / (1024**3)       # GB
            disk_percent = (disk.used / disk.total) * 100
            
            info = f"""System Information:
CPU: {cpu_count} cores, {cpu_percent}% usage
Memory: {memory_used:.1f}GB / {memory_total:.1f}GB ({memory_percent}% used)
Disk: {disk_used:.1f}GB / {disk_total:.1f}GB ({disk_percent:.1f}% used)
Platform: {os.name}
Python: {os.sys.version}
"""
            
            logger.info("System information retrieved")
            return info
            
        except Exception as e:
            error_msg = f"Error getting system info: {str(e)}"
            logger.error(error_msg)
            return error_msg

    @staticmethod
    def check_process_status(process_name: str) -> str:
        """Check if a specific process is running"""
        try:
            import psutil
            
            for proc in psutil.process_iter(['pid', 'name']):
                if process_name.lower() in proc.info['name'].lower():
                    return f"Process '{process_name}' is running (PID: {proc.info['pid']})"
            
            return f"Process '{process_name}' is not running"
            
        except Exception as e:
            error_msg = f"Error checking process status: {str(e)}"
            logger.error(error_msg)
            return error_msg


class CodeAnalysisTools:
    """Advanced code analysis and manipulation tools"""
    
    @staticmethod
    def analyze_python_file(file_path: str) -> str:
        """Analyze a Python file for imports, functions, and classes"""
        try:
            if not file_path.endswith('.py'):
                return "Error: This tool only analyzes Python files."
            
            if not os.path.exists(file_path):
                return f"Error: File '{file_path}' not found."
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple analysis
            lines = content.split('\n')
            imports = [line.strip() for line in lines if line.strip().startswith(('import ', 'from '))]
            functions = [line.strip() for line in lines if line.strip().startswith('def ')]
            classes = [line.strip() for line in lines if line.strip().startswith('class ')]
            
            analysis = f"""Python File Analysis: {file_path}
Lines: {len(lines)}
Imports: {len(imports)}
Functions: {len(functions)}
Classes: {len(classes)}

Imports:
{chr(10).join(imports) if imports else 'None'}

Functions:
{chr(10).join(functions) if functions else 'None'}

Classes:
{chr(10).join(classes) if classes else 'None'}
"""
            
            logger.info(f"Python file analyzed: {file_path}")
            return analysis
            
        except Exception as e:
            error_msg = f"Error analyzing Python file '{file_path}': {str(e)}"
            logger.error(error_msg)
            return error_msg

    @staticmethod
    def validate_json(json_string: str) -> str:
        """Validate and format JSON string"""
        try:
            parsed = json.loads(json_string)
            formatted = json.dumps(parsed, indent=2)
            return f"Valid JSON:\n{formatted}"
        except json.JSONDecodeError as e:
            return f"Invalid JSON: {str(e)}"


# Export all tools for easy access
__all__ = ['FileTools', 'ShellTools', 'SystemTools', 'CodeAnalysisTools'] 