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

# Simple BaseTool class to replace crewai-tools dependency
class BaseTool:
    """Base class for tools to maintain compatibility"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement __call__")


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
            base_command = command.split()[0] if command.split() else ""
            
            # Check if command is allowed
            if base_command not in ShellTools.ALLOWED_COMMANDS:
                return f"Error: Command '{base_command}' is not allowed for security reasons."
            
            # Execute command
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                logger.info(f"Command executed successfully: {command}")
                return f"Command executed successfully:\n{output}"
            else:
                error = result.stderr.strip()
                logger.warning(f"Command failed: {command} - {error}")
                return f"Command failed:\n{error}"
                
        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out: {command}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error executing command '{command}': {str(e)}"
            logger.error(error_msg)
            return error_msg


class SystemTools:
    """System information and monitoring tools"""
    
    @staticmethod
    def get_system_info() -> str:
        """Get comprehensive system information"""
        try:
            import psutil
            import platform
            
            # CPU info
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory info
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_total = memory.total / (1024**3)  # GB
            
            # Disk info
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_total = disk.total / (1024**3)  # GB
            
            # Network info
            network = psutil.net_io_counters()
            bytes_sent = network.bytes_sent / (1024**2)  # MB
            bytes_recv = network.bytes_recv / (1024**2)  # MB
            
            info = f"""
System Information:
==================
Platform: {platform.platform()}
Python: {platform.python_version()}

CPU:
- Usage: {cpu_percent:.1f}%
- Cores: {cpu_count}

Memory:
- Usage: {memory_percent:.1f}%
- Total: {memory_total:.1f} GB

Disk:
- Usage: {disk_percent:.1f}%
- Total: {disk_total:.1f} GB

Network:
- Bytes Sent: {bytes_sent:.1f} MB
- Bytes Received: {bytes_recv:.1f} MB
"""
            
            logger.info("System information retrieved")
            return info
            
        except Exception as e:
            error_msg = f"Error getting system info: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    @staticmethod
    def check_process_status(process_name: str) -> str:
        """Check if a process is running"""
        try:
            import psutil
            
            running_processes = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if process_name.lower() in proc.info['name'].lower():
                        running_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if running_processes:
                result = f"Found {len(running_processes)} process(es) matching '{process_name}':\n"
                for proc in running_processes:
                    result += f"- PID {proc['pid']}: {proc['name']}\n"
            else:
                result = f"No processes found matching '{process_name}'"
            
            logger.info(f"Process status checked for: {process_name}")
            return result
            
        except Exception as e:
            error_msg = f"Error checking process status: {str(e)}"
            logger.error(error_msg)
            return error_msg


class CodeAnalysisTools:
    """Code analysis and validation tools"""
    
    @staticmethod
    def analyze_python_file(file_path: str) -> str:
        """Analyze a Python file for syntax and style"""
        try:
            if not os.path.exists(file_path):
                return f"Error: File '{file_path}' not found."
            
            if not file_path.endswith('.py'):
                return f"Error: File '{file_path}' is not a Python file."
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = {
                'file_path': file_path,
                'size': len(content),
                'lines': len(content.splitlines()),
                'syntax_valid': True,
                'issues': []
            }
            
            # Check syntax
            try:
                compile(content, file_path, 'exec')
            except SyntaxError as e:
                analysis['syntax_valid'] = False
                analysis['issues'].append(f"Syntax error: {e}")
            
            # Basic style checks
            lines = content.splitlines()
            for i, line in enumerate(lines, 1):
                if len(line) > 79:
                    analysis['issues'].append(f"Line {i}: Line too long ({len(line)} chars)")
                if line.strip() and not line.startswith(' ') and line.endswith(' '):
                    analysis['issues'].append(f"Line {i}: Trailing whitespace")
            
            # Generate report
            report = f"""
Code Analysis for {file_path}:
==============================
File Size: {analysis['size']} characters
Lines: {analysis['lines']}
Syntax Valid: {'Yes' if analysis['syntax_valid'] else 'No'}

Issues Found: {len(analysis['issues'])}
"""
            
            if analysis['issues']:
                report += "\nIssues:\n"
                for issue in analysis['issues']:
                    report += f"- {issue}\n"
            else:
                report += "\n✅ No issues found!"
            
            logger.info(f"Code analysis completed for: {file_path}")
            return report
            
        except Exception as e:
            error_msg = f"Error analyzing Python file: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    @staticmethod
    def validate_json(json_string: str) -> str:
        """Validate JSON string"""
        try:
            parsed = json.loads(json_string)
            return f"✅ Valid JSON with {len(parsed)} top-level keys"
        except json.JSONDecodeError as e:
            return f"❌ Invalid JSON: {str(e)}"
        except Exception as e:
            return f"❌ Error validating JSON: {str(e)}" 