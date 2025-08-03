# 🚀 Sentinel Cognitive Forge v5.2

**Advanced AI-powered mission execution system with Unified Event Bus, real-time UI/UX, and comprehensive agent tracking**

## 🎯 Overview

Cognitive Forge v5.2 represents a complete system transformation with a **Unified Event Bus** architecture, enhanced real-time UI/UX, and comprehensive agent observability:

- **🌐 Unified Event Bus** - Centralized real-time data streaming across all system components
- **🎨 Enhanced UI/UX** - Professional dashboard with sleek scrollbars and responsive design
- **📊 Real-Time Observability** - Live agent tracking with detailed action monitoring
- **🔮 Predictive Caching** - Intelligent result caching for improved performance
- **📈 Machine Learning Integration** - Self-improving system that learns from execution patterns
- **🤖 Multi-Agent Tracking** - Detailed monitoring of every AI agent action and decision
- **🎯 Scrollbar Implementation** - Sleek, hover-activated scrollbars across all modals and containers

## ✨ Key Features

### 🌐 Unified Event Bus Architecture
- **Centralized Data Streaming** - Single `/api/events/stream` endpoint for all real-time data
- **Server-Sent Events (SSE)** - Efficient real-time updates without polling
- **Event Dispatcher** - Intelligent routing of events to appropriate UI components
- **Fallback Systems** - Robust error handling and graceful degradation
- **Performance Optimization** - Reduced server load and improved responsiveness

### 🎨 Enhanced UI/UX
- **Professional Dashboard** - Black Dashboard theme with blue accent colors
- **Sleek Scrollbars** - Always-visible, hover-activated scrollbars across all containers
- **Responsive Design** - Mobile and tablet optimized layouts
- **Real-Time Updates** - Live data streaming to all dashboard components
- **Interactive Components** - Smooth transitions and hover effects

### 📊 Real-Time Observability
- **Live Agent Tracking** - Monitor every AI agent action in real-time
- **Action-Level Monitoring** - Track thinking, tool calls, decisions, and responses
- **Performance Metrics** - CPU, memory, execution time, and token usage
- **Decision Analytics** - Complete visibility into routing decisions
- **Error Tracking** - Comprehensive error monitoring with Sentry integration

### 🔮 Predictive Caching
- **Intelligent Result Caching** - Cache frequently requested results
- **Cache Hit Rate Optimization** - Automatic cache eviction and optimization
- **Performance Improvement Tracking** - Monitor cache effectiveness

### 🌐 Real-Time Observability
- **Live Log Streaming** - Server-Sent Events (SSE) for real-time updates
- **Unified Log Interception** - Capture logs from all system components
- **Comprehensive System Monitoring** - Health checks and performance metrics
- **Weave Integration** - Distributed tracing and monitoring
- **Weights & Biases** - Experiment tracking and analytics

## 🏗️ Architecture

### Core Components

```
Cognitive Forge v5.2
├── 🌐 Unified Event Bus
│   ├── Central Event Stream
│   ├── Event Dispatcher
│   ├── SSE Endpoints
│   └── Fallback Systems
├── 🎨 Enhanced UI/UX
│   ├── Professional Dashboard
│   ├── Sleek Scrollbars
│   ├── Responsive Design
│   └── Real-Time Updates
├── 🔧 Cognitive Forge Engine
│   ├── Golden Path (Fast Execution)
│   ├── Full Workflow (8-Phase Comprehensive)
│   └── Mission Orchestration
├── 📊 Enhanced Observability
│   ├── Agent Action Tracking
│   ├── Performance Monitoring
│   ├── Weave Integration
│   └── Weights & Biases
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
- **Observability**: Real-time action tracking

#### 🔵 Full Workflow (Comprehensive)
- **Use Case**: Complex tasks, detailed analysis
- **Execution**: 8-phase AI workflow with multiple agents
- **Typical Time**: 10-60 seconds
- **Examples**: "Design a microservice architecture", "Create a machine learning system"
- **Observability**: Detailed phase-by-phase tracking

### 8-Phase AI Workflow

1. **Planning & Analysis** - Problem analysis and requirements gathering
2. **Research & Information Gathering** - Comprehensive research and data collection
3. **Design & Architecture** - System design and architecture planning
4. **Implementation & Development** - Detailed code and configuration
5. **Testing & Validation** - Comprehensive testing strategies
6. **Optimization & Refinement** - Performance and quality improvements
7. **Documentation & Knowledge Synthesis** - Complete documentation
8. **Deployment & Integration** - Deployment and integration guidance

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
# Unified Event Bus Configuration
ENABLE_UNIFIED_EVENT_BUS=true
EVENT_STREAM_ENABLED=true
SSE_KEEPALIVE_INTERVAL=30

# UI/UX Configuration
ENABLE_ENHANCED_UI=true
SCROLLBAR_VISIBILITY=always
RESPONSIVE_DESIGN=true

# Hybrid System Configuration
ENABLE_HYBRID_MODE=true
AUTO_SWITCHING=true
HYBRID_SWITCH_THRESHOLD=0.4

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

# Enhanced Observability
ENABLE_ML_PREDICTION=true
ENABLE_PREDICTIVE_CACHING=true
ENABLE_ADVANCED_ANALYTICS=true
ENABLE_DYNAMIC_THRESHOLDS=true

# Weave & W&B Integration
WEAVE_PROJECT_NAME=cognitive-forge-v5
WANDB_PROJECT_NAME=cognitive-forge-v5
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
- **Observability Dashboard**: http://localhost:8001/api/observability/agent-analytics
- **Event Stream**: http://localhost:8001/api/events/stream

## 📊 API Endpoints

### Mission Management
- `POST /api/missions` - Create new mission with hybrid routing
- `GET /missions` - List all missions with metadata
- `GET /api/missions/{id}/updates` - Get real-time mission updates

### Unified Event Bus
- `GET /api/events/stream` - Server-Sent Events for live updates
- `GET /api/observability/live-stream` - Live observability stream
- `GET /api/system/logs/stream` - Real-time system logs

### Enhanced Observability
- `GET /api/observability/agent-analytics` - Comprehensive agent performance metrics
- `GET /api/observability/mission/{mission_id}` - Detailed mission observability
- `GET /api/observability/session/{session_id}` - Agent session details
- `GET /api/observability/report` - Complete observability report

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

## 🎨 UI/UX Enhancements

### Professional Dashboard
- **Black Dashboard Theme** - Professional dark theme with blue accents
- **Responsive Layout** - Mobile and tablet optimized
- **Interactive Components** - Smooth transitions and hover effects
- **Real-Time Updates** - Live data streaming to all components

### Sleek Scrollbars
- **Always Visible** - Scrollbars are always visible for better UX
- **Hover Activation** - Enhanced hover effects for better interaction
- **Cross-Browser Support** - Works on Chrome, Firefox, Safari, and Edge
- **Custom Styling** - Professional appearance with subtle backgrounds

### Container Modals
- **Active Missions Modal** - Real-time mission tracking with scrollbars
- **Agent Activity Modal** - Live agent activity with compact design
- **System Logs Modal** - Real-time log streaming with syntax highlighting
- **Live Stream Feed** - Comprehensive event streaming with scrollbars

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

- **Score < 0.4** → Golden Path (fast, simple)
- **Score ≥ 0.4** → Full Workflow (comprehensive, detailed)

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

## 📊 Enhanced Observability

### Agent Action Tracking

The system tracks every AI agent action with detailed metrics:

- **Thinking**: Agent reasoning and thought processes
- **Tool Calls**: External tool usage and results
- **Decisions**: Routing and decision-making processes
- **Responses**: Output generation and token usage
- **Errors**: Error handling and recovery

### Performance Metrics

- **Execution Time**: Detailed timing for each phase
- **Token Usage**: Input/output token tracking
- **Cost Estimation**: API cost tracking
- **Memory Usage**: System resource monitoring
- **CPU Usage**: Performance monitoring

### Real-Time Monitoring

```bash
# Get agent analytics
curl http://localhost:8001/api/observability/agent-analytics

# Get mission observability
curl http://localhost:8001/api/observability/mission/mission_123

# Get session details
curl http://localhost:8001/api/observability/session/session_456
```

## 📈 Performance Metrics

### Expected Improvements

- **50-70% faster** average execution time
- **95%+ user satisfaction** through intelligent routing
- **Zero database errors** with proper schema
- **Real-time observability** for debugging
- **Complete agent visibility** for optimization
- **Enhanced UI/UX** with professional scrollbars
- **Unified Event Bus** for efficient data streaming

### Monitoring

Access comprehensive analytics:

```bash
# Get hybrid system analytics
curl http://localhost:8001/api/hybrid/analytics

# Get system statistics
curl http://localhost:8001/api/system/stats

# Get observability report
curl http://localhost:8001/api/observability/report
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENABLE_UNIFIED_EVENT_BUS` | Enable unified event bus | `true` |
| `EVENT_STREAM_ENABLED` | Enable event streaming | `true` |
| `SSE_KEEPALIVE_INTERVAL` | SSE keepalive interval (seconds) | `30` |
| `ENABLE_ENHANCED_UI` | Enable enhanced UI features | `true` |
| `SCROLLBAR_VISIBILITY` | Scrollbar visibility mode | `always` |
| `RESPONSIVE_DESIGN` | Enable responsive design | `true` |
| `ENABLE_HYBRID_MODE` | Enable hybrid decision engine | `true` |
| `HYBRID_SWITCH_THRESHOLD` | Complexity threshold for path selection | `0.4` |
| `ENABLE_ML_PREDICTION` | Enable ML-based performance prediction | `true` |
| `ENABLE_PREDICTIVE_CACHING` | Enable intelligent result caching | `true` |
| `CACHE_SIZE_LIMIT` | Maximum cache entries | `1000` |
| `CACHE_TTL` | Cache time-to-live (seconds) | `3600` |
| `ENABLE_ADVANCED_ANALYTICS` | Enable enhanced analytics | `true` |
| `ENABLE_DYNAMIC_THRESHOLDS` | Enable dynamic threshold adjustment | `true` |

### Advanced Settings

```env
# Unified Event Bus Configuration
ENABLE_UNIFIED_EVENT_BUS=true
EVENT_STREAM_ENABLED=true
SSE_KEEPALIVE_INTERVAL=30
EVENT_BUFFER_SIZE=1000

# UI/UX Configuration
ENABLE_ENHANCED_UI=true
SCROLLBAR_VISIBILITY=always
RESPONSIVE_DESIGN=true
HOVER_EFFECTS=true

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

# Observability Configuration
WEAVE_PROJECT_NAME=cognitive-forge-v5
WANDB_PROJECT_NAME=cognitive-forge-v5
SENTRY_DSN=your_sentry_dsn_here
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
│   │   ├── weave_observability.py
│   │   ├── agent_observability.py
│   │   └── google_ai_wrapper.py
│   └── main.py
├── config/
│   └── settings.py
├── static/
│   ├── css/
│   │   └── sentinel-dash.css
│   └── js/
│       └── unified-realtime.js
├── templates/
│   └── index.html
├── logs/
├── db/
├── tests/
├── pyproject.toml
└── start_cognitive_forge.py
```

### Testing

```bash
# Test unified event bus
curl http://localhost:8001/api/events/stream

# Test mission creation
curl -X POST http://localhost:8001/api/missions \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello world", "title": "Test"}'

# Test observability
curl http://localhost:8001/api/observability/agent-analytics
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

3. **Event Bus Issues**
   ```bash
   # Check event stream
   curl http://localhost:8001/api/events/stream
   
   # Test SSE connection
   curl -N http://localhost:8001/api/events/stream
   ```

4. **UI/UX Issues**
   ```bash
   # Check static files
   curl http://localhost:8001/static/css/sentinel-dash.css
   
   # Test JavaScript
   curl http://localhost:8001/static/js/unified-realtime.js
   ```

5. **Hybrid Engine Not Working**
   ```bash
   # Check configuration
   curl http://localhost:8001/api/hybrid/status
   
   # Test analysis
   curl -X POST http://localhost:8001/api/hybrid/analyze \
     -H "Content-Type: application/json" \
     -d '{"prompt": "test", "title": "Test"}'
   ```

6. **Observability Issues**
   ```bash
   # Check observability endpoints
   curl http://localhost:8001/api/observability/agent-analytics
   curl http://localhost:8001/api/observability/report
   ```

### Logs

- **Application Logs**: `logs/cognitive_forge.log`
- **Engine Logs**: `logs/cognitive_engine.log`
- **Real-Time Logs**: http://localhost:8001/api/logs/live
- **Streaming Logs**: http://localhost:8001/api/events/stream
- **Observability Logs**: `logs/desktop_app.log`

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
ENABLE_UNIFIED_EVENT_BUS=true
EVENT_STREAM_ENABLED=true
ENABLE_ENHANCED_UI=true
ENABLE_HYBRID_MODE=true
ENABLE_ML_PREDICTION=true
ENABLE_PREDICTIVE_CACHING=true
ENABLE_ADVANCED_ANALYTICS=true
ENABLE_DYNAMIC_THRESHOLDS=true

# Security
ALLOWED_FILE_EXTENSIONS=.py,.js,.html,.css,.json,.txt,.md
ALLOWED_SHELL_COMMANDS=ls,dir,pwd,echo,cat,head,tail,grep,find

# Performance
CACHE_SIZE_LIMIT=1000
CACHE_TTL=3600
LOG_BUFFER_SIZE=200
EVENT_BUFFER_SIZE=1000

# Observability
WEAVE_PROJECT_NAME=cognitive-forge-v5-prod
WANDB_PROJECT_NAME=cognitive-forge-v5-prod
SENTRY_DSN=your_production_sentry_dsn
```

## 📚 Documentation

- **API Documentation**: http://localhost:8001/docs
- **System Status**: http://localhost:8001/health
- **Hybrid Analytics**: http://localhost:8001/api/hybrid/analytics
- **Agent Analytics**: http://localhost:8001/api/observability/agent-analytics
- **Observability Report**: http://localhost:8001/api/observability/report
- **Event Stream**: http://localhost:8001/api/events/stream

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
5. Review observability data at http://localhost:8001/api/observability/agent-analytics
6. Test event stream at http://localhost:8001/api/events/stream

---

**🚀 Cognitive Forge v5.2 - The Future of AI Mission Execution with Unified Event Bus and Enhanced UI/UX** 