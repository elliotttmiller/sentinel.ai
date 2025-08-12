"""
AI Task Parser - Converts natural language prompts into executable task plans
Uses LLM to understand user intent and generate structured execution plans
"""

import json
import re
from typing import Dict, Any, List, Optional
from loguru import logger

# Import LLM wrapper
try:
    from ..utils.google_ai_wrapper import create_google_ai_llm
except ImportError:
    from utils.google_ai_wrapper import create_google_ai_llm


class AITaskParser:
    """Parses natural language prompts into executable task plans"""
    
    def __init__(self, llm=None):
        if llm is None:
            self.llm = create_google_ai_llm()
        else:
            self.llm = llm
        
        logger.info("AITaskParser initialized")
    
    async def parse_prompt_to_task_plan(self, prompt: str, mission_id: str = None) -> Dict[str, Any]:
        """Parse a natural language prompt into an executable task plan"""
        try:
            # Create a comprehensive parsing prompt
            parsing_prompt = f"""You are an AI Task Parser that converts user requests into executable task plans.

USER REQUEST: "{prompt}"

Your job is to analyze this request and create a structured task plan that can be executed by an automated agent.

TASK CLASSIFICATION:
Identify the primary task type from these options:
- create_webapp: Creating web applications, websites, HTML pages
- create_script: Creating scripts, code files, automation
- setup_project: Setting up development projects, folder structures
- file_operations: Creating, modifying, organizing files
- system_commands: Running commands, installing software
- data_processing: Processing, analyzing, transforming data
- generic: Other tasks not fitting above categories

RESPONSE FORMAT (JSON only):
{{
    "task_type": "primary_task_type",
    "name": "descriptive_task_name",
    "description": "detailed description of what will be executed",
    "executable_plan": {{
        "type": "task_type",
        "name": "project_or_file_name",
        "parameters": {{
            // Specific parameters based on task type
        }},
        "actions": [
            {{
                "type": "action_type",
                "description": "what this action does",
                "parameters": {{
                    // Action-specific parameters
                }}
            }}
        ]
    }},
    "expected_outputs": [
        "list of expected files, folders, or results"
    ],
    "estimated_time": "rough time estimate",
    "complexity": "low|medium|high"
}}

EXAMPLES:

User: "Create a simple website for my portfolio"
{{
    "task_type": "create_webapp",
    "name": "portfolio_website",
    "description": "Create a portfolio website with HTML, CSS, and JavaScript",
    "executable_plan": {{
        "type": "create_webapp",
        "name": "portfolio",
        "parameters": {{
            "framework": "html",
            "includes_css": true,
            "includes_js": true
        }},
        "actions": [
            {{
                "type": "create_project_structure",
                "description": "Create website files",
                "parameters": {{
                    "structure_type": "html_website"
                }}
            }}
        ]
    }},
    "expected_outputs": ["index.html", "style.css", "script.js"],
    "estimated_time": "2-3 minutes",
    "complexity": "low"
}}

User: "Write a Python script to organize my files"
{{
    "task_type": "create_script",
    "name": "file_organizer_script",
    "description": "Create a Python script that organizes files by type",
    "executable_plan": {{
        "type": "create_script",
        "name": "file_organizer.py",
        "parameters": {{
            "language": "python",
            "functionality": "file_organization"
        }},
        "actions": [
            {{
                "type": "create_file",
                "description": "Create Python file organizer script",
                "parameters": {{
                    "filename": "file_organizer.py",
                    "content_type": "python_script"
                }}
            }}
        ]
    }},
    "expected_outputs": ["file_organizer.py"],
    "estimated_time": "3-5 minutes",
    "complexity": "medium"
}}

Now analyze the user request and provide the JSON response:"""

            # Get LLM response
            from langchain_core.messages import HumanMessage
            messages = [HumanMessage(content=parsing_prompt)]
            response = self.llm.invoke(messages)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Extract JSON from response
            task_plan = self._extract_json_from_response(response_text)
            
            # Enhance with execution details
            task_plan = self._enhance_task_plan(task_plan, prompt)
            
            logger.info(f"Task plan parsed successfully: {task_plan.get('task_type', 'unknown')}")
            return task_plan
            
        except Exception as e:
            logger.error(f"Failed to parse prompt to task plan: {e}")
            # Return fallback task plan
            return self._create_fallback_task_plan(prompt)
    
    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response text"""
        try:
            # Try to find JSON block
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                # Look for JSON-like content
                json_match = re.search(r'\\{.*\\}', response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(0)
                else:
                    json_text = response_text
            
            # Parse JSON
            return json.loads(json_text)
            
        except Exception as e:
            logger.error(f"Failed to extract JSON from response: {e}")
            return {}
    
    def _enhance_task_plan(self, task_plan: Dict[str, Any], original_prompt: str) -> Dict[str, Any]:
        """Enhance task plan with additional execution details"""
        if not task_plan:
            return self._create_fallback_task_plan(original_prompt)
        
        # Ensure required fields exist
        task_plan.setdefault("task_type", "generic")
        task_plan.setdefault("name", "unnamed_task")
        task_plan.setdefault("description", original_prompt)
        
        # Enhance executable_plan based on task_type
        executable_plan = task_plan.get("executable_plan", {})
        task_type = task_plan.get("task_type")
        
        if task_type == "create_webapp":
            executable_plan = self._enhance_webapp_plan(executable_plan, original_prompt)
        elif task_type == "create_script":
            executable_plan = self._enhance_script_plan(executable_plan, original_prompt)
        elif task_type == "setup_project":
            executable_plan = self._enhance_project_plan(executable_plan, original_prompt)
        else:
            executable_plan = self._enhance_generic_plan(executable_plan, original_prompt)
        
        task_plan["executable_plan"] = executable_plan
        return task_plan
    
    def _enhance_webapp_plan(self, plan: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Enhance web application creation plan"""
        plan.setdefault("type", "create_webapp")
        plan.setdefault("name", "webapp")
        plan.setdefault("framework", "html")
        
        # Determine framework based on prompt
        if "react" in prompt.lower():
            plan["framework"] = "react"
        elif "vue" in prompt.lower():
            plan["framework"] = "vue"
        elif "angular" in prompt.lower():
            plan["framework"] = "angular"
        else:
            plan["framework"] = "html"
        
        return plan
    
    def _enhance_script_plan(self, plan: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Enhance script creation plan"""
        plan.setdefault("type", "create_script")
        plan.setdefault("name", "script.py")
        
        # Determine language based on prompt
        if "python" in prompt.lower() or ".py" in prompt.lower():
            plan["language"] = "python"
            if not plan["name"].endswith(".py"):
                plan["name"] = plan["name"] + ".py"
        elif "javascript" in prompt.lower() or ".js" in prompt.lower():
            plan["language"] = "javascript"
            if not plan["name"].endswith(".js"):
                plan["name"] = plan["name"] + ".js"
        elif "bash" in prompt.lower() or "shell" in prompt.lower():
            plan["language"] = "bash"
            if not plan["name"].endswith(".sh"):
                plan["name"] = plan["name"] + ".sh"
        
        # Generate script content based on prompt
        plan["content"] = self._generate_script_content(plan, prompt)
        
        return plan
    
    def _enhance_project_plan(self, plan: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Enhance project setup plan"""
        plan.setdefault("type", "setup_project")
        plan.setdefault("name", "project")
        
        # Determine project type based on prompt
        if "python" in prompt.lower():
            plan["project_type"] = "python"
        elif "javascript" in prompt.lower() or "node" in prompt.lower():
            plan["project_type"] = "nodejs"
        elif "web" in prompt.lower() or "html" in prompt.lower():
            plan["project_type"] = "web"
        else:
            plan["project_type"] = "generic"
        
        return plan
    
    def _enhance_generic_plan(self, plan: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Enhance generic task plan"""
        plan.setdefault("type", "generic")
        
        # Parse for specific actions
        actions = []
        
        if "create file" in prompt.lower() or "make file" in prompt.lower():
            actions.append({
                "type": "create_file",
                "path": "output.txt",
                "content": f"# File created based on request: {prompt}"
            })
        
        if "run command" in prompt.lower() or "execute" in prompt.lower():
            actions.append({
                "type": "run_command",
                "command": "echo 'Command executed by Sentinel AI'"
            })
        
        plan["actions"] = actions
        return plan
    
    def _generate_script_content(self, plan: Dict[str, Any], prompt: str) -> str:
        """Generate script content based on the plan and prompt"""
        language = plan.get("language", "python")
        
        if language == "python":
            if "organize" in prompt.lower() and "file" in prompt.lower():
                return '''#!/usr/bin/env python3
"""
File Organizer Script
Created by Sentinel AI Agent
"""

import os
import shutil
from pathlib import Path

def organize_files(directory="."):
    """Organize files by extension"""
    directory = Path(directory)
    
    # File type mappings
    file_types = {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
        'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
        'audio': ['.mp3', '.wav', '.flac', '.aac'],
        'archives': ['.zip', '.rar', '.7z', '.tar', '.gz']
    }
    
    # Create directories
    for folder in file_types.keys():
        (directory / folder).mkdir(exist_ok=True)
    
    # Organize files
    for file_path in directory.iterdir():
        if file_path.is_file():
            extension = file_path.suffix.lower()
            moved = False
            
            for folder, extensions in file_types.items():
                if extension in extensions:
                    shutil.move(str(file_path), str(directory / folder / file_path.name))
                    print(f"Moved {file_path.name} to {folder}/")
                    moved = True
                    break
            
            if not moved:
                print(f"No category for {file_path.name}")

if __name__ == "__main__":
    organize_files()
    print("File organization complete!")'''
            else:
                return f'''#!/usr/bin/env python3
"""
Python Script
Created by Sentinel AI Agent based on: {prompt}
"""

def main():
    """Main function"""
    print("Hello from Sentinel AI Agent!")
    print("Task: {prompt}")
    
    # Add your code here
    pass

if __name__ == "__main__":
    main()'''
        
        elif language == "javascript":
            return f'''// JavaScript Script
// Created by Sentinel AI Agent based on: {prompt}

function main() {{
    console.log("Hello from Sentinel AI Agent!");
    console.log("Task: {prompt}");
    
    // Add your code here
}}

main();'''
        
        else:
            return f'# Script created by Sentinel AI Agent\n# Task: {prompt}\necho "Hello from Sentinel AI Agent!"'
    
    def _create_fallback_task_plan(self, prompt: str) -> Dict[str, Any]:
        """Create a fallback task plan when parsing fails"""
        return {
            "task_type": "generic",
            "name": "fallback_task",
            "description": f"Execute user request: {prompt}",
            "executable_plan": {
                "type": "generic",
                "name": "task_output",
                "actions": [
                    {
                        "type": "create_file",
                        "path": "task_output.txt",
                        "content": f"Task executed by Sentinel AI Agent\\nOriginal request: {prompt}\\nTimestamp: {logger.__version__}"
                    }
                ]
            },
            "expected_outputs": ["task_output.txt"],
            "estimated_time": "1-2 minutes",
            "complexity": "low"
        }
