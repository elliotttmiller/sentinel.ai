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

## 2. Directory Tree Structure

```
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
├── src/
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
