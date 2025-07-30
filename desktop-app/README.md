# Sentinel Desktop App (Local-Only)

This directory contains a fully self-contained, local-only version of the Sentinel agent command center. It is designed for personal use on your desktop, with no cloud, tunnel, or mobile app dependencies required.

## 🚀 Features
- Simple web UI for entering prompts and viewing agent results
- FastAPI backend running locally
- Direct integration with CrewAI and LangChain for agent logic
- No user accounts, no multi-user logic
- Can be extended with desktop automation, local file I/O, and more

## 📁 Project Structure
```
desktop-app/
├── src/                    # Source code
│   ├── api/               # API endpoints
│   ├── core/              # Core business logic
│   ├── models/            # Data models
│   └── utils/             # Utility functions
├── static/                # Static assets
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   ├── images/           # Images and icons
│   └── fonts/            # Font files
├── templates/             # HTML templates
├── config/               # Configuration files
├── logs/                 # Application logs
└── tests/                # Test files
```

## 🛠️ Installation & Usage

### Prerequisites
- Python 3.9+
- pip

### Quick Start
1. Install dependencies: `pip install -r requirements.txt`
2. Run the server: `python start_desktop_app.py`
3. Open your browser to [http://localhost:8001](http://localhost:8001)

### Development
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run with auto-reload
uvicorn src.main:app --reload --port 8001

# Run tests
pytest tests/
```

## 🔧 Configuration
- Environment variables are loaded from `.env` file
- Database configuration in `config/database.py`
- Agent settings in `config/agents.py`

## 📝 Notes
- This app is for local, personal use only. It does not expose any public endpoints.
- The rest of the Sentinel system (mobile app, backend, cloud) remains available and unchanged.
- If you want to add desktop automation or other features, see the TODOs in this directory.

## 🧹 Maintenance
- Logs are automatically rotated and cleaned up
- Database backups are stored in `backups/` directory
- Use `python manage_services.py` for service management 