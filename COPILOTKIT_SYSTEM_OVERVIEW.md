## File & Folder Explanations

### Root Directory

- `.env`: Main environment variables for backend (API keys, DB URLs, etc.)
- `.git/`: Git version control data.
- `.gitignore`: Specifies files/folders to ignore in Git.
- `.vscode/`: VS Code workspace settings.
- `COPILOTKIT_SYSTEM_OVERVIEW.md`: This system overview and documentation file.
- `README.md`: Main project documentation and onboarding guide.
- `SETUP_GUIDE.md`: Step-by-step setup instructions for the system.
- `manage_services.py`: Python script to automate starting/stopping backend/frontend services.
- `move_desktop_app_to_root.ps1`: PowerShell script for moving desktop app files.
- `requirements.txt`: Python package dependencies for backend.
- `runtime-references.txt`: Notes and references for runtime configuration.
- `setup.cfg`: Python packaging configuration.

### copilotkit-frontend/
- `.env`: Frontend environment variables (API keys, config).
- `build/`: Production build output (auto-generated).
- `LICENSE`: Project license (MIT).
- `node_modules/`: Installed frontend dependencies (auto-generated).
- `package.json`: Frontend dependencies, scripts, and metadata.
- `public/`: Static assets for frontend (favicon, HTML, manifest, robots.txt).
- `README.md`: Frontend-specific documentation.
- `src/`: Main frontend source code.
  - `App.js`, `App.jsx`: Main React app entry points.
  - `googleGenAIAdapter.js`: Adapter for Google Generative AI integration.
  - `index.css`, `index.js`: Global styles and entry point for React.
  - `setupProxy.js`: Proxy configuration for local API requests.
  - `components/`: Reusable React UI components.
    - `AdvancedAgentPanel.js`: Advanced agent dashboard panel.
    - `AgenticTaskExecutor.js`: UI for agentic task execution.
    - `AnalyticsCharts.js`: Analytics chart components.
    - `CopilotAgent.jsx`: Main Copilot agent logic and UI.
    - `CopilotAgentPanel.js`: Panel for Copilot agent controls.
    - `CopilotChat.js`: Chat UI component (custom or placeholder).
    - `CopilotMissionChat.js`: Mission-specific chat UI.
    - `DashboardWidgets.js`: Dashboard widget components.
    - `ErrorBoundary.js`: Error boundary for React error handling.
    - `KeyboardNavigation.js`: Keyboard navigation logic.
    - `MissionList.js`: Mission list UI.
    - `MissionModal.js`: Modal for mission details.
    - `NavBar.js`: Navigation bar UI.
    - `Notification.js`: Notification system UI.
    - `SentinelInitializer.js`: Initialization logic for Sentinel frontend.
    - `SettingsPanel.js`: Settings panel UI.
    - `ThemeProvider.js`: Theme/context provider for UI.
  - `context/`: React context providers.
    - `SentinelContext.js`: Global Sentinel context provider.
  - `hooks/`: Custom React hooks.
    - `useNotification.js`: Hook for notifications.
    - `useRealtime.js`: Hook for real-time updates.
  - `pages/`: Page-level React components.
    - `AgenticGenerativeUI.js`: Agentic generative UI page (CopilotKit agentic chat).
    - `Analytics.js`: Analytics dashboard page.
    - `Dashboard.js`: Main dashboard page.
    - `Missions.js`: Missions dashboard page.
    - `NotFound.js`: 404 error page.
    - `Settings.js`: Settings page.
  - `styles/`: CSS stylesheets.
    - `agentic.css`: Styles for agentic generative UI.
  - `utils/`: Utility functions for frontend.
    - `api.js`: API call utilities.
    - `index.js`: General frontend utilities.
    - `llm.js`: LLM integration utilities.
    - `realtime.js`: Real-time update utilities.
  - `views/`: High-level UI views/screens.
    - `Analytics.jsx`: Analytics view.
    - `Dashboard.jsx`: Dashboard view.
    - `Missions.jsx`: Missions view.
    - `Settings.jsx`: Settings view.
    - `TestMissions.jsx`: Test missions view.

