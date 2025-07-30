#!/usr/bin/env python3
"""
Simple Agent Test
Test basic agent creation without tools
"""

import os
import sys
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from crewai import Agent, Task, Crew, Process

# Load environment variables
load_dotenv()

def test_simple_agent():
    """Test basic agent creation without tools"""
    print("🧪 Testing Simple Agent Creation...")
    
    try:
        # Initialize LLM
        model_name = os.getenv("LLM_MODEL", "gemini-1.5-pro-latest")
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        
        llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
        print(f"✅ LLM initialized: {model_name}")
        
        # Create a simple agent without tools
        simple_agent = Agent(
            role="Simple Test Agent",
            goal="Your goal is to respond to simple questions and tasks.",
            backstory="You are a helpful AI assistant that can answer questions and perform simple tasks.",
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )
        
        print("✅ Simple agent created successfully")
        
        # Create a simple task
        simple_task = Task(
            description="Create a simple test file with 'Hello World' content",
            expected_output="A file named test.txt with 'Hello World' content",
            agent=simple_agent,
        )
        print("✅ Simple task created successfully")
        
        # Create a simple crew
        simple_crew = Crew(
            agents=[simple_agent],
            tasks=[simple_task],
            process=Process.sequential,
            verbose=True,
        )
        print("✅ Simple crew created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing simple agent: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Simple Agent Test")
    print("=" * 50)
    
    if test_simple_agent():
        print("\n✅ Simple agent test completed successfully!")
    else:
        print("\n❌ Simple agent test failed!") 