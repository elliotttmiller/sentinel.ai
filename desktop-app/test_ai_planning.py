#!/usr/bin/env python3
"""
Test AI Planning Generation
Simple test to see what the AI is generating for planning
"""

import os
import sys
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.advanced_agents import PlannerAgents
from crewai import Task, Crew, Process

# Load environment variables
load_dotenv()

def test_ai_planning():
    """Test what the AI is generating for planning"""
    print("🧪 Testing AI Planning Generation...")
    
    try:
        # Initialize LLM
        model_name = os.getenv("LLM_MODEL", "gemini-1.5-pro-latest")
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        
        llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
        print(f"✅ LLM initialized: {model_name}")
        
        # Initialize planner agents
        planner_agents = PlannerAgents()
        
        # Create a simple test prompt
        test_prompt = "Create a test file on my desktop called 'sentinel_test.txt' with the message 'Hello from Sentinel AI!'"
        
        print(f"📝 Test prompt: {test_prompt}")
        
        # Create the Lead Architect agent
        architect = planner_agents.lead_architect(llm)
        
        planning_task = Task(
            description=f"""User's high-level goal: '{test_prompt}'
            
            Your task is to generate a JSON execution plan. The JSON must have a 'steps' array. 
            Each step object in the array must have the following keys: 
            - 'step_id': A unique identifier for the step
            - 'agent_role': The role to execute this step ('senior_developer', 'qa_tester', 'code_analyzer', 'system_integrator')
            - 'task_description': A crystal-clear description of what this step should accomplish
            - 'expected_output': A precise description of what this step should produce
            
            Available agent roles: 'senior_developer', 'qa_tester', 'code_analyzer', 'system_integrator'
            
            Consider the complexity of the task and assign the most appropriate agent for each step.
            Respond ONLY with the raw JSON object.""",
            expected_output="A valid JSON object representing the execution plan.",
            agent=architect,
        )
        
        # Create the Plan Validator agent
        validator = planner_agents.plan_validator(llm)
        
        validation_task = Task(
            description="""Review the generated JSON plan for:
            1. Valid JSON syntax
            2. Required fields: 'steps', 'agent_role', 'task_description', 'expected_output'
            3. Logical sequence and flow
            4. Appropriate agent assignments
            
            If valid, output the JSON as-is. If invalid, provide clear correction instructions.""",
            expected_output="The validated JSON plan or correction instructions.",
            agent=validator,
        )
        
        # Execute planning crew with validation
        planning_crew = Crew(
            agents=[architect, validator],
            tasks=[planning_task, validation_task],
            process=Process.sequential,
            verbose=True,
        )
        
        print("🔍 Generating execution plan...")
        plan_str = planning_crew.kickoff()
        
        print("\n📋 Generated Plan:")
        print("=" * 50)
        print(plan_str)
        print("=" * 50)
        
        # Try to parse the plan
        try:
            # First try to parse as-is
            plan = json.loads(plan_str)
            print("✅ Plan parsed successfully as JSON!")
            print(f"📊 Plan has {len(plan.get('steps', []))} steps")
            return True
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract JSON from markdown code blocks
            print("⚠️ Failed to parse plan as JSON, attempting to extract from markdown...")
            
            # Look for JSON code blocks
            import re
            json_pattern = r'```(?:json)?\s*\n(.*?)\n```'
            matches = re.findall(json_pattern, plan_str, re.DOTALL)
            
            if matches:
                # Try the first match
                json_content = matches[0].strip()
                try:
                    plan = json.loads(json_content)
                    print("✅ Plan extracted from markdown successfully!")
                    print(f"📊 Plan has {len(plan.get('steps', []))} steps")
                    return True
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse extracted JSON: {e}")
                    print(f"🔍 Extracted content: {json_content}")
            
            # If still failing, try to find any JSON-like structure
            try:
                # Remove markdown and try to find JSON
                cleaned = plan_str.replace('```json', '').replace('```', '').strip()
                plan = json.loads(cleaned)
                print("✅ Plan cleaned and parsed successfully!")
                print(f"📊 Plan has {len(plan.get('steps', []))} steps")
                return True
            except json.JSONDecodeError:
                print(f"❌ All JSON parsing attempts failed. Raw response: {plan_str}")
                return False
            
    except Exception as e:
        print(f"❌ Error testing AI planning: {e}")
        return False

if __name__ == "__main__":
    print("🧪 AI Planning Test")
    print("=" * 50)
    
    if test_ai_planning():
        print("\n✅ AI planning test completed successfully!")
    else:
        print("\n❌ AI planning test failed!") 