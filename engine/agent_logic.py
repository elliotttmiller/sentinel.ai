from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# --- IMPORTANT: ONE-TIME SETUP ---
# Make sure you have a .env file in your `sentinel/engine/` directory
# with your GOOGLE_APPLICATION_CREDENTIALS="path/to/your/key.json"
# --------------------------------

def get_llm():
    """Initializes the LLM from environment credentials."""
    # This will automatically use the GOOGLE_APPLICATION_CREDENTIALS env var
    return ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.7)

def run_simple_agent_task(prompt: str) -> str:
    """
    Takes a prompt, runs a simple CrewAI crew, and returns the result.
    This is the core "unit of work" for our agents.
    """
    print(f"--- Received task: {prompt} ---")
    llm = get_llm()

    # Define a simple agent
    researcher = Agent(
        role="Expert Tech Researcher",
        goal=f"Find and provide a concise, factual answer for the user's prompt: '{prompt}'",
        backstory=(
            "You are a master researcher, capable of synthesizing information "
            "from any source to provide clear, accurate answers."
        ),
        llm=llm,
        verbose=True,
    )

    # Define a simple task
    research_task = Task(
        description=prompt,
        expected_output="A concise, paragraph-long answer to the user's prompt.",
        agent=researcher,
    )

    # Assemble and run the crew
    simple_crew = Crew(
        agents=[researcher],
        tasks=[research_task],
        verbose=2
    )

    # Run the mission
    result = simple_crew.kickoff()
    
    print(f"--- Task completed. Result: {result} ---")
    return result 