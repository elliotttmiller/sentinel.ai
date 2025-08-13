# Sentinel CopilotKit System Overview (August 2025)

## Current Architecture & Integrations

- **Backend:** FastAPI (Python), SQLAlchemy models for multi-tenancy, mission tracking, optimization proposals, logs, metrics, preferences
- **Database:** SQLite (no ChromaDB/vector DBs), Redis for caching/queueing
- **Observability/Analytics:** CopilotKit-native only (no Sentry, Wandb, Weave, or custom agent observability code)
- **Frontend:** React SPA, CopilotKit UI components
- **Deployment:** Local and self-hosted only (no Railway, Vercel, or legacy serverless configs)
- **Environment:** .env used for all secrets and API keys
- **LLM Integration:** Direct to LLM (Gemini, OpenAI, etc.) via CopilotKit runtime/adapters
- **Optimization:** supercharged_optimizer.py manages system optimization, configuration, and CopilotKit analytics
- **Status:** All obsolete code removed, backend and frontend are CopilotKit-native, ready for production

This system is now fully aligned with CopilotKit best practices and ready for robust, scalable operation.

# Sentinel CopilotKit Integration

## Endpoints

- **Frontend (React SPA):**
  - Local: http://localhost:3000
  - Production: [your production domain]

- **Backend (FastAPI):**
  - Local: http://localhost:8000
  - Remote: [https://thrush-real-lacewing.ngrok-free.app]
  - Health: /health
  - Status: /status
  - CopilotKit: /api/copilotkit (POST)
  - CopilotKit Info: /api/copilotkit/info (GET)
  - WebSocket: /ws

## Environment Variables

- **Frontend (.env):**
  - REACT_APP_API_URL=http://localhost:8000/api
  - REACT_APP_PUBLIC_API_KEY=ck_pub_011541242c359e759e3256628c64144b

- **Backend (.env):**
  - GOOGLE_API_KEY=AIzaSyDb0VpQBhxlS6JNWZfQEcgUckY9d4i0ARM
  - DATABASE_URL=postgresql://sentinel:sentinelpass@localhost:5432/sentinel_dbl
  - REDIS_URL_LOCAL=redis://localhost:6379
  - REDIS_URL_CLOUD=redis://default:Nybmod0YjbYq3KvjBu99zJDVw1FpJKK8@redis-18067.c253.us-central1-1.gce.redns.redis-cloud.com:18067

## Integration

- The React app is wrapped with CopilotKit provider using the correct runtimeUrl and publicApiKey.
- API requests are routed to the backend via proxy for local development.
- Backend endpoints are implemented and registered in FastAPI.
- WebSocket endpoint is available for real-time features.

## Remote Access

- Use ngrok or a static domain to expose your backend for remote CopilotKit integration.
- Update REACT_APP_API_URL in frontend .env for production.

## Health & Monitoring

- Use /health and /status endpoints for backend monitoring.

---

For further customization, add new endpoints to src/api/ or update frontend components as needed.
