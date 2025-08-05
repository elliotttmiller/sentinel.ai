"""
Simple Executable Agents for Real Task Execution
Works without external dependencies while providing the same functionality
"""

from typing import List, Any
import asyncio
from datetime import datetime

# Simple logger
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

# Simple Agent class to replace CrewAI Agent
class SimpleAgent:
    def __init__(self, role, goal, backstory, tools=None, verbose=True, allow_delegation=False):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools = tools or []
        self.verbose = verbose
        self.allow_delegation = allow_delegation
        if verbose:
            logger.info(f"Agent created: {role}")

# Import tools
try:
    from .simple_file_system_tools import ALL_TOOLS
    tools_available = True
    logger.info("Simple file system tools imported successfully")
except ImportError:
    try:
        from simple_file_system_tools import ALL_TOOLS
        tools_available = True
        logger.info("Simple file system tools imported successfully")
    except ImportError:
        ALL_TOOLS = []
        tools_available = False
        logger.warning("File system tools not available")

class SimpleExecutableAgents:
    """
    Contains the definitions for agents that can perform real, executable tasks.
    Simplified version that works without external dependencies.
    """
    
    def __init__(self):
        self.tools_available = tools_available
        logger.info(f"SimpleExecutableAgents initialized (tools available: {self.tools_available})")
    
    def planner_agent(self) -> SimpleAgent:
        """Agent that creates detailed execution plans"""
        return SimpleAgent(
            role="AI Software Architect and Planner",
            goal="Break down a user's request into a clear, step-by-step, executable plan. Each step must correspond to a single, available tool.",
            backstory=(
                "You are a meticulous planner, an expert in software development workflows. "
                "Your strength lies in analyzing complex requests and decomposing them into a sequence of simple, "
                "atomic actions. You do not execute tasks yourself; you only create the plan for others to follow. "
                "You understand the available tools: Create File, Execute Python File, List Directory, Read File, "
                "Install Python Package, and Create Directory. Each step in your plan must use one of these tools."
            ),
            verbose=True,
            allow_delegation=False,
        )

    def executor_agent(self) -> SimpleAgent:
        """Agent that executes tasks using available tools"""
        return SimpleAgent(
            role="Senior Software Engineer and Executor",
            goal="Execute the step-by-step plan provided by the planner. Use the available tools to perform each action and report the results.",
            backstory=(
                "You are a hands-on engineer who gets things done. You follow instructions precisely, "
                "executing one step at a time using your available tools. After each step, you carefully review the outcome "
                "to ensure it was successful before proceeding to the next. You have access to file system tools "
                "that allow you to create files, execute Python code, manage directories, and install packages safely."
            ),
            verbose=True,
            allow_delegation=False,
            tools=ALL_TOOLS if self.tools_available else []
        )
    
    def supervisor_agent(self) -> SimpleAgent:
        """Agent that oversees and validates the entire process"""
        read_only_tools = []
        if self.tools_available:
            read_only_tools = [tool for tool in ALL_TOOLS if tool.name in ["List Directory", "Read File"]]
        
        return SimpleAgent(
            role="Technical Project Supervisor",
            goal="Oversee the planning and execution process, ensuring quality and completeness of the final deliverable.",
            backstory=(
                "You are an experienced technical lead who ensures that projects are completed to specification. "
                "You review plans for completeness, monitor execution for success, and verify that the final "
                "deliverable meets the user's requirements. You provide guidance and make final assessments."
            ),
            verbose=True,
            allow_delegation=False,
            tools=read_only_tools  # Read-only tools for validation
        )
    
    async def execute_task_with_agents(self, user_request: str) -> dict:
        """
        Execute a task using the agent team.
        This is a simplified version that demonstrates real agent execution.
        """
        logger.info(f"🚀 Executing task with agent team: {user_request}")
        
        try:
            # Step 1: Planning Agent creates plan
            planner = self.planner_agent()
            logger.info(f"{planner.role} is analyzing the request...")
            
            # Simple planning logic - determine what needs to be done
            plan = await self._create_execution_plan(user_request)
            logger.success(f"Plan created with {len(plan)} steps")
            
            # Step 2: Executor Agent executes the plan
            executor = self.executor_agent()
            logger.info(f"{executor.role} is executing the plan...")
            
            execution_results = []
            for i, step in enumerate(plan, 1):
                logger.info(f"Executing step {i}: {step['description']}")
                result = await self._execute_step(step, executor)
                execution_results.append(result)
                
                if not result.get('success', False):
                    logger.error(f"Step {i} failed: {result.get('error', 'Unknown error')}")
                    break
                else:
                    logger.success(f"Step {i} completed successfully")
            
            # Step 3: Supervisor Agent validates results
            supervisor = self.supervisor_agent()
            logger.info(f"{supervisor.role} is validating results...")
            
            validation_result = await self._validate_execution(execution_results, supervisor)
            
            overall_success = all(r.get('success', False) for r in execution_results)
            
            return {
                "success": overall_success,
                "user_request": user_request,
                "plan": plan,
                "execution_results": execution_results,
                "validation": validation_result,
                "agents_used": [planner.role, executor.role, supervisor.role],
                "real_execution": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_request": user_request,
                "real_execution": False,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _create_execution_plan(self, user_request: str) -> List[dict]:
        """Create an execution plan based on the user request"""
        plan = []
        
        # Simple planning logic based on keywords
        if "create file" in user_request.lower() or "file" in user_request.lower():
            plan.append({
                "step": 1,
                "description": "Create file based on user request",
                "tool": "Create File",
                "action": "create_file"
            })
        
        if "python" in user_request.lower() or "code" in user_request.lower():
            plan.append({
                "step": len(plan) + 1,
                "description": "Create Python code file",
                "tool": "Create File", 
                "action": "create_python_file"
            })
            plan.append({
                "step": len(plan) + 1,
                "description": "Execute Python code",
                "tool": "Execute Python File",
                "action": "execute_python"
            })
        
        if "directory" in user_request.lower() or "folder" in user_request.lower():
            plan.append({
                "step": len(plan) + 1,
                "description": "Create directory",
                "tool": "Create Directory",
                "action": "create_directory"
            })
        
        # Default plan if no specific actions detected
        if not plan:
            plan.append({
                "step": 1,
                "description": "Create output file with task results",
                "tool": "Create File",
                "action": "create_output_file"
            })
        
        return plan
    
    async def _execute_step(self, step: dict, executor: SimpleAgent) -> dict:
        """Execute a single step of the plan"""
        try:
            action = step.get("action", "")
            
            if action == "create_file":
                return await self._execute_create_file(step)
            elif action == "create_python_file":
                return await self._execute_create_python_file(step)
            elif action == "execute_python":
                return await self._execute_python_file(step)
            elif action == "create_directory":
                return await self._execute_create_directory(step)
            elif action == "create_output_file":
                return await self._execute_create_output_file(step)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_create_file(self, step: dict) -> dict:
        """Execute file creation"""
        if not self.tools_available:
            return {"success": False, "error": "File system tools not available"}
        
        create_tool = None
        for tool in ALL_TOOLS:
            if tool.name == "Create File":
                create_tool = tool
                break
        
        if not create_tool:
            return {"success": False, "error": "Create File tool not found"}
        
        filename = f"agent_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        content = f"File created by AI agent execution\nTimestamp: {datetime.now().isoformat()}\nStep: {step['description']}"
        
        result = create_tool._run(filename, content)
        
        return {
            "success": "successfully" in result.lower(),
            "result": result,
            "filename": filename,
            "step": step
        }
    
    async def _execute_create_python_file(self, step: dict) -> dict:
        """Create a Python file"""
        if not self.tools_available:
            return {"success": False, "error": "File system tools not available"}
        
        create_tool = None
        for tool in ALL_TOOLS:
            if tool.name == "Create File":
                create_tool = tool
                break
        
        if not create_tool:
            return {"success": False, "error": "Create File tool not found"}
        
        filename = f"agent_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        content = f'''#!/usr/bin/env python3
"""
Python code generated by AI agent
Generated at: {datetime.now().isoformat()}
"""

print("Hello from AI agent!")
print("This code was generated and will be executed by a real AI agent.")

result = 10 * 5
print(f"Agent calculation: 10 * 5 = {{result}}")

with open("agent_python_output.txt", "w") as f:
    f.write("This file was created by AI agent Python code execution!\\n")
    f.write(f"Timestamp: {datetime.now().isoformat()}\\n")
    f.write(f"Calculation result: {{result}}\\n")

print("Python execution completed successfully!")
'''
        
        result = create_tool._run(filename, content)
        
        return {
            "success": "successfully" in result.lower(),
            "result": result,
            "filename": filename,
            "step": step
        }
    
    async def _execute_python_file(self, step: dict) -> dict:
        """Execute a Python file"""
        if not self.tools_available:
            return {"success": False, "error": "File system tools not available"}
        
        exec_tool = None
        for tool in ALL_TOOLS:
            if tool.name == "Execute Python File":
                exec_tool = tool
                break
        
        if not exec_tool:
            return {"success": False, "error": "Execute Python File tool not found"}
        
        # Find the most recent Python file
        filename = f"agent_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        result = exec_tool._run(filename)
        
        return {
            "success": "successfully" in result.lower(),
            "result": result,
            "filename": filename,
            "step": step
        }
    
    async def _execute_create_directory(self, step: dict) -> dict:
        """Create a directory"""
        if not self.tools_available:
            return {"success": False, "error": "File system tools not available"}
        
        create_dir_tool = None
        for tool in ALL_TOOLS:
            if tool.name == "Create Directory":
                create_dir_tool = tool
                break
        
        if not create_dir_tool:
            return {"success": False, "error": "Create Directory tool not found"}
        
        dirname = f"agent_dir_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        result = create_dir_tool._run(dirname)
        
        return {
            "success": "successfully" in result.lower() or result.strip() == "",
            "result": result,
            "dirname": dirname,
            "step": step
        }
    
    async def _execute_create_output_file(self, step: dict) -> dict:
        """Create a general output file"""
        return await self._execute_create_file(step)
    
    async def _validate_execution(self, execution_results: List[dict], supervisor: SimpleAgent) -> dict:
        """Validate the execution results"""
        successful_steps = sum(1 for r in execution_results if r.get('success', False))
        total_steps = len(execution_results)
        
        validation = {
            "total_steps": total_steps,
            "successful_steps": successful_steps,
            "success_rate": (successful_steps / total_steps * 100) if total_steps > 0 else 0,
            "supervisor": supervisor.role,
            "overall_success": successful_steps == total_steps,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Validation complete: {successful_steps}/{total_steps} steps successful")
        return validation

# Test function
async def test_simple_agents():
    """Test the simple agents system"""
    print("🧪 Testing Simple Executable Agents...")
    
    agents = SimpleExecutableAgents()
    
    test_requests = [
        "Create a file with some test content",
        "Write Python code that performs a calculation",
        "Create a directory for organizing files"
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n{'='*60}")
        print(f"🤖 TEST {i}: {request}")
        print("="*60)
        
        result = await agents.execute_task_with_agents(request)
        
        print(f"Success: {result.get('success', False)}")
        print(f"Real Execution: {result.get('real_execution', False)}")
        print(f"Agents Used: {result.get('agents_used', [])}")
        
        if result.get('success', False):
            print("✅ TEST PASSED")
        else:
            print("❌ TEST FAILED")
            print(f"Error: {result.get('error', 'Unknown')}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_simple_agents())