### db/
- `chroma_memory/`: ChromaDB vector database files for agent memory.
  - `chroma.sqlite3`: Main ChromaDB SQLite file.
  - `a71a6ad9-eb43-41a4-b61f-877454df2314/`: ChromaDB binary data directory.

### desktop-app/
- `clean_copilotkit_workspace.ps1`: PowerShell script to clean workspace for desktop app.

### src/
- `__init__.py`: Python package marker.
- `cognitive_engine_service.py`: Core cognitive engine logic.
- `main.py`: Backend entry point (FastAPI).
- `README_WebSocket_Fixes.md`: Notes/fixes for WebSocket issues.
- `agents/`: AI agent logic and mission execution.
  - `__init__.py`: Agents package marker.
  - `advanced_agents.py`: Advanced agent logic.
  - `ai_task_parser.py`: AI task parsing logic.
  - `executable_agent.py`: Executable agent logic.
  - `real_mission_executor.py`: Mission execution logic.
  - `simple_executable_agent.py`: Simple agent logic.
  - `specialized_agents.py`: Specialized agent logic.
- `api/`: API endpoint definitions.
  - `__init__.py`: API package marker.
  - `copilotkit.py`: CopilotKit API integration.
- `config/`: System configuration modules.
  - `__init__.py`: Config package marker.
  - `settings.py`: System settings/configuration.
- `core/`: Core business logic and workflow engines.
  - `__init__.py`: Core package marker.
  - `advanced_intelligence.py`: Advanced intelligence logic.
  - `blueprint_tasks.py`: Task blueprint logic.
  - `cognitive_forge_engine.py`: Cognitive forge engine logic.
  - `enhanced_cognitive_forge_engine.py`: Enhanced cognitive forge engine logic.
  - `execution_workflow.py`: Workflow execution logic.
  - `hybrid_decision_engine.py`: Hybrid decision engine logic.
  - `real_mission_executor.py`: Mission execution logic.
  - `sandbox_executor.py`: Sandbox execution logic.
  - `sentinel_multi_agent_integration.py`: Multi-agent integration logic.
  - `supercharged_optimizer.py`: Optimizer logic.
  - `supercharged_websocket_manager.py`: WebSocket manager logic.
- `models/`: Data models and DB logic.
  - `__init__.py`: Models package marker.
  - `advanced_database.py`: Advanced database logic.
  - `fix_database_schema.py`: Database schema fixes.
  - `fix_railway_database.py`: Railway DB fixes.
- `tools/`: Tools and utilities for agents.
  - `__init__.py`: Tools package marker.
  - `advanced_tools.py`: Advanced tools for agents.
  - `file_system_tools.py`: File system utilities.
  - `simple_file_system_tools.py`: Simple file system tools.
  - `specialized_tools.py`: Specialized agent tools.
- `utils/`: General backend utilities.
  - `__init__.py`: Utils package marker.
  - `agent_observability.py`: Observability utilities.
  - `auto_fix.py`: Automated fix logic.
  - `automated_debugger.py`: Automated debugging logic.
  - `crewai_bypass.py`: CrewAI bypass logic.
  - `debug_killer.py`: Debugging utilities.
  - `debug_logger.py`: Debug logger.
  - `fix_ai.py`: AI fix logic.
  - `google_ai_wrapper.py`: Google AI integration.
  - `guardian_protocol.py`: Guardian protocol logic.
  - `json_parser.py`: JSON parsing utilities.
  - `litellm_custom_provider.py`: LiteLLM provider logic.
  - `llm_patch.py`: LLM patch logic.
  - `log_collector.py`: Log collection utilities.
  - `manage_services.py`: Service management utilities.
  - `onnxruntime_fix.py`: ONNX runtime fix logic.
  - `performance_optimizer.py`: Performance optimization logic.
  - `phoenix_protocol.py`: Phoenix protocol logic.
  - `self_learning_module.py`: Self-learning module logic.
  - `sentry_api_client.py`: Sentry API client.
  - `sentry_integration.py`: Sentry integration logic.
  - `synapse_logging.py`: Synapse logging utilities.
  - `system_cheatsheet.txt`: System cheatsheet.

