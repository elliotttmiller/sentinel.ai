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
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Agent Engine Setup**
   ```bash
   cd agent-engine
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
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