"""
Advanced Tools System for Cognitive Forge
Provides real file I/O, shell execution, and system interaction capabilities
"""

import os
import subprocess

from loguru import logger


# CrewAI-compatible tool classes
class BaseTool:
    """Base class for CrewAI-compatible tools"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def _run(self, *args, **kwargs):
        """Abstract method that must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _run")


class WriteFileTool(BaseTool):
    """Tool for writing content to files"""

    def __init__(self):
        super().__init__(
            name="write_file",
            description="Write content to a file. Args: file_path (str), content (str)",
        )

    def _run(self, file_path: str, content: str) -> str:
        """Safely write content to a file with directory creation"""
        try:
            # Ensure the file has an allowed extension
            allowed_extensions = {
                ".py",
                ".js",
                ".html",
                ".css",
                ".json",
                ".txt",
                ".md",
                ".yml",
                ".yaml",
            }
            if not any(file_path.endswith(ext) for ext in allowed_extensions):
                return (
                    f"Error: File extension not allowed. Allowed: {allowed_extensions}"
                )

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


class ReadFileTool(BaseTool):
    """Tool for reading content from files"""

    def __init__(self):
        super().__init__(
            name="read_file",
            description="Read content from a file. Args: file_path (str)",
        )

    def _run(self, file_path: str) -> str:
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


class ListFilesTool(BaseTool):
    """Tool for listing files in directories"""

    def __init__(self):
        super().__init__(
            name="list_files",
            description="List files in a directory. Args: directory (str, optional, default='.')",
        )

    def _run(self, directory: str = ".") -> str:
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


class ExecuteShellCommandTool(BaseTool):
    """Tool for executing shell commands safely"""

    def __init__(self):
        super().__init__(
            name="execute_shell_command",
            description="Execute a shell command safely. Args: command (str)",
        )
        self.ALLOWED_COMMANDS = {
            "python",
            "python3",
            "pip",
            "pip3",
            "echo",
            "ls",
            "dir",
            "cat",
            "type",
            "mkdir",
            "rmdir",
            "cp",
            "copy",
            "mv",
            "move",
            "rm",
            "del",
            "touch",
            "head",
            "tail",
            "grep",
            "find",
            "wc",
            "sort",
            "uniq",
            "cut",
            "awk",
            "sed",
            "tr",
            "tee",
            "chmod",
            "chown",
            "ln",
            "tar",
            "zip",
            "unzip",
            "curl",
            "wget",
            "git",
            "npm",
            "node",
            "npx",
            "yarn",
            "docker",
            "kubectl",
            "helm",
            "terraform",
            "ansible",
            "ssh",
            "scp",
            "rsync",
        }

    def _run(self, command: str) -> str:
        """Execute a shell command safely with whitelist validation"""
        try:
            # Extract the base command (first word)
            base_command = command.split()[0].lower()

            # Check if command is allowed
            if base_command not in self.ALLOWED_COMMANDS:
                return f"Error: Command '{base_command}' is not in the allowed list. Allowed commands: {list(self.ALLOWED_COMMANDS)}"

            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                logger.info(f"Command executed successfully: {command}")
                return f"Command executed successfully:\n{output}"
            else:
                error = result.stderr.strip()
                logger.warning(f"Command failed: {command} - {error}")
                return f"Command failed with error:\n{error}"

        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out: {command}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error executing command '{command}': {str(e)}"
            logger.error(error_msg)
            return error_msg


class AnalyzePythonFileTool(BaseTool):
    """Tool for analyzing Python files"""

    def __init__(self):
        super().__init__(
            name="analyze_python_file",
            description="Analyze a Python file for syntax and style. Args: file_path (str)",
        )

    def _run(self, file_path: str) -> str:
        """Analyze a Python file for syntax and style"""
        try:
            if not os.path.exists(file_path):
                return f"Error: File '{file_path}' not found."

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            analysis = []
            analysis.append(f"=== Python File Analysis: {file_path} ===")

            # Basic stats
            lines = content.split("\n")
            analysis.append(f"Total lines: {len(lines)}")
            analysis.append(f"Non-empty lines: {len([l for l in lines if l.strip()])}")
            analysis.append(f"Characters: {len(content)}")

            # Syntax check
            try:
                compile(content, file_path, "exec")
                analysis.append("✅ Syntax: Valid Python code")
            except SyntaxError as e:
                analysis.append(f"❌ Syntax Error: {e}")

            # Import analysis
            import_lines = [
                line
                for line in lines
                if line.strip().startswith("import ")
                or line.strip().startswith("from ")
            ]
            if import_lines:
                analysis.append(f"Imports ({len(import_lines)}):")
                for imp in import_lines[:5]:  # Show first 5 imports
                    analysis.append(f"  {imp.strip()}")
                if len(import_lines) > 5:
                    analysis.append(f"  ... and {len(import_lines) - 5} more")

            # Function/class analysis
            def_lines = [
                line
                for line in lines
                if line.strip().startswith("def ") or line.strip().startswith("class ")
            ]
            if def_lines:
                analysis.append(f"Functions/Classes ({len(def_lines)}):")
                for func in def_lines[:5]:  # Show first 5
                    analysis.append(f"  {func.strip()}")
                if len(def_lines) > 5:
                    analysis.append(f"  ... and {len(def_lines) - 5} more")

            result = "\n".join(analysis)
            logger.info(f"Python file analyzed: {file_path}")
            return result

        except Exception as e:
            error_msg = f"Error analyzing Python file '{file_path}': {str(e)}"
            logger.error(error_msg)
            return error_msg


# Create tool instances
write_file_tool = WriteFileTool()
read_file_tool = ReadFileTool()
list_files_tool = ListFilesTool()
execute_shell_command_tool = ExecuteShellCommandTool()
analyze_python_file_tool = AnalyzePythonFileTool()
