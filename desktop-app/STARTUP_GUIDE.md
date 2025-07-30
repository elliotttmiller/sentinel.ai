# 🚀 Sentinel Automated Startup Guide

## Overview

The Sentinel system now has **fully automated startup** that handles everything from dependency installation to service monitoring. No more manual steps!

## 🎯 Why Automated Startup?

**Before:** You had to manually:
- Check Python version
- Install dependencies
- Run database migrations
- Start services individually
- Monitor services manually

**Now:** One command does everything:
- ✅ Automatic dependency detection and installation
- ✅ Database schema migration
- ✅ Service startup and health monitoring
- ✅ Real-time status monitoring
- ✅ Graceful shutdown

## 🚀 Quick Start Options

### Option 1: One-Click Windows Startup (Recommended)
```bash
# Double-click this file:
start_sentinel.bat
```

### Option 2: PowerShell Startup
```powershell
# Run in PowerShell:
.\start_sentinel.ps1
```

### Option 3: Python Direct Startup
```bash
# Run in terminal:
python start_sentinel.py
```

## 📋 What the Automated Startup Does

### 1. **Environment Check**
- ✅ Python version verification (3.8+)
- ✅ Project directory setup
- ✅ Required directories creation

### 2. **Dependency Management**
- ✅ Automatic detection of missing packages
- ✅ Installation of required dependencies:
  - `fastapi`, `uvicorn`, `sqlalchemy`
  - `psycopg2-binary`, `python-dotenv`
  - `loguru`, `requests`, `pydantic`
  - `crewai`, `langchain-google-genai`
  - `colorama`

### 3. **Environment Setup**
- ✅ Creates necessary directories (`logs`, `db`, `static`, `templates`)
- ✅ Creates default `.env` file if missing
- ✅ Validates configuration

### 4. **Database Migration**
- ✅ Runs `fix_database_schema.py` automatically
- ✅ Handles existing data safely
- ✅ Adds missing columns with proper defaults

### 5. **Service Startup**
- ✅ Starts Desktop App on port 8001
- ✅ Starts Cognitive Engine on port 8002
- ✅ Health check verification
- ✅ Service monitoring

### 6. **Real-time Monitoring**
- ✅ Continuous health monitoring
- ✅ Uptime tracking
- ✅ Status reporting every 30 seconds
- ✅ Graceful shutdown on Ctrl+C

## 🎮 Usage Examples

### First Time Setup
```bash
# Just run the startup script - it handles everything!
python start_sentinel.py
```

### Daily Startup
```bash
# Double-click start_sentinel.bat
# OR
.\start_sentinel.ps1
```

### Development Mode
```bash
# For development with auto-reload:
python start_sentinel.py
```

## 📊 What You'll See

```
============================================================
🚀 SENTINEL AUTOMATED STARTUP SYSTEM
============================================================
📅 Started at: 2025-07-30 07:45:00
📁 Project root: C:\Users\AMD\sentinel\desktop-app
============================================================

🔍 Checking Python version...
✅ Python 3.11.9 ✓

📦 Checking dependencies...
✅ fastapi ✓
✅ uvicorn ✓
✅ sqlalchemy ✓
✅ All dependencies are installed!

🔧 Setting up environment...
✅ Created directory: logs
✅ Created directory: db
✅ Created directory: static
✅ Created directory: templates
✅ Environment setup complete!

🗄️ Running database migration...
✅ Database migration completed!

🚀 Starting Sentinel services...
🚀 Starting Desktop App on port 8001...
✅ Desktop App started successfully!
🚀 Starting Cognitive Engine on port 8002...
✅ Cognitive Engine started successfully!

============================================================
🎉 SENTINEL STARTUP COMPLETE!
============================================================
📱 Desktop App: http://localhost:8001/
🧠 Cognitive Engine: http://localhost:8002/
🔧 Service Manager: python src/utils/manage_services.py
============================================================

👀 Monitoring services...
Press Ctrl+C to stop all services

============================================================
📊 Service Status - 07:45:30
============================================================
Desktop App (8001): 🟢 ONLINE - Uptime: 0:00:30
Cognitive Engine (8002): 🟢 ONLINE - Uptime: 0:00:30
```

## 🔧 Advanced Options

### Skip Dependency Checks
```bash
python start_sentinel.py --skip-checks
```

### Verbose Mode
```bash
python start_sentinel.py --verbose
```

### Custom Configuration
Edit `.env` file for custom settings:
```env
DATABASE_URL=your_database_url
LLM_MODEL=gemini-1.5-pro-latest
LLM_TEMPERATURE=0.7
GOOGLE_API_KEY=your_api_key
```

## 🛠️ Troubleshooting

### If Startup Fails:
1. **Check Python version**: Must be 3.8+
2. **Check internet connection**: For dependency installation
3. **Check ports**: 8001 and 8002 must be available
4. **Check permissions**: Run as administrator if needed

### Common Issues:
- **Port already in use**: Kill existing processes or change ports
- **Database connection failed**: Check DATABASE_URL in .env
- **Missing dependencies**: The script will auto-install them

### Manual Recovery:
```bash
# If automated startup fails, you can still run manually:
python src/utils/manage_services.py
```

## 🎉 Benefits

### ✅ **Zero Manual Steps**
- No more remembering commands
- No more manual dependency installation
- No more manual database setup

### ✅ **Reliable Startup**
- Automatic error detection
- Graceful failure handling
- Health monitoring

### ✅ **Development Friendly**
- Auto-reload enabled
- Real-time monitoring
- Easy debugging

### ✅ **Production Ready**
- Service monitoring
- Graceful shutdown
- Error logging

## 🚀 Ready to Use!

Now you can start Sentinel with just **one command**:

```bash
python start_sentinel.py
```

**That's it!** Everything else is automated. 🎉 