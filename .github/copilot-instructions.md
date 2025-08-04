# 🧑‍💻 Copilot Instructions for Sentinel Cognitive Forge

## Big Picture Architecture
- Distributed, event-driven AI platform with FastAPI backend, real-time dashboard frontend, and modular agent engine.
- Major components:
  - `desktop-app/` (UI, API, agent runner; see `src/` for FastAPI and engine)
  - `backend/` (cloud backend, Railway deployment)
  - `mobile-app/` (React Native client)
  - `shared/` (shared types/utilities)
- Data flows via REST APIs and Server-Sent Events (SSE) for real-time updates. All agent, mission, and analytics data is live-tracked.
- The agent engine uses an 8-phase workflow (see `src/core/cognitive_forge_engine.py`), dynamically assembling agent crews per mission. See also `sentinel_overview.txt` for role breakdowns.

## Developer Workflows
- **Start servers:** Use `desktop-app/start_servers.ps1` to launch both the dashboard and cognitive engine (ports 8001, 8002).
- **Run tests:**
  - All: `python -m pytest tests/`
  - Specific: `python test_fix_ai.py`, `python comprehensive_system_test.py`
- **Live API testing:** Use `curl` against endpoints like `/api/missions`, `/api/events/stream`, `/api/observability/agent-analytics` (see `README.md`).
- **Database:** SQLite for local, PostgreSQL/ChromaDB for production. See `db/` and `src/models/advanced_database.py`.
- **Debugging:** Logs in `logs/`, real-time via `/api/system/logs/stream`. Sentry and W&B are integrated (see `.env`, `src/utils/sentry_integration.py`).
- **Manual/automated testing:** See `MANUAL_TESTING_GUIDE.md` and `README.md` for guides and test endpoints.

## Project-Specific Conventions
- **UI:** Black Dashboard theme, always-visible scrollbars, Alpine.js for reactivity. See `static/` and `templates/` (e.g., `templates/ai-agents.html`).
- **Agent roles:** Defined in `src/agents/advanced_agents.py` (PromptAlchemist, GrandArchitect, Debugger, etc.).
- **Live data:** All dashboard metrics and agent activity are real-time via unified event bus (`static/js/unified-realtime.js`).
- **Config:** Use `.env` and `config.py` for all environment variables (see `README.md` for required keys like `GOOGLE_API_KEY`).
- **Fallback logic:** If core modules are missing, `src/main.py` provides fallback classes for database, engine, and observability. Agents should handle missing dependencies gracefully.
- **Error handling:** Use loguru for logging. All API endpoints should log errors and return structured error responses.

## Integration Points
- **External LLMs:** Google, OpenAI, Anthropic (API keys required, see `src/utils/google_ai_wrapper.py`).
- **Observability:** W&B and Sentry are optional but recommended for analytics and error tracking.
- **Mobile/Cloud:** Mobile app connects via REST/SSE to backend, backend relays to desktop via secure tunnel (Cloudflare/ngrok).

## Extending the System
- **Add a new agent:** Extend `src/agents/advanced_agents.py`, register in `cognitive_forge_engine.py`.
- **Add a dashboard metric:** Update `static/js/unified-realtime.js` and relevant `templates/*.html`.
- **Add a new API endpoint:** Follow FastAPI patterns in `src/main.py`. Use Pydantic models for request/response.
- **Add a new UI feature:** Use Alpine.js for reactivity, update `static/` and `templates/`.

## Troubleshooting & Environment
- **Startup errors:** Check for missing env vars (e.g., `GOOGLE_API_KEY`), database connection issues, or import errors. Fallback logic in `src/main.py` will log and simulate core services if needed.
- **Live data not updating:** Ensure unified event bus is enabled in `.env` and `config.py`.
- **Sentry/W&B:** See `src/utils/sentry_integration.py` and `SENTRY_SETUP.md` for setup.

## Examples
- To test live mission creation: `curl -X POST http://localhost:8001/api/missions -d '{"prompt": "Test", "title": "Test"}'`
- To stream live events: `curl http://localhost:8001/api/events/stream`
- To add a new agent: see `src/agents/advanced_agents.py` and register in `src/core/cognitive_forge_engine.py`.

---
For more, see `desktop-app/README.md`, `src/utils/system_cheatsheet.txt`, and `sentinel_overview.txt`.