### logs/
- (Empty or runtime logs generated during operation.)

### agentic_generative_ui/ (legacy)
- `agent.py`: Legacy agentic generative UI backend logic.
- `page.tsx`: Legacy agentic generative UI frontend logic.
- `README.md`: Legacy agentic generative UI documentation.
- `style.css`: Legacy agentic generative UI styles.
# Sentinel.ai — Full End-to-End System Overview

## 1. High-Level Architecture

Sentinel.ai is a modular AI platform combining a FastAPI backend (Python), a React SPA frontend, CopilotKit-native observability, SQLite/Redis data storage, and advanced agent/mission logic. It is designed for robust, scalable, and secure operation in local or self-hosted environments.

**Main Components:**
- **Backend:** FastAPI, SQLAlchemy, CopilotKit, custom agents, mission logic, analytics, and API endpoints
- **Frontend:** React SPA, custom UI components, CopilotKit integration, health checks, and user dashboards
- **Database:** SQLite (primary), Redis (cache/queue)
- **Observability:** CopilotKit-native (no legacy Sentry/Wandb/Weave)
- **Deployment:** Local, Render, or other self-hosted platforms

---

sentinel.ai/
├── .env                        # Backend environment variables
├── .gitignore                  # Git ignore rules
├── copilotkit-references.txt   # CopilotKit reference notes
├── COPILOTKIT_SYSTEM_OVERVIEW.md # System overview (this file)
├── db/
│   └── chroma_memory/
│       ├── chroma.sqlite3      # ChromaDB SQLite file
│       └── a71a6ad9-eb43-41a4-b61f-877454df2314/
│           ├── data_level0.bin # Vector DB binary data
│           ├── header.bin      # Vector DB header
│           ├── length.bin      # Vector DB length info
│           └── link_lists.bin  # Vector DB link lists
├── desktop-app/
│   └── clean_copilotkit_workspace.ps1 # Cleans workspace for desktop app
├── manage_services.py          # Service management script
├── move_desktop_app_to_root.ps1 # PowerShell script for desktop app
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
├── runtime-references.txt      # Runtime notes
├── setup.cfg                   # Python setup configuration
├── SETUP_GUIDE.md              # Setup instructions
## System Directory Structure Overview

