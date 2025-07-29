from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
import os

def get_llm():
    """Initializes the LLM from environment credentials."""
    return ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.7)

def run_simple_agent_task(prompt: str) -> str:
    print(f"--- Received task: {prompt} ---")
    llm = get_llm()
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
    research_task = Task(
        description=prompt,
        expected_output="A concise, paragraph-long answer to the user's prompt.",
        agent=researcher,
    )
    simple_crew = Crew(
        agents=[researcher],
        tasks=[research_task],
        verbose=2
    )
    result = simple_crew.kickoff()
    print(f"--- Task completed. Result: {result} ---")
    return result 