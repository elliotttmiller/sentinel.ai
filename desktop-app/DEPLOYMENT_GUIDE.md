# Cognitive Forge Desktop App - Deployment Guide

## 🚀 Complete System Upgrade v3.0.0

This guide will walk you through deploying the advanced Cognitive Forge system with all its cutting-edge features.

## 📋 Prerequisites

- Python 3.11+
- Google API Key for Gemini
- Git (for version control)
- 4GB+ RAM recommended
- 2GB+ free disk space

## 🛠️ Installation Steps

### 1. Environment Setup

```bash
# Clone or navigate to the desktop-app directory
cd desktop-app

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Or install with specific versions
pip install fastapi==0.111.0 uvicorn[standard]==0.29.0 crewai==0.36.1
pip install langchain-google-genai==1.0.6 chromadb==0.5.0
pip install pydantic-settings==2.2.1 loguru==0.7.2
```

### 3. Configuration

```bash
# Copy the environment template
cp .env.template .env

# Edit the .env file with your settings
# Most importantly, set your GOOGLE_API_KEY
```

**Required Environment Variables:**
```env
GOOGLE_API_KEY=your_actual_google_api_key_here
LLM_MODEL=gemini-1.5-pro-latest
LLM_TEMPERATURE=0.7
```

### 4. Database Initialization

The system will automatically create:
- SQLite database: `db/sentinel_missions.db`
- ChromaDB vector memory: `db/chroma_memory/`
- Log files: `logs/cognitive_forge.log`

## 🚀 Starting the System

### Option 1: Using the Startup Script (Recommended)

```bash
# Run the comprehensive startup script
python start_cognitive_forge.py
```

This script will:
- ✅ Check all dependencies
- ✅ Create necessary directories
- ✅ Validate environment configuration
- ✅ Start the server with proper settings

### Option 2: Direct Server Start

```bash
# Start the FastAPI server directly
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

### Option 3: Development Mode

```bash
# For development with auto-reload
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

## 🌐 Accessing the System

Once started, access the system at:
- **Main Interface**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## 🧪 Testing the System

### Run Comprehensive Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python tests/test_cognitive_forge.py

# Run with verbose output
python -m pytest tests/ -v
```

### Manual Testing

1. **Health Check**: Visit http://localhost:8001/health
2. **System Stats**: Visit http://localhost:8001/system-stats
3. **API Status**: Visit http://localhost:8001/api/status

## 🔧 Advanced Configuration

### Customizing Agent Behavior

Edit `config/settings.py` or set environment variables:

```env
# Agent Settings
ENABLE_PLAN_VALIDATION=true
ENABLE_MEMORY_SYNTHESIS=true
ENABLE_REAL_TIME_UPDATES=true

# Performance Settings
WORKER_TIMEOUT=60
PLANNING_TIMEOUT=120
MAX_MISSION_DURATION=300
```

### Security Configuration

```env
# File Operations
ALLOWED_FILE_EXTENSIONS=.py,.js,.html,.css,.json,.txt,.md,.yml,.yaml

# Shell Commands
ALLOWED_SHELL_COMMANDS=ls,dir,pwd,echo,cat,head,tail,grep,find,python,pip
```

## 📊 System Architecture

### Core Components

1. **Cognitive Forge Engine** (`src/core/cognitive_forge_engine.py`)
   - Orchestrates multi-agent workflows
   - Manages mission planning and execution
   - Handles memory synthesis and learning

2. **Advanced Agents** (`src/agents/advanced_agents.py`)
   - Lead AI Architect (planning)
   - Plan Validator (quality assurance)
   - Senior Developer (code creation)
   - QA Tester (testing)
   - Code Analyzer (analysis)
   - System Integrator (deployment)
   - Memory Synthesizer (learning)

3. **Advanced Tools** (`src/tools/advanced_tools.py`)
   - File I/O operations
   - Safe shell execution
   - System monitoring
   - Code analysis

4. **Database System** (`src/models/advanced_database.py`)
   - SQLite persistence
   - ChromaDB vector memory
   - Real-time mission tracking

### API Endpoints

- `POST /advanced-mission` - Create new mission
- `GET /mission/{id}` - Get mission status
- `GET /missions` - List all missions
- `GET /system-stats` - System statistics
- `GET /memory/search` - Search mission memory
- `DELETE /mission/{id}` - Archive mission

## 🔍 Monitoring and Debugging

### Log Files

- **Application Logs**: `logs/cognitive_forge.log`
- **Mission Logs**: Individual mission logs in database
- **System Logs**: Database-stored system events

### Real-time Monitoring

The system provides real-time updates through:
- Web interface live feed
- Database mission updates
- Structured logging

### Debugging

```bash
# Enable debug mode
export DEBUG=true

# Increase log verbosity
export LOG_LEVEL=DEBUG

# Check system status
curl http://localhost:8001/system-stats
```

## 🚨 Troubleshooting

### Common Issues

1. **Missing Google API Key**
   ```
   Error: GOOGLE_API_KEY not set
   Solution: Set GOOGLE_API_KEY in .env file
   ```

2. **Database Connection Issues**
   ```
   Error: Database not accessible
   Solution: Check file permissions for db/ directory
   ```

3. **Memory Issues**
   ```
   Error: ChromaDB initialization failed
   Solution: Ensure write permissions for db/chroma_memory/
   ```

4. **Port Already in Use**
   ```
   Error: Port 8001 already in use
   Solution: Change PORT in .env or kill existing process
   ```

### Performance Optimization

1. **Memory Usage**: Monitor with `GET /system-stats`
2. **Concurrent Missions**: Adjust `MAX_CONCURRENT_MISSIONS`
3. **Timeout Settings**: Modify `WORKER_TIMEOUT` and `PLANNING_TIMEOUT`

## 🔄 Upgrading the System

### Version Updates

1. **Backup Data**
   ```bash
   cp -r db/ db_backup/
   cp -r logs/ logs_backup/
   ```

2. **Update Code**
   ```bash
   git pull origin main
   pip install -r requirements.txt
   ```

3. **Restart System**
   ```bash
   python start_cognitive_forge.py
   ```

## 📈 Advanced Features

### Memory and Learning

The system automatically:
- Stores mission outcomes in vector memory
- Learns from past successes and failures
- Provides context for future missions
- Synthesizes knowledge across missions

### Multi-Agent Orchestration

Each mission follows this workflow:
1. **Planning Phase**: Lead Architect creates execution plan
2. **Validation Phase**: Plan Validator ensures quality
3. **Execution Phase**: Worker agents execute tasks
4. **Memory Phase**: Outcomes are synthesized and stored

### Real-time Observability

- Live mission progress updates
- Detailed agent activity logging
- Performance metrics tracking
- Error handling and recovery

## 🎯 Next Steps

1. **Configure your Google API key**
2. **Start the system**: `python start_cognitive_forge.py`
3. **Access the interface**: http://localhost:8001
4. **Deploy your first mission** and watch the AI work!

## 📞 Support

For issues or questions:
- Check the logs in `logs/cognitive_forge.log`
- Review system stats at `/system-stats`
- Run tests with `python tests/test_cognitive_forge.py`

---

**🎉 Congratulations! You now have a state-of-the-art Cognitive Forge system running with advanced AI capabilities, memory, learning, and real-time observability.** 