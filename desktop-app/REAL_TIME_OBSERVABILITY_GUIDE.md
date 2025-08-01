# 🚀 Real-Time Observability Integration Guide

## Overview

This guide shows you how to integrate **real-time live data** from Weave, Sentry, and WandB into your Strategic Command Center. The system is designed to provide live monitoring, tracing, and analytics for your AI operations.

## 🎯 What You'll Get

### **Real-Time Dashboard Data**
- **Weave**: Live mission traces, agent performance, execution times
- **Sentry**: Real-time error rates, uptime monitoring, issue tracking
- **WandB**: Live experiment metrics, model performance, accuracy tracking
- **System Vitals**: CPU, memory, disk usage in real-time

### **Live Streaming**
- Server-Sent Events (SSE) for real-time updates
- 5-second refresh intervals
- Automatic error handling and recovery

---

## 📋 Setup Instructions

### **Step 1: Environment Configuration**

Create or update your `.env` file in the `desktop-app` directory:

```bash
# =============================================================================
# OBSERVABILITY CONFIGURATION
# =============================================================================

# Weave Observability
WEAVE_PROJECT_NAME=cognitive-forge-v5
WEAVE_API_KEY=your_weave_api_key_here  # Optional

# Sentry Error Tracking
SENTRY_AUTH_TOKEN=your_sentry_auth_token_here
SENTRY_ORG_SLUG=your_organization_slug
SENTRY_PROJECT_ID=your_project_id
SENTRY_DSN=https://your_dsn_here@sentry.io/project_id

# WandB Experiment Tracking
WANDB_API_KEY=your_wandb_api_key_here
WANDB_PROJECT=cognitive-forge-v5
WANDB_ENTITY=your_username_or_team
```

### **Step 2: Get Your Credentials**

#### **🔍 Weave Setup**
1. Visit [https://weave.ai](https://weave.ai)
2. Create an account and project
3. Get API key from settings (optional for basic functionality)
4. Weave automatically tracks all mission executions

#### **🚨 Sentry Setup**
1. Visit [https://sentry.io](https://sentry.io)
2. Create account and organization
3. Create a new project
4. Go to **Settings > API > Auth Tokens**
5. Create a new token with `project:read` scope
6. Get **Project ID** from project settings
7. Get **DSN** from project settings

#### **📊 WandB Setup**
1. Visit [https://wandb.ai](https://wandb.ai)
2. Create account
3. Go to **Settings > API Keys**
4. Create a new API key
5. Note your username/team name for entity

### **Step 3: Install Dependencies**

```bash
# Navigate to desktop-app directory
cd desktop-app

# Install observability packages
pip install weave wandb sentry-sdk
```

### **Step 4: Verify Integration**

Run the status checker:

```bash
python observability_config.py
```

You should see:
```
🔍 Observability Integration Status Check
==================================================

📊 WEAVE:
   Status: READY
   Enabled: True

📊 SENTRY:
   Status: READY
   Enabled: True

📊 WANDB:
   Status: READY
   Enabled: True
```

---

## 🎮 How to Use Real-Time Data

### **1. Dashboard Integration**

The Strategic Command Center automatically displays real-time data:

- **System Vitals**: Live CPU/memory charts
- **Observability Hub**: Real-time Weave/Sentry/WandB metrics
- **Active Missions**: Live mission status updates
- **Live Event Feed**: Real-time system events

### **2. API Endpoints**

#### **Overview Data**
```bash
GET /api/observability/overview
```
Returns real-time summary of all systems.

#### **Individual System Data**
```bash
GET /observability/weave      # Weave traces and performance
GET /observability/sentry     # Sentry error tracking
GET /observability/wandb      # WandB experiment data
```

#### **Real-Time Streaming**
```bash
GET /api/observability/stream
```
Server-Sent Events stream with 5-second updates.

### **3. Live Data Examples**

#### **Weave Real-Time Data**
```json
{
  "status": "ACTIVE",
  "active_traces": 3,
  "success_rate": 98.5,
  "avg_response_ms": 245,
  "total_traces": 156,
  "recent_traces": [...],
  "performance_metrics": {
    "total_missions": 45,
    "avg_execution_time": 12.3,
    "total_cost": 0.85,
    "memory_usage": 67.2,
    "cpu_usage": 23.1
  }
}
```

#### **Sentry Real-Time Data**
```json
{
  "status": "ACTIVE",
  "error_rate": 0.1,
  "active_issues": 2,
  "uptime": 99.9,
  "recent_issues": [...],
  "issue_types": {
    "TypeError": 1,
    "ConnectionError": 1
  }
}
```

#### **WandB Real-Time Data**
```json
{
  "status": "ACTIVE",
  "active_runs": 1,
  "accuracy": 94.2,
  "loss": 0.023,
  "experiments": [...],
  "metrics": {
    "best_accuracy": 96.1,
    "avg_loss": 0.018
  }
}
```

---

## 🔧 Advanced Configuration

### **Custom Weave Project**
```python
# In your .env file
WEAVE_PROJECT_NAME=my-custom-project
```

### **Sentry Error Filtering**
```python
# The system automatically filters by:
# - Last 24 hours for overview
# - Last 1 hour for streaming
# - Project-specific issues
```

### **WandB Experiment Tracking**
```python
# Automatically tracks:
# - Model accuracy and loss
# - Training metrics
# - Experiment comparisons
```

---

## 🚨 Troubleshooting

### **Common Issues**

#### **"Weave not available"**
```bash
pip install weave
# Check if weave is properly initialized in logs
```

#### **"Sentry API credentials not configured"**
- Verify `SENTRY_AUTH_TOKEN` is set
- Check `SENTRY_ORG_SLUG` and `SENTRY_PROJECT_ID`
- Ensure token has `project:read` scope

#### **"WandB not configured"**
```bash
pip install wandb
# Set WANDB_API_KEY in .env
```

### **Status Check Commands**

```bash
# Check all integrations
python observability_config.py

# Test individual endpoints
curl http://localhost:8001/api/observability/overview
curl http://localhost:8001/observability/weave
curl http://localhost:8001/observability/sentry
curl http://localhost:8001/observability/wandb
```

---

## 🎯 Real-Time Features

### **Live Updates**
- **5-second refresh intervals**
- **Automatic error recovery**
- **Graceful degradation** when services are unavailable

### **Data Visualization**
- **Real-time charts** for system vitals
- **Live status indicators** for all systems
- **Dynamic metrics** in the Observability Hub

### **Error Handling**
- **Automatic fallbacks** to simulated data
- **Detailed error logging** for debugging
- **Graceful service degradation**

---

## 🚀 Next Steps

1. **Set up your credentials** using the guide above
2. **Restart your servers** to load the new configuration
3. **Check the dashboard** for real-time data
4. **Monitor the logs** for any integration issues
5. **Customize** the refresh intervals and data sources as needed

Your Strategic Command Center will now display **real-time live data** from all your observability systems! 🎉

---

## 📞 Support

If you encounter issues:
1. Check the logs for detailed error messages
2. Verify all environment variables are set correctly
3. Test individual API endpoints
4. Run the status checker: `python observability_config.py`

The system is designed to work even with partial configurations, so you can set up integrations gradually. 