#!/usr/bin/env python3
"""
Test New CrewAI Tools
Verify that the new tools work properly with CrewAI
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

def test_new_tools():
    """Test the new CrewAI tools"""
    print("🧪 Testing New CrewAI Tools...")
    
    try:
        # Initialize LLM
        model_name = os.getenv("LLM_MODEL", "gemini-1.5-pro-latest")
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        
        llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
        print(f"✅ LLM initialized: {model_name}")
        
        # Initialize worker agents with new tools
        worker_agents = WorkerAgents()
        print("✅ Worker agents initialized")
        
        # Test creating each agent with tools
        agents_map = {
            "senior_developer": worker_agents.senior_developer(llm),
            "qa_tester": worker_agents.qa_tester(llm),
            "code_analyzer": worker_agents.code_analyzer(llm),
            "system_integrator": worker_agents.system_integrator(llm),
        }
        
        print("✅ All agents created successfully with tools")
        
        # Test accessing agent properties
        for role, agent in agents_map.items():
            print(f"🔍 Testing agent: {role}")
            print(f"   Role: {agent.role}")
            print(f"   Goal: {agent.goal[:100]}...")
            print(f"   Tools count: {len(agent.tools) if hasattr(agent, 'tools') else 0}")
            if hasattr(agent, 'tools') and agent.tools:
                for tool in agent.tools:
                    print(f"     - {tool.name}: {tool.description[:50]}...")
        
        # Test creating a simple task with file operations
        print("\n🧪 Testing task with file operations...")
        test_agent = agents_map["senior_developer"]
        
        test_task = Task(
            description="Create a simple test file called 'test_tools.txt' with the content 'Hello from CrewAI Tools!' and then read it back to verify it was created correctly.",
            expected_output="A file named test_tools.txt with 'Hello from CrewAI Tools!' content, and verification that it was read successfully.",
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
        
        # Test the crew execution
        print("\n🚀 Testing crew execution...")
        result = test_crew.kickoff()
        print(f"✅ Crew execution completed!")
        print(f"📄 Result: {result[:500]}{'...' if len(result) > 500 else ''}")
        
        # Verify the file was actually created
        if os.path.exists('test_tools.txt'):
            print("✅ File was actually created!")
            with open('test_tools.txt', 'r') as f:
                content = f.read()
            print(f"📄 File content: {content}")
        else:
            print("❌ File was not created")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing new tools: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 New CrewAI Tools Test")
    print("=" * 50)
    
    if test_new_tools():
        print("\n✅ New tools test completed successfully!")
    else:
        print("\n❌ New tools test failed!") 