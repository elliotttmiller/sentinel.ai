"""
Sandboxed Executor for Safe Command and File Execution
Uses Docker to provide isolated execution environment
"""

import os
import tempfile
import shutil
from loguru import logger
from pathlib import Path

# Import Docker with fallback
try:
    import docker
    DOCKER_AVAILABLE = True
    logger.info("Docker library imported successfully")
except ImportError:
    logger.warning("Docker library not available, using local execution only")
    DOCKER_AVAILABLE = False
    docker = None

class SandboxExecutor:
    """
    Manages a sandboxed environment using Docker for safe command and file execution.
    Falls back to local execution if Docker is not available.
    """
    
    def __init__(self, image_name="python:3.11-slim", workspace_dir="workspace"):
        self.workspace_dir = os.path.abspath(workspace_dir)
        self.image_name = image_name
        
        # Default to local execution - Docker is optional
        self.client = None
        self.docker_available = False
        
        # Only attempt Docker if explicitly enabled via environment variable
        use_docker = os.getenv("SENTINEL_USE_DOCKER", "false").lower() == "true"
        
        if use_docker and DOCKER_AVAILABLE:
            try:
                self.client = docker.from_env()
                # Test Docker connectivity
                self.client.ping()
                self.docker_available = True
                
                # Ensure the Python image is available locally
                try:
                    self.client.images.get(self.image_name)
                    logger.info(f"Docker image '{self.image_name}' found.")
                except docker.errors.ImageNotFound:
                    logger.info(f"Docker image '{self.image_name}' not found. Pulling from Docker Hub...")
                    self.client.images.pull(self.image_name)
                    logger.success(f"Successfully pulled Docker image '{self.image_name}'.")
                
                logger.success("Docker is available and ready for sandboxed execution.")
                
            except (docker.errors.DockerException, Exception) as e:
                logger.info(f"Docker not available: {e}. Using local execution.")
                self.client = None
                self.docker_available = False
        else:
            if use_docker:
                logger.info("Docker requested but not available. Using local execution.")
            else:
                logger.info("Using local execution mode (Docker disabled by default)")

        # Ensure the workspace directory exists on the host
        os.makedirs(self.workspace_dir, exist_ok=True)
        logger.info(f"Agent workspace initialized at: {self.workspace_dir}")

    def execute_command(self, command: str) -> str:
        """
        Executes a command in the sandboxed environment (Docker) or safely locally.
        """
        if self.docker_available:
            return self._execute_in_docker(command)
        else:
            return self._execute_locally_safe(command)
    
    def _execute_in_docker(self, command: str) -> str:
        """Execute command in Docker container"""
        try:
            logger.info(f"🐳 Executing in Docker: {command}")
            
            container = self.client.containers.run(
                self.image_name,
                command=f"sh -c 'cd /workspace && {command}'",
                volumes={self.workspace_dir: {'bind': '/workspace', 'mode': 'rw'}},
                working_dir="/workspace",
                detach=False,
                remove=True,  # Automatically remove the container when done
                stdout=True,
                stderr=True
            )
            
            output = container.decode('utf-8')
            logger.success(f"Docker command executed successfully.")
            return f"Command executed successfully in Docker:\n{output}"
            
        except docker.errors.ContainerError as e:
            error_output = e.stderr.decode('utf-8') if e.stderr else str(e)
            error_message = f"Docker execution error:\n{error_output}"
            logger.error(error_message)
            return error_message
            
        except Exception as e:
            error_message = f"Unexpected Docker error: {str(e)}"
            logger.error(error_message)
            return error_message
    
    def _execute_locally_safe(self, command: str) -> str:
        """Execute command locally with safety measures"""
        import subprocess
        
        # Security: Only allow safe commands
        safe_commands = ['ls', 'cat', 'python', 'pip', 'mkdir', 'echo', 'pwd', 'find']
        command_parts = command.split()
        
        if not command_parts or command_parts[0] not in safe_commands:
            return f"Error: Command '{command_parts[0] if command_parts else 'empty'}' not allowed in local execution mode."
        
        try:
            logger.info(f"💻 Executing locally (safe mode): {command}")
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            if result.returncode == 0:
                output = result.stdout or "Command completed successfully (no output)"
                logger.success("Local command executed successfully.")
                return f"Command executed successfully:\n{output}"
            else:
                error_output = result.stderr or "Unknown error"
                logger.error(f"Local command failed: {error_output}")
                return f"Command failed:\n{error_output}"
                
        except subprocess.TimeoutExpired:
            error_message = "Command timed out after 30 seconds"
            logger.error(error_message)
            return error_message
            
        except Exception as e:
            error_message = f"Local execution error: {str(e)}"
            logger.error(error_message)
            return error_message

    def create_file(self, file_path: str, content: str) -> str:
        """
        Safely creates a file inside the workspace directory.
        """
        # Normalize the path
        file_path = file_path.lstrip('/')  # Remove leading slashes
        host_path = os.path.join(self.workspace_dir, file_path)
        
        # Security: Prevent path traversal attacks
        abs_host_path = os.path.abspath(host_path)
        abs_workspace = os.path.abspath(self.workspace_dir)
        
        if not abs_host_path.startswith(abs_workspace):
            error_msg = f"Error: Path traversal detected. Attempted path: {file_path}"
            logger.error(error_msg)
            return error_msg
            
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(abs_host_path), exist_ok=True)
            
            # Write the file
            with open(abs_host_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            success_message = f"Successfully created file: {file_path} ({len(content)} characters)"
            logger.success(success_message)
            return success_message
            
        except Exception as e:
            error_message = f"Failed to create file '{file_path}': {str(e)}"
            logger.error(error_message)
            return error_message
    
    def get_workspace_path(self) -> str:
        """Return the absolute path to the workspace directory"""
        return self.workspace_dir
    
    def list_workspace_contents(self) -> str:
        """List all contents of the workspace"""
        try:
            contents = []
            for root, dirs, files in os.walk(self.workspace_dir):
                level = root.replace(self.workspace_dir, '').count(os.sep)
                indent = ' ' * 2 * level
                rel_root = os.path.relpath(root, self.workspace_dir)
                if rel_root == '.':
                    contents.append(f"{indent}📁 workspace/")
                else:
                    contents.append(f"{indent}📁 {rel_root}/")
                
                sub_indent = ' ' * 2 * (level + 1)
                for file in files:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    contents.append(f"{sub_indent}📄 {file} ({file_size} bytes)")
            
            return '\n'.join(contents) if contents else "Workspace is empty"
            
        except Exception as e:
            return f"Error listing workspace: {str(e)}"