```
copilot/
│
├── .env                        # Main environment variables for backend (API keys, DB URLs, etc.)
├── .git/                       # Git version control data
├── .gitignore                  # Specifies files/folders to ignore in Git
├── .vscode/                    # VS Code workspace settings
├── COPILOTKIT_SYSTEM_OVERVIEW.md # This system overview and documentation file
├── README.md                   # Main project documentation and onboarding guide
├── SETUP_GUIDE.md              # Step-by-step setup instructions for the system
├── manage_services.py          # Python script to automate starting/stopping backend/frontend services
├── move_desktop_app_to_root.ps1 # PowerShell script for moving desktop app files
├── requirements.txt            # Python package dependencies for backend
├── runtime-references.txt      # Notes and references for runtime configuration
├── setup.cfg                   # Python packaging configuration
│
├── copilotkit-frontend/        # Modern React SPA frontend (CopilotKit UI)
│   ├── .env                    # Frontend environment variables (API keys, config)
│   ├── build/                  # Production build output (auto-generated)
│   ├── LICENSE                 # Project license (MIT)
│   ├── node_modules/           # Installed frontend dependencies (auto-generated)
│   ├── package.json            # Frontend dependencies, scripts, and metadata
│   ├── public/                 # Static assets for frontend
│   │   ├── favicon.ico         # App favicon
│   │   ├── index.html          # Main HTML file
│   │   ├── manifest.json       # Web app manifest
│   │   └── robots.txt          # Robots exclusion file
│   ├── README.md               # Frontend-specific documentation
│   ├── src/                    # Main frontend source code
│   │   ├── App.js              # Main React app entry point
│   │   ├── App.jsx             # Alternate React app entry point
│   │   ├── googleGenAIAdapter.js # Adapter for Google Generative AI integration
│   │   ├── index.css           # Global styles
│   │   ├── index.js            # React entry point
│   │   ├── setupProxy.js       # Proxy configuration for local API requests
│   │   ├── components/         # Reusable React UI components
│   │   │   ├── AdvancedAgentPanel.js      # Advanced agent dashboard panel
│   │   │   ├── AgenticTaskExecutor.js     # UI for agentic task execution
│   │   │   ├── AnalyticsCharts.js         # Analytics chart components
│   │   │   ├── CopilotAgent.jsx           # Main Copilot agent logic and UI
│   │   │   ├── CopilotAgentPanel.js       # Panel for Copilot agent controls
│   │   │   ├── CopilotChat.js             # Chat UI component (custom or placeholder)
│   │   │   ├── CopilotMissionChat.js      # Mission-specific chat UI
│   │   │   ├── DashboardWidgets.js        # Dashboard widget components
│   │   │   ├── ErrorBoundary.js           # Error boundary for React error handling
│   │   │   ├── KeyboardNavigation.js      # Keyboard navigation logic
│   │   │   ├── MissionList.js             # Mission list UI
│   │   │   ├── MissionModal.js            # Modal for mission details
│   │   │   ├── NavBar.js                  # Navigation bar UI
│   │   │   ├── Notification.js            # Notification system UI
│   │   │   ├── SentinelInitializer.js     # Initialization logic for Sentinel frontend
│   │   │   ├── SettingsPanel.js           # Settings panel UI
│   │   │   ├── ThemeProvider.js           # Theme/context provider for UI
│   │   ├── context/            # React context providers
│   │   │   └── SentinelContext.js         # Global Sentinel context provider
│   │   ├── hooks/              # Custom React hooks
│   │   │   ├── useNotification.js         # Hook for notifications
│   │   │   └── useRealtime.js             # Hook for real-time updates
│   │   ├── pages/              # Page-level React components
│   │   │   ├── AgenticGenerativeUI.js     # Agentic generative UI page (CopilotKit agentic chat)
│   │   │   ├── Analytics.js               # Analytics dashboard page
│   │   │   ├── Dashboard.js               # Main dashboard page
│   │   │   ├── Missions.js                # Missions dashboard page
│   │   │   ├── NotFound.js                # 404 error page
│   │   │   ├── Settings.js                # Settings page
│   │   ├── styles/              # CSS stylesheets
│   │   │   └── agentic.css               # Styles for agentic generative UI
│   │   ├── utils/               # Utility functions for frontend
│   │   │   ├── api.js                   # API call utilities
│   │   │   ├── index.js                 # General frontend utilities
│   │   │   ├── llm.js                   # LLM integration utilities
│   │   │   └── realtime.js              # Real-time update utilities
│   │   ├── views/               # High-level UI views/screens
│   │   │   ├── Analytics.jsx            # Analytics view
│   │   │   ├── Dashboard.jsx            # Dashboard view
│   │   │   ├── Missions.jsx             # Missions view
│   │   │   ├── Settings.jsx             # Settings view
│   │   │   └── TestMissions.jsx         # Test missions view
│   ├── yarn.lock                # Yarn lockfile for dependency management
│
├── db/                         # Local database files for agent memory
│   └── chroma_memory/          # ChromaDB vector database files for agent memory
│       ├── chroma.sqlite3      # Main ChromaDB SQLite file
│       └── a71a6ad9-eb43-41a4-b61f-877454df2314/ # ChromaDB binary data directory
│
├── desktop-app/                # Desktop app scripts
│   └── clean_copilotkit_workspace.ps1   # PowerShell script to clean workspace for desktop app
│
├── src/                        # Python backend source code
│   ├── __init__.py             # Python package marker
│   ├── cognitive_engine_service.py      # Core cognitive engine logic
│   ├── main.py                 # Backend entry point (FastAPI)
│   ├── README_WebSocket_Fixes.md        # Notes/fixes for WebSocket issues
│   ├── agents/                 # AI agent logic and mission execution
│   │   ├── __init__.py                 # Agents package marker
│   │   ├── advanced_agents.py          # Advanced agent logic
│   │   ├── ai_task_parser.py           # AI task parsing logic
│   │   ├── executable_agent.py         # Executable agent logic
│   │   ├── real_mission_executor.py    # Mission execution logic
│   │   ├── simple_executable_agent.py  # Simple agent logic
│   │   ├── specialized_agents.py       # Specialized agent logic
│   ├── api/                    # API endpoint definitions
│   │   ├── __init__.py                 # API package marker
│   │   └── copilotkit.py               # CopilotKit API integration
│   ├── config/                 # System configuration modules
│   │   ├── __init__.py                 # Config package marker
│   │   └── settings.py                 # System settings/configuration
│   ├── core/                   # Core business logic and workflow engines
│   │   ├── __init__.py                 # Core package marker
│   │   ├── advanced_intelligence.py    # Advanced intelligence logic
│   │   ├── blueprint_tasks.py          # Task blueprint logic
│   │   ├── cognitive_forge_engine.py   # Cognitive forge engine logic
│   │   ├── enhanced_cognitive_forge_engine.py # Enhanced cognitive forge engine logic
│   │   ├── execution_workflow.py       # Workflow execution logic
│   │   ├── hybrid_decision_engine.py   # Hybrid decision engine logic
│   │   ├── real_mission_executor.py    # Mission execution logic
│   │   ├── sandbox_executor.py         # Sandbox execution logic
│   │   ├── sentinel_multi_agent_integration.py # Multi-agent integration logic
│   │   ├── supercharged_optimizer.py   # Optimizer logic
│   │   ├── supercharged_websocket_manager.py # WebSocket manager logic
│   ├── models/                 # Data models and DB logic
│   │   ├── __init__.py                 # Models package marker
│   │   ├── advanced_database.py        # Advanced database logic
│   │   ├── fix_database_schema.py      # Database schema fixes
│   │   ├── fix_railway_database.py     # Railway DB fixes
│   ├── tools/                  # Tools and utilities for agents
│   │   ├── __init__.py                 # Tools package marker
│   │   ├── advanced_tools.py           # Advanced tools for agents
│   │   ├── file_system_tools.py        # File system utilities
│   │   ├── simple_file_system_tools.py # Simple file system tools
│   │   ├── specialized_tools.py        # Specialized agent tools
│   └── utils/                  # General backend utilities
│       ├── __init__.py                 # Utils package marker
│       ├── agent_observability.py      # Observability utilities
│       ├── auto_fix.py                 # Automated fix logic
│       ├── automated_debugger.py       # Automated debugging logic
│       ├── crewai_bypass.py            # CrewAI bypass logic
│       ├── debug_killer.py             # Debugging utilities
│       ├── debug_logger.py             # Debug logger
│       ├── fix_ai.py                   # AI fix logic
│       ├── google_ai_wrapper.py        # Google AI integration
│       ├── guardian_protocol.py        # Guardian protocol logic
│       ├── json_parser.py              # JSON parsing utilities
│       ├── litellm_custom_provider.py  # LiteLLM provider logic
│       ├── llm_patch.py                # LLM patch logic
│       ├── log_collector.py            # Log collection utilities
│       ├── manage_services.py          # Service management utilities
│       ├── onnxruntime_fix.py          # ONNX runtime fix logic
│       ├── performance_optimizer.py    # Performance optimization logic
│       ├── phoenix_protocol.py         # Phoenix protocol logic
│       ├── self_learning_module.py     # Self-learning module logic
│       ├── sentry_api_client.py        # Sentry API client
│       ├── sentry_integration.py       # Sentry integration logic
│       ├── synapse_logging.py          # Synapse logging utilities
│       ├── system_cheatsheet.txt       # System cheatsheet
│
├── logs/                      # (Empty or runtime logs generated during operation)
│
└── agentic_generative_ui/     # (legacy, now removed from main system)
    ├── agent.py               # Legacy agentic generative UI backend logic
    ├── page.tsx               # Legacy agentic generative UI frontend logic
    ├── README.md              # Legacy agentic generative UI documentation
    └── style.css              # Legacy agentic generative UI styles
```
│   ├── __init__.py             # Python package marker
│   ├── cognitive_engine_service.py # Cognitive engine service logic
│   ├── main.py                 # Backend entry point
│   ├── README_WebSocket_Fixes.md # WebSocket notes
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── advanced_agents.py      # Advanced agent logic
│   │   ├── ai_task_parser.py       # AI task parsing
│   │   ├── executable_agent.py     # Executable agent logic
│   │   ├── real_mission_executor.py# Mission execution
│   │   ├── simple_executable_agent.py # Simple agent logic
│   │   └── specialized_agents.py   # Specialized agent logic
│   ├── api/
│   │   ├── __init__.py
│   │   └── copilotkit.py           # CopilotKit API integration
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py             # System settings/config
│   ├── core/
│   │   ├── __init__.py
│   │   ├── advanced_intelligence.py
│   │   ├── blueprint_tasks.py
│   │   ├── cognitive_forge_engine.py
│   │   ├── enhanced_cognitive_forge_engine.py
│   │   ├── execution_workflow.py
│   │   ├── hybrid_decision_engine.py
│   │   ├── real_mission_executor.py
│   │   ├── supercharged_optimizer.py
│   │   └── supercharged_websocket_manager.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── advanced_database.py    # SQLAlchemy models
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── advanced_tools.py
│   │   ├── file_system_tools.py
│   │   ├── simple_file_system_tools.py
│   │   └── specialized_tools.py
│   └── utils/
│       ├── __init__.py
│       ├── auto_fix.py
│       ├── crewai_bypass.py
│       ├── debug_killer.py
│       ├── debug_logger.py
│       ├── google_ai_wrapper.py
│       ├── guardian_protocol.py
│       ├── json_parser.py
│       ├── llm_patch.py
│       ├── log_collector.py
│       ├── manage_services.py
│       ├── performance_optimizer.py
│       ├── phoenix_protocol.py
│       ├── self_learning_module.py
│       ├── synapse_logging.py
│       ├── system_cheatsheet.txt
│       ├── test_onnxruntime_fix.py
│       └── websocket_helpers.py
└── copilotkit-frontend/
    ├── .env                      # Frontend environment variables
    ├── LICENSE                   # MIT license
    ├── package.json              # Frontend dependencies/scripts
    ├── README.md                 # Frontend documentation
    ├── yarn.lock                 # Dependency lock file
    ├── build/                    # Production build output
    ├── node_modules/             # Installed dependencies (ignored)
    ├── public/
    │   ├── favicon.ico
    │   ├── health.html           # Health check endpoint
    │   ├── index.html
    │   ├── manifest.json
    │   └── robots.txt
    └── src/
        ├── App.js, App.jsx       # Main React app entry points
        ├── index.css, index.js   # Global styles and entry
        ├── sentry.js             # Sentry integration (if used)
        ├── setupProxy.js         # Proxy setup for API
        ├── components/
        │   ├── AdvancedAgentPanel.js
        │   ├── AgenticTaskExecutor.js
        │   ├── AnalyticsCharts.js
        │   ├── CopilotAgent.jsx
        │   ├── CopilotAgentPanel.js
        │   ├── CopilotChat.js
        │   ├── CopilotMissionChat.js
        │   ├── DashboardWidgets.js
        │   ├── ErrorBoundary.js
        │   ├── KeyboardNavigation.js
        │   ├── MissionList.js
        │   ├── MissionModal.js
        │   ├── NavBar.js
        │   ├── Notification.js
        │   ├── SentinelInitializer.js
        │   ├── SettingsPanel.js
        │   └── ThemeProvider.js
        ├── context/
        │   └── SentinelContext.js
        ├── hooks/
        │   ├── useNotification.js
        │   └── useRealtime.js
        ├── pages/
        │   ├── AgenticGenerativeUI.js
        │   ├── Analytics.js
        │   ├── Dashboard.js
        │   ├── Missions.js
        │   ├── NotFound.js
        │   └── Settings.js
        ├── styles/
        │   └── agentic.css
        ├── utils/
        │   ├── api.js
        │   ├── index.js
        │   ├── llm.js
        │   └── realtime.js
        └── views/
            ├── Analytics.jsx
            ├── Dashboard.jsx
            ├── Missions.jsx
            ├── Settings.jsx
            └── TestMissions.jsx
```

---

## 3. In-Depth File & Folder Explanations

- **Backend (`src/`)**:  
  - `main.py`: FastAPI entry point, sets up routes and services.
  - `cognitive_engine_service.py`: Core logic for cognitive/AI engine.
  - `agents/`: Implements agent logic, mission execution, and task parsing.
  - `api/`: API endpoints, including CopilotKit integration.
  - `config/`: System configuration and settings.
  - `core/`: Advanced intelligence, optimization, and workflow engines.
  - `models/`: SQLAlchemy models for database structure.
  - `tools/`: Utility modules for file system, advanced tools, etc.
  - `utils/`: Helper functions for logging, debugging, protocol handling, etc.

- **Frontend (`copilotkit-frontend/`)**:  
  - `App.js`, `App.jsx`: Main React app entry points.
  - `components/`: UI widgets, chat panels, agent dashboards.
  - `context/`: React context providers for global state.
  - `hooks/`: Custom React hooks for notifications, realtime updates.
  - `pages/`: Page-level React components.
  - `styles/`: CSS files for styling.
  - `utils/`: Utility functions for API calls, LLM integration, etc.
  - `views/`: Dashboard and analytics views.
  - `public/`: Static assets and health check endpoint.

- **Database (`db/`)**:  
  - `chroma_memory/`: Vector DB files for advanced memory/embedding storage.

- **Desktop App (`desktop-app/`)**:  
  - PowerShell scripts for workspace management.

- **Config & Docs**:  
  - `.env`, `.env.txt`: Environment variables for backend/frontend.
  - `README.md`, `SETUP_GUIDE.md`: Documentation and setup instructions.

---

## 4. System Flow & Useful Information

- **Startup**:  
  - Backend starts via `main.py`, loads agents, config, and models.
  - Frontend starts via `App.js`/`App.jsx`, loads UI and connects to backend API.

- **Data Flow**:  
  - User interacts with React SPA → API requests sent to FastAPI backend → Agents process tasks → Results returned to frontend.

- **Observability**:  
  - All analytics and tracking are CopilotKit-native.
  - Health checks via `/health` endpoint.

- **Deployment**:  
  - Local: Run backend and frontend separately.
  - Render: Set root directory to `copilotkit-frontend/`, use `yarn install && yarn build`, `yarn start`.

---

## 5. Example Diagrams

**System Architecture:**

```
[User] <---> [React SPA Frontend] <---> [FastAPI Backend] <---> [SQLite/Redis DB]
                                      |---> [Agents, Missions, Analytics]
                                      |---> [CopilotKit Observability]
```

**Frontend Component Hierarchy:**

```
App.js/App.jsx
├── NavBar
├── Notification
├── SentinelInitializer
├── CopilotChat
├── Routes
│   ├── Dashboard
│   ├── Missions
│   ├── Analytics
│   ├── Settings
│   └── NotFound
```

---

## 6. Summary

Sentinel.ai is a modular, production-ready AI platform with:
- Clean separation of backend and frontend
- CopilotKit-native observability and analytics
- SQLite/Redis for robust data storage
- Advanced agent and mission logic
- Scalable deployment for local or cloud

---
