from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI

class PlanningSpecialistAgents:
    """Specialized agents for prompt optimization and blueprint planning"""
    
    def prompt_optimizer(self, llm: ChatGoogleGenerativeAI) -> Agent:
        """Advanced prompt optimization agent"""
        return Agent(
            role="Advanced Prompt Optimization Specialist",
            goal="Transform user requests into optimized, detailed prompts with clear success criteria and technical context",
            backstory="""You are an expert in prompt engineering and request optimization. 
            You excel at taking vague or incomplete user requests and transforming them into 
            detailed, actionable specifications that AI agents can execute with precision.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            tools=[],
            memory=True
        )
    
    def planning_specialist(self, llm: ChatGoogleGenerativeAI) -> Agent:
        """Planning specialist agent for creating execution blueprints"""
        return Agent(
            role="Strategic Planning Specialist",
            goal="Create comprehensive execution blueprints with task breakdown, agent assignments, and resource planning",
            backstory="""You are a master strategist and project planner. You excel at taking 
            optimized prompts and creating detailed execution plans that maximize efficiency 
            and success probability. You understand agent capabilities, resource constraints, 
            and optimal task sequencing.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            tools=[],
            memory=True
        )

class AdvancedAgents:
    """Advanced agent definitions for the Cognitive Forge system"""
    
    def __init__(self):
        self.agents = {}
    
    def researcher(self, llm: ChatGoogleGenerativeAI) -> Agent:
        """Research specialist agent"""
        return Agent(
            role="Research Specialist",
            goal="Conduct comprehensive research and gather relevant information",
            backstory="""You are an expert researcher with deep analytical skills. 
            You excel at finding, analyzing, and synthesizing information from various sources.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            tools=[],
            memory=True
        )
    
    def writer(self, llm: ChatGoogleGenerativeAI) -> Agent:
        """Content creation specialist agent"""
        return Agent(
            role="Content Creation Specialist",
            goal="Create high-quality, engaging content based on research and requirements",
            backstory="""You are a skilled content creator with expertise in writing, 
            editing, and content strategy. You excel at transforming ideas into compelling content.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            tools=[],
            memory=True
        )
    
    def reviewer(self, llm: ChatGoogleGenerativeAI) -> Agent:
        """Quality assurance and review specialist agent"""
        return Agent(
            role="Quality Assurance Specialist",
            goal="Review and validate content quality, accuracy, and adherence to requirements",
            backstory="""You are a meticulous quality assurance expert with keen attention to detail. 
            You excel at identifying issues, ensuring accuracy, and maintaining high standards.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            tools=[],
            memory=True
        )
    
    def lead_architect(self, llm: ChatGoogleGenerativeAI) -> Agent:
        """Enhanced Lead Architect Agent for comprehensive planning and execution blueprints"""
        return Agent(
            role="Lead Strategic Architect",
            goal="Create comprehensive execution blueprints and orchestrate complex mission execution",
            backstory="""You are the master architect of the Cognitive Forge system. You excel at 
            strategic planning, resource allocation, and creating detailed execution blueprints that 
            maximize success probability. You understand the capabilities of all agents, system 
            constraints, and optimal execution strategies. You are responsible for transforming 
            optimized prompts into actionable, detailed plans that guide the entire mission execution.""",
            verbose=True,
            allow_delegation=True,
            llm=llm,
            tools=[],
            memory=True
        )
    
    def code_generator(self, llm: ChatGoogleGenerativeAI) -> Agent:
        """Code generation specialist agent"""
        return Agent(
            role="Code Generation Specialist",
            goal="Generate high-quality, functional code based on specifications and requirements",
            backstory="""You are an expert software developer with deep knowledge of multiple 
            programming languages and frameworks. You excel at writing clean, efficient, and 
            maintainable code that meets exact specifications.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            tools=[],
            memory=True
        )
    
    def debugger(self, llm: ChatGoogleGenerativeAI) -> Agent:
        """Debugging and problem-solving specialist agent"""
        return Agent(
            role="Debugging Specialist",
            goal="Identify, analyze, and resolve technical issues and errors",
            backstory="""You are a skilled debugger and problem solver with expertise in 
            identifying root causes, analyzing error patterns, and implementing effective solutions. 
            You excel at systematic troubleshooting and error resolution.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            tools=[],
            memory=True
        ) 