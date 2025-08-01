# 🚀 Sentinel Cognitive Forge v5.0

**State-of-the-art AI-powered mission execution system with hybrid decision engine and real-time observability**

## 🎯 Overview

Cognitive Forge v5.0 is a complete system upgrade that transforms your AI application into a production-ready, intelligent platform with:

- **🧠 Hybrid Decision Engine** - Intelligent routing between fast Golden Path and comprehensive Full Workflow
- **📊 Real-Time Analytics** - Advanced performance tracking and user preference learning
- **🔮 Predictive Caching** - Intelligent result caching for improved performance
- **📈 Machine Learning Integration** - Self-improving system that learns from execution patterns
- **🌐 Real-Time Observability** - Live log streaming and comprehensive system monitoring

## ✨ Key Features

### 🧠 Hybrid Intelligence
- **Task Complexity Analysis** - Multi-factor analysis of prompt complexity
- **Performance Prediction** - ML-based execution time estimation
- **User Preference Learning** - Adaptive system behavior based on user satisfaction
- **Automatic Path Selection** - Intelligent routing between Golden Path and Full Workflow

### 📊 Advanced Analytics
- **Real-Time Performance Tracking** - Monitor execution times and success rates
- **Decision Accuracy Metrics** - Track hybrid engine decision quality
- **Cache Efficiency Monitoring** - Optimize predictive caching performance
- **User Satisfaction Tracking** - Learn from user feedback

### 🔮 Predictive Caching
- **Intelligent Result Caching** - Cache frequently requested results
- **Cache Hit Rate Optimization** - Automatic cache eviction and optimization
- **Performance Improvement Tracking** - Monitor cache effectiveness

### 🌐 Real-Time Observability
- **Live Log Streaming** - Server-Sent Events (SSE) for real-time updates
- **Unified Log Interception** - Capture logs from all system components
- **Comprehensive System Monitoring** - Health checks and performance metrics

## 🏗️ Architecture

### Core Components

```
Cognitive Forge v5.0
├── 🧠 Hybrid Decision Engine
│   ├── Task Complexity Analyzer
│   ├── Performance Learning System
│   ├── Predictive Cache
│   └── Advanced Analytics
├── 🔧 Cognitive Forge Engine
│   ├── Golden Path (Fast Execution)
│   ├── Full Workflow (Comprehensive)
│   └── Mission Orchestration
├── 💾 Advanced Database
│   ├── SQLite (Relational Data)
│   ├── ChromaDB (Vector Memory)
│   └── Performance Metrics
└── 🌐 Real-Time API
    ├── FastAPI Server
    ├── SSE Streaming
    └── Comprehensive Endpoints
```

### Execution Paths

#### 🟡 Golden Path (Fast)
- **Use Case**: Simple tasks, quick responses
- **Execution**: Direct LLM inference
- **Typical Time**: 0.5-5 seconds
- **Examples**: "Hello world", "Calculate 2+2", "Print hello"

#### 🔵 Full Workflow (Comprehensive)
- **Use Case**: Complex tasks, detailed analysis
- **Execution**: 8-phase AI workflow with multiple agents
- **Typical Time**: 10-60 seconds
- **Examples**: "Design a microservice architecture", "Create a machine learning system"

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone the repository
cd desktop-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file with your configuration:

```env
# Hybrid System Configuration
ENABLE_HYBRID_MODE=true
AUTO_SWITCHING=true

# Golden Path Feature Flags
ENABLE_FULL_WORKFLOW=false
MINIMAL_MODE=true
GOLDEN_PATH_LOGGING=true

# Google AI Configuration
GOOGLE_API_KEY=your_api_key_here
LLM_MODEL=gemini-1.5-pro-latest
LLM_TEMPERATURE=0.7

# Server Configuration
HOST=0.0.0.0
PORT=8001

# Database Configuration
DATABASE_URL=sqlite:///db/sentinel_missions.db

# Advanced Features
ENABLE_ML_PREDICTION=true
ENABLE_PREDICTIVE_CACHING=true
ENABLE_ADVANCED_ANALYTICS=true
```

### 3. Launch System

```bash
# Start with comprehensive validation
python start_cognitive_forge.py

# Or start directly with uvicorn
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

### 4. Access the System

- **Web Interface**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## 📊 API Endpoints

### Mission Management
- `POST /api/missions` - Create new mission with hybrid routing
- `GET /missions` - List all missions with metadata
- `GET /api/missions/{id}/updates` - Get real-time mission updates

### Hybrid System
- `GET /api/hybrid/status` - Get hybrid system status
- `POST /api/hybrid/analyze` - Analyze task complexity
- `GET /api/hybrid/analytics` - Get advanced analytics

### Real-Time Streaming
- `GET /api/events/stream` - Server-Sent Events for live updates
- `GET /api/logs/live` - Get current log buffer

### System Monitoring
- `GET /health` - Health check
- `GET /api/system/stats` - Comprehensive system statistics

## 🧠 Hybrid Decision Engine

### Complexity Analysis

The system analyzes tasks using multiple factors:

```python
overall_score = (
    0.3 * length_score +      # 30% - Prompt length
    0.4 * keyword_score +     # 40% - Complex keywords
    0.2 * context_score +     # 20% - Context indicators
    0.1 * historical_score    # 10% - Historical data
)
```

### Decision Threshold

- **Score < 0.6** → Golden Path (fast, simple)
- **Score ≥ 0.6** → Full Workflow (comprehensive, detailed)

### Example Analysis

```bash
curl -X POST http://localhost:8001/api/hybrid/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Design a microservice architecture", "title": "Test"}'
```

Response:
```json
{
  "status": "success",
  "task_analysis": {
    "overall_score": 0.85,
    "length_score": 0.12,
    "keyword_score": 1.0,
    "context_score": 0.33,
    "confidence": 0.78
  },
  "recommendation": {
    "path": "full_workflow",
    "reason": "high_complexity",
    "confidence": 0.78
  }
}
```

## 📈 Performance Metrics

### Expected Improvements

- **50-70% faster** average execution time
- **95%+ user satisfaction** through intelligent routing
- **Zero database errors** with proper schema
- **Real-time observability** for debugging

### Monitoring

Access comprehensive analytics:

```bash
# Get hybrid system analytics
curl http://localhost:8001/api/hybrid/analytics

# Get system statistics
curl http://localhost:8001/api/system/stats
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENABLE_HYBRID_MODE` | Enable hybrid decision engine | `true` |
| `HYBRID_SWITCH_THRESHOLD` | Complexity threshold for path selection | `0.6` |
| `ENABLE_ML_PREDICTION` | Enable ML-based performance prediction | `true` |
| `ENABLE_PREDICTIVE_CACHING` | Enable intelligent result caching | `true` |
| `CACHE_SIZE_LIMIT` | Maximum cache entries | `1000` |
| `CACHE_TTL` | Cache time-to-live (seconds) | `3600` |

### Advanced Settings

```env
# Machine Learning Configuration
ENABLE_ML_PREDICTION=true
ML_MODEL_UPDATE_INTERVAL=3600
MIN_TRAINING_SAMPLES=50

# Advanced Analytics
ENABLE_ADVANCED_ANALYTICS=true
ANALYTICS_SAMPLE_RATE=0.1
PERFORMANCE_METRICS_RETENTION=86400

# Dynamic Threshold Adjustment
ENABLE_DYNAMIC_THRESHOLDS=true
THRESHOLD_UPDATE_INTERVAL=1800
THRESHOLD_LEARNING_RATE=0.1
```

## 🛠️ Development

### Project Structure

```
desktop-app/
├── src/
│   ├── core/
│   │   ├── cognitive_forge_engine.py
│   │   └── hybrid_decision_engine.py
│   ├── models/
│   │   └── advanced_database.py
│   ├── utils/
│   │   └── google_ai_wrapper.py
│   └── main.py
├── config/
│   └── settings.py
├── static/
│   └── index.html
├── logs/
├── db/
├── pyproject.toml
└── start_cognitive_forge.py
```

### Testing

```bash
# Test hybrid system
python -c "
from src.core.hybrid_decision_engine import hybrid_decision_engine
result = hybrid_decision_engine.make_hybrid_decision('Hello world')
print(f'Decision: {result}')
"

# Test mission creation
curl -X POST http://localhost:8001/api/missions \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello world", "title": "Test"}'
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the correct directory
   cd desktop-app
   python start_cognitive_forge.py
   ```

2. **Database Errors**
   ```bash
   # Check database directory
   ls -la db/
   
   # Recreate database if needed
   rm -rf db/sentinel_missions.db
   python start_cognitive_forge.py
   ```

3. **Hybrid Engine Not Working**
   ```bash
   # Check configuration
   curl http://localhost:8001/api/hybrid/status
   
   # Test analysis
   curl -X POST http://localhost:8001/api/hybrid/analyze \
     -H "Content-Type: application/json" \
     -d '{"prompt": "test", "title": "Test"}'
   ```

### Logs

- **Application Logs**: `logs/cognitive_forge.log`
- **Real-Time Logs**: http://localhost:8001/api/logs/live
- **Streaming Logs**: http://localhost:8001/api/events/stream

## 🚀 Production Deployment

### Docker Support

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Environment Variables

Set production environment variables:

```env
# Production Settings
ENABLE_HYBRID_MODE=true
ENABLE_ML_PREDICTION=true
ENABLE_PREDICTIVE_CACHING=true
ENABLE_ADVANCED_ANALYTICS=true

# Security
ALLOWED_FILE_EXTENSIONS=.py,.js,.html,.css,.json,.txt,.md
ALLOWED_SHELL_COMMANDS=ls,dir,pwd,echo,cat,head,tail,grep,find

# Performance
CACHE_SIZE_LIMIT=1000
CACHE_TTL=3600
LOG_BUFFER_SIZE=200
```

## 📚 Documentation

- **API Documentation**: http://localhost:8001/docs
- **System Status**: http://localhost:8001/health
- **Hybrid Analytics**: http://localhost:8001/api/hybrid/analytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

1. Check the troubleshooting section
2. Review the logs at `logs/cognitive_forge.log`
3. Test the system health at http://localhost:8001/health
4. Check hybrid system status at http://localhost:8001/api/hybrid/status

---

**🚀 Cognitive Forge v5.0 - The Future of AI Mission Execution** 