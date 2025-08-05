# Sentinel AI - System Configuration Guide

## Quick Start

### 1. Install Dependencies
```bash
cd desktop-app
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Run the system optimizer to check configuration
python system_optimizer.py

# Edit the generated .env file with your API keys
nano .env
```

### 3. Required Configuration
Add these to your `.env` file:
```env
GOOGLE_API_KEY=your_google_api_key_here
LLM_MODEL=gemini-1.5-pro
LLM_TEMPERATURE=0.7
```

### 4. Start the System
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

### 5. Access the Dashboard
Open: http://localhost:8001

## Recent Fixes Applied

### ✅ LLM Provider Error Fixed
- **Issue**: `litellm.BadRequestError: LLM Provider NOT provided`
- **Cause**: Model name format incompatibility between langchain-google-genai and litellm
- **Solution**: Comprehensive model name formatting fixes applied at multiple levels

### ✅ Docker Configuration Optimized
- Cleaned up redundant Docker availability checks
- Better error handling for containerization features

### ✅ System Optimization Tools Added
- `system_optimizer.py`: Comprehensive system configuration checker
- `test_simple_logic.py`: Verification of LLM fix logic
- Automatic `.env` template generation

## System Architecture

```
src/
├── main.py              # Main FastAPI application
├── core/
│   ├── execution_workflow.py    # CrewAI orchestration  
│   └── sandbox_executor.py     # Code execution environment
├── agents/
│   └── executable_agent.py     # AI agent definitions
├── utils/
│   ├── google_ai_wrapper.py    # LLM configuration (FIXED)
│   ├── llm_patch.py            # Runtime compatibility patches
│   └── litellm_custom_provider.py  # LiteLLM configuration
└── config/
    └── settings.py             # Application settings
```

## Testing the Fix

### Verify LLM Configuration
```bash
python test_simple_logic.py
```
Expected output: All tests should pass ✅

### Full System Check
```bash  
python system_optimizer.py
```
Expected output: System optimized and ready 🎉

### Test Mission Execution
1. Start the server: `uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload`
2. Open the dashboard: http://localhost:8001
3. Create a simple mission: "Create a file named 'test.txt' with the content 'Hello World'"
4. The mission should execute successfully without LLM provider errors

## Troubleshooting

### Common Issues

**1. Missing API Key**
```
❌ Missing required variable: GOOGLE_API_KEY
```
Solution: Add your Google API key to the `.env` file

**2. Import Errors**
```
ModuleNotFoundError: No module named 'crewai'
```
Solution: Install dependencies with `pip install -r requirements.txt`

**3. LLM Provider Error (Should be fixed)**
```
litellm.BadRequestError: LLM Provider NOT provided
```
Solution: This should be resolved by the recent fixes. If it persists, check the model name configuration.

**4. Docker Warnings**
```
WARNING: Docker is not available
```
Solution: This is non-critical. The system will use local execution instead of containerized execution.

## Performance Optimization

### Recommended Settings
- **CPU**: 2+ cores
- **RAM**: 4GB+ available
- **Storage**: 1GB+ free space for logs and database
- **Network**: Stable internet connection for API calls

### Production Deployment
- Use a production ASGI server like Gunicorn
- Configure proper logging levels
- Set up monitoring with Sentry/Wandb
- Use PostgreSQL instead of SQLite for better performance

## Support
- Check the logs in `logs/` directory for detailed error information
- Run `python system_optimizer.py` to verify configuration
- All fixes are documented in `LLM_FIX_README.md`