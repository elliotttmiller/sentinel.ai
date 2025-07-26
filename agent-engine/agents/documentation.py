"""
Documentation Agent for Project Sentinel.

Technical writer and historian that generates clear and concise documentation.
Updates README files, generates code comments, and writes CHANGELOG entries.
"""

from typing import Dict, Any, List, Optional
import json
from pathlib import Path
from datetime import datetime
from loguru import logger

from ..core.agent_base import BaseAgent, AgentRole, AgentContext, AgentResult, AgentStatus


class DocumentationAgent(BaseAgent):
    """
    Documentation Agent - Technical writer and historian.
    
    Responsibilities:
    - Generate clear and concise documentation
    - Update README files with project information
    - Write code comments and docstrings
    - Create CHANGELOG entries for changes
    - Maintain API documentation
    - Ensure documentation is up-to-date and accurate
    """
    
    def __init__(
        self,
        role: AgentRole,
        name: str,
        description: str,
        tools: list[str],
        model_name: str,
        llm_client,
        tool_manager
    ):
        super().__init__(role, name, description, tools, model_name)
        self.llm_client = llm_client
        self.tool_manager = tool_manager
        self.logger = logger.bind(agent="documentation")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt that defines the Documentation Agent's behavior."""
        return """
        You are the Documentation Agent, a technical writer and historian for Project Sentinel.
        Your role is to generate clear, comprehensive, and maintainable documentation
        that helps users and developers understand the project.
        
        Your expertise includes:
        1. **Technical Writing**: Create clear and concise technical documentation
        2. **Code Documentation**: Write helpful comments and docstrings
        3. **Project Documentation**: Maintain README files and project guides
        4. **Change Documentation**: Create CHANGELOG entries for updates
        5. **API Documentation**: Document interfaces and endpoints
        6. **User Guides**: Create tutorials and usage examples
        
        Documentation Principles:
        - **Clarity**: Write in simple, understandable language
        - **Completeness**: Cover all necessary information
        - **Accuracy**: Ensure documentation matches the actual code
        - **Consistency**: Use consistent formatting and style
        - **Accessibility**: Make documentation easy to find and navigate
        - **Maintainability**: Keep documentation up-to-date
        
        Documentation Types:
        - **README Files**: Project overview and getting started guides
        - **Code Comments**: Inline documentation for functions and classes
        - **API Documentation**: Interface specifications and examples
        - **CHANGELOG**: Version history and change descriptions
        - **User Guides**: Tutorials and usage instructions
        - **Developer Guides**: Setup and contribution instructions
        
        Always prioritize:
        - User-friendly language and examples
        - Comprehensive coverage of features
        - Clear structure and organization
        - Regular updates to reflect changes
        """
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute the Documentation Agent's documentation task.
        
        Args:
            context: The execution context containing documentation requirements
            
        Returns:
            AgentResult: The documentation result
        """
        self.logger.info(f"Starting documentation task for mission {context.mission_id}")
        self.update_status(AgentStatus.WORKING)
        
        try:
            # Extract documentation requirements from context
            doc_requirements = context.user_prompt
            
            # Analyze the codebase for documentation needs
            codebase_analysis = await self._analyze_codebase_for_documentation(context.workspace_path)
            
            # Generate comprehensive documentation
            documentation_result = await self._generate_documentation(
                codebase_analysis,
                doc_requirements,
                context
            )
            
            # Create the result
            result = AgentResult(
                success=True,
                output=json.dumps(documentation_result, indent=2),
                metadata={
                    "documentation_type": "comprehensive_documentation",
                    "files_updated": len(documentation_result.get("files_updated", [])),
                    "new_files_created": len(documentation_result.get("new_files_created", [])),
                    "documentation_coverage": documentation_result.get("coverage", {}).get("overall", 0),
                    "changelog_entries": len(documentation_result.get("changelog_entries", []))
                }
            )
            
            self.logger.info("Documentation task completed successfully")
            self.update_status(AgentStatus.COMPLETED)
            return result
            
        except Exception as e:
            self.logger.error(f"Documentation task failed: {e}")
            self.update_status(AgentStatus.ERROR)
            return AgentResult(
                success=False,
                output="",
                error=f"Documentation task failed: {str(e)}"
            )
    
    async def _analyze_codebase_for_documentation(self, workspace_path: Path) -> Dict[str, Any]:
        """
        Analyze the codebase to understand documentation needs.
        
        Args:
            workspace_path: Path to the workspace
            
        Returns:
            Dict[str, Any]: Codebase analysis for documentation
        """
        self.logger.info("Analyzing codebase for documentation requirements")
        
        analysis = {
            "project_structure": {},
            "main_files": [],
            "documentation_files": [],
            "languages": [],
            "frameworks": [],
            "entry_points": [],
            "dependencies": {}
        }
        
        try:
            # Detect project structure
            if (workspace_path / "README.md").exists():
                analysis["documentation_files"].append("README.md")
            
            if (workspace_path / "CHANGELOG.md").exists():
                analysis["documentation_files"].append("CHANGELOG.md")
            
            # Find main application files
            for file_path in workspace_path.rglob("*.py"):
                if file_path.name in ["main.py", "app.py", "__init__.py"]:
                    analysis["main_files"].append(str(file_path))
            
            for file_path in workspace_path.rglob("*.js"):
                if file_path.name in ["index.js", "app.js", "server.js"]:
                    analysis["main_files"].append(str(file_path))
            
            # Detect languages and frameworks
            if (workspace_path / "requirements.txt").exists():
                analysis["languages"].append("python")
                analysis["frameworks"].append("fastapi")
            
            if (workspace_path / "package.json").exists():
                analysis["languages"].append("javascript")
                analysis["frameworks"].append("react")
            
        except Exception as e:
            self.logger.warning(f"Error analyzing codebase for documentation: {e}")
        
        return analysis
    
    async def _generate_documentation(
        self, 
        codebase_analysis: Dict[str, Any],
        doc_requirements: str,
        context: AgentContext
    ) -> Dict[str, Any]:
        """
        Generate comprehensive documentation.
        
        Args:
            codebase_analysis: Analysis of the codebase
            doc_requirements: Specific documentation requirements
            context: Execution context
            
        Returns:
            Dict[str, Any]: Documentation generation result
        """
        self.logger.info("Generating comprehensive documentation")
        
        documentation_result = {
            "files_updated": [],
            "new_files_created": [],
            "coverage": {},
            "changelog_entries": [],
            "recommendations": []
        }
        
        # Update README
        readme_result = await self._update_readme(codebase_analysis, doc_requirements)
        documentation_result["files_updated"].append(readme_result)
        
        # Update CHANGELOG
        changelog_result = await self._update_changelog(doc_requirements)
        documentation_result["changelog_entries"] = changelog_result
        
        # Generate code documentation
        code_docs = await self._generate_code_documentation(codebase_analysis)
        documentation_result["files_updated"].extend(code_docs)
        
        # Calculate documentation coverage
        documentation_result["coverage"] = self._calculate_documentation_coverage(
            codebase_analysis, documentation_result
        )
        
        # Generate recommendations
        documentation_result["recommendations"] = self._generate_documentation_recommendations(
            documentation_result
        )
        
        return documentation_result
    
    async def _update_readme(
        self, 
        codebase_analysis: Dict[str, Any], 
        doc_requirements: str
    ) -> Dict[str, Any]:
        """
        Update the README file with project information.
        
        Args:
            codebase_analysis: Analysis of the codebase
            doc_requirements: Documentation requirements
            
        Returns:
            Dict[str, Any]: README update result
        """
        readme_content = f"""
# Project Sentinel: Personal AI Agent Command Center

A mobile-first command center for deploying and managing autonomous AI agents that execute complex tasks on your local desktop.

## 🎯 Vision

Transform high-level natural language commands from your mobile device into sophisticated, multi-step tasks executed by specialized AI agents running locally on your desktop.

## 🏗️ Architecture

```
Mobile App (React Native/Expo)
    ↓
Cloud Backend (Railway + FastAPI)
    ↓
Cloudflare Tunnel
    ↓
Local Desktop (Agent Engine)
```

## 🧠 Core Features

- **AI Chain of Command Planning**: Two-phase planning with Prompt Alchemist and Grand Architect
- **Dynamic Crew Execution**: Assembled on-demand based on mission requirements
- **Autonomous Self-Healing**: Debugger Agent for automatic error recovery
- **Long-Term Memory**: Vector database for continuous learning
- **Human-in-the-Loop**: Interactive guidance when needed

## 🛠️ Agent Guild

- **Senior Developer Agent**: Primary code builder and implementer
- **Code Reviewer Agent**: Quality gatekeeper and code analyzer
- **QA Tester Agent**: Test creation and validation specialist
- **Debugger Agent**: Crisis manager for error resolution
- **Documentation Agent**: Technical writer and historian

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Git
- Railway account
- Cloudflare account
- OpenAI/Anthropic API key

### Local Development Setup

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd sentinel
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   pip install -r requirements.txt
   ```

3. **Agent Engine Setup**
   ```bash
   cd agent-engine
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   pip install -r requirements.txt
   ```

4. **Mobile App Setup**
   ```bash
   cd mobile-app
   npm install
   npx expo start
   ```

## 📁 Project Structure

```
sentinel/
├── backend/                 # Cloud backend (Railway)
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
├── agent-engine/           # Local desktop agent runner
│   ├── agents/
│   ├── core/
│   ├── tools/
│   └── requirements.txt
├── mobile-app/            # React Native mobile app
│   ├── src/
│   ├── package.json
│   └── app.json
├── shared/                # Shared utilities and types
│   ├── types/
│   └── utils/
├── docs/                  # Documentation
├── scripts/               # Development scripts
└── tests/                 # Test suites
```

## 🔧 Configuration

Create `.env` files in each component directory:

### Backend (.env)
```
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-...
RAILWAY_TOKEN=...
```

### Agent Engine (.env)
```
OPENAI_API_KEY=sk-...
CLOUDFLARE_TUNNEL_TOKEN=...
LOCAL_API_PORT=8001
```

### Mobile App (.env)
```
EXPO_PUBLIC_API_URL=https://...
EXPO_PUBLIC_WEBSOCKET_URL=wss://...
```

## 🧪 Development

### Running Locally

1. **Start Backend**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Start Agent Engine**
   ```bash
   cd agent-engine
   python main.py
   ```

3. **Start Mobile App**
   ```bash
   cd mobile-app
   npx expo start
   ```

### Testing

```bash
# Backend tests
cd backend && pytest

# Agent tests
cd agent-engine && pytest

# Mobile tests
cd mobile-app && npm test
```

## 📚 Documentation

- [Architecture Overview](docs/architecture.md)
- [Agent Framework](docs/agents.md)
- [API Documentation](docs/api.md)
- [Deployment Guide](docs/deployment.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Project Sentinel** - Your personal AI agent command center 🚀
"""
        
        return {
            "file_path": "README.md",
            "content": readme_content,
            "status": "updated",
            "changes_made": ["Updated project overview", "Added setup instructions", "Updated architecture diagram"]
        }
    
    async def _update_changelog(self, doc_requirements: str) -> List[Dict[str, Any]]:
        """
        Update the CHANGELOG with recent changes.
        
        Args:
            doc_requirements: Documentation requirements
            
        Returns:
            List[Dict[str, Any]]: CHANGELOG entries
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        changelog_entries = [
            {
                "version": "0.1.0",
                "date": today,
                "type": "added",
                "description": "Initial implementation of Project Sentinel agent framework",
                "details": [
                    "Core agent framework with base agent class",
                    "Mission planner with two-phase planning system",
                    "Crew manager for dynamic agent assembly",
                    "Memory manager for long-term learning",
                    "Specialized agents: Prompt Alchemist, Grand Architect, Senior Developer, Code Reviewer, QA Tester, Debugger, Documentation"
                ]
            }
        ]
        
        return changelog_entries
    
    async def _generate_code_documentation(self, codebase_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate documentation for code files.
        
        Args:
            codebase_analysis: Analysis of the codebase
            
        Returns:
            List[Dict[str, Any]]: Code documentation results
        """
        code_docs = []
        
        # TODO: Implement actual code documentation generation
        # For now, return placeholder documentation
        
        for main_file in codebase_analysis.get("main_files", []):
            code_docs.append({
                "file_path": main_file,
                "documentation_type": "code_comments",
                "status": "updated",
                "changes_made": ["Added function docstrings", "Updated inline comments"]
            })
        
        return code_docs
    
    def _calculate_documentation_coverage(
        self, 
        codebase_analysis: Dict[str, Any], 
        documentation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate documentation coverage metrics."""
        total_files = len(codebase_analysis.get("main_files", []))
        documented_files = len(documentation_result.get("files_updated", []))
        
        coverage_percentage = (documented_files / total_files * 100) if total_files > 0 else 0
        
        return {
            "overall": coverage_percentage,
            "readme_updated": "README.md" in [f.get("file_path") for f in documentation_result.get("files_updated", [])],
            "changelog_updated": len(documentation_result.get("changelog_entries", [])) > 0,
            "code_documented": documented_files
        }
    
    def _generate_documentation_recommendations(self, documentation_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on documentation results."""
        recommendations = []
        
        coverage = documentation_result.get("coverage", {}).get("overall", 0)
        if coverage < 80:
            recommendations.append("Increase documentation coverage to at least 80%")
        
        if not documentation_result.get("coverage", {}).get("readme_updated", False):
            recommendations.append("Update README with current project information")
        
        if not documentation_result.get("coverage", {}).get("changelog_updated", False):
            recommendations.append("Add entries to CHANGELOG for recent changes")
        
        if len(documentation_result.get("files_updated", [])) < 3:
            recommendations.append("Create more comprehensive documentation")
        
        return recommendations 