# Sentinel CopilotKit Frontend

This is the new CopilotKit-powered SPA frontend for Sentinel.

## Features
- Modern React SPA using CopilotKit for agent and chat features
- Gemini LLM integration via Flask backend
- Modular pages: Dashboard, Missions, Analytics, Settings
- Real-time and chat capabilities

## Development

1. Install dependencies:
   ```sh
   npm install
   ```
2. Start the development server:
   ```sh
   npm start
   ```
   The app will be available at http://localhost:3000 and will proxy API requests to the Flask backend.

## Production Build

1. Build the app:
   ```sh
   npm run build
   ```
2. Serve the build output with your Flask backend or a static file server.

## LLM Integration
All LLM requests are routed to the Flask backend, which uses Gemini as configured in `.env`.

---

For more details, see the main Sentinel documentation.
