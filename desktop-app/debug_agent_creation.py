#!/usr/bin/env python3
"""
Debug Agent Creation
Test to identify the 'role' error in agent creation
"""

import os
import sys
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.advanced_agents import WorkerAgents
from crewai import Task, Crew, Process

# Load environment variables
load_dotenv()

def test_agent_creation():
    """Test agent creation to identify the 'role' error"""
    print("🧪 Testing Agent Creation...")
    
    try:
        # Initialize LLM
        model_name = os.getenv("LLM_MODEL", "gemini-1.5-pro-latest")
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        
        llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
        print(f"✅ LLM initialized: {model_name}")
        
        # Initialize worker agents
        worker_agents = WorkerAgents()
        print("✅ Worker agents initialized")
        
        # Test creating each agent
        agents_map = {
            "senior_developer": worker_agents.senior_developer(llm),
            "qa_tester": worker_agents.qa_tester(llm),
            "code_analyzer": worker_agents.code_analyzer(llm),
            "system_integrator": worker_agents.system_integrator(llm),
        }
        
        print("✅ All agents created successfully")
        
        # Test accessing agent properties
        for role, agent in agents_map.items():
            print(f"🔍 Testing agent: {role}")
            print(f"   Role: {agent.role}")
            print(f"   Goal: {agent.goal[:100]}...")
            print(f"   Tools count: {len(agent.tools) if hasattr(agent, 'tools') else 0}")
        
        # Test creating a simple task
        print("\n🧪 Testing task creation...")
        test_agent = agents_map["senior_developer"]
        
        test_task = Task(
            description="Create a simple test file with 'Hello World' content",
            expected_output="A file named test.txt with 'Hello World' content",
            agent=test_agent,
        )
        print("✅ Task created successfully")
        
        # Test creating a crew
        print("\n🧪 Testing crew creation...")
        test_crew = Crew(
            agents=[test_agent],
            tasks=[test_task],
            process=Process.sequential,
            verbose=True,
        )
        print("✅ Crew created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing agent creation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Agent Creation Debug Test")
    print("=" * 50)
    
    if test_agent_creation():
        print("\n✅ Agent creation test completed successfully!")
    else:
        print("\n❌ Agent creation test failed!") 