# 🧪 Manual Testing Guide for Real-Time Observability

## Quick Start Testing

### **Step 1: Start Your Servers**
```bash
# Start the servers using your script
./start_servers_tabs.ps1
```

### **Step 2: Run the Automated Test**
```bash
# Navigate to desktop-app directory
cd desktop-app

# Run the comprehensive test
python test_real_time_data.py

# Or run a quick test
python test_real_time_data.py --quick
```

### **Step 3: Manual Browser Testing**

Open your browser and test these URLs:

#### **🌐 Dashboard Testing**
```
http://localhost:8001
```
- Check if the dashboard loads
- Look for real-time data in the Observability Hub
- Verify System Vitals chart is updating

#### **📊 API Endpoint Testing**
```
http://localhost:8001/api/observability/overview
http://localhost:8001/api/system/vitals
http://localhost:8001/observability/weave
http://localhost:8001/observability/sentry
http://localhost:8001/observability/wandb
```

---

## 🔍 Detailed Testing Steps

### **1. Test System Vitals**
```bash
curl http://localhost:8001/api/system/vitals
```
**Expected Response:**
```json
{
  "cpu_usage": 25.6,
  "memory_usage": 67.2,
  "disk_usage": 45.1
}
```

### **2. Test Observability Overview**
```bash
curl http://localhost:8001/api/observability/overview
```
**Expected Response:**
```json
{
  "weave": {
    "status": "ACTIVE",
    "active_traces": 0,
    "success_rate": 0,
    "avg_response_ms": 0
  },
  "sentry": {
    "status": "ACTIVE",
    "error_rate_percent": 0,
    "active_issues": 0,
    "uptime_percent": 99.9
  },
  "wandb": {
    "status": "INACTIVE",
    "active_runs": 0,
    "best_accuracy": 0,
    "avg_loss": 0
  }
}
```

### **3. Test Real-Time Streaming**
```bash
curl -N http://localhost:8001/api/observability/stream
```
**Expected Response:**
```
data: {"timestamp":"2025-08-01T03:15:30.123456","weave":{"status":"ACTIVE",...},"sentry":{...},"wandb":{...},"system_vitals":{"cpu_usage":25.6,"memory_usage":67.2,"disk_usage":45.1}}

data: {"timestamp":"2025-08-01T03:15:35.123456","weave":{"status":"ACTIVE",...},"sentry":{...},"wandb":{...},"system_vitals":{"cpu_usage":25.8,"memory_usage":67.3,"disk_usage":45.1}}
```

---

## 🎯 What to Look For

### **✅ Success Indicators**

1. **All endpoints return 200 status codes**
2. **JSON responses are properly formatted**
3. **System vitals show realistic values (0-100%)**
4. **Streaming endpoint provides continuous data**
5. **Dashboard displays live updates**

### **❌ Common Issues**

1. **"Connection refused"** - Server not running
2. **"404 Not Found"** - Endpoint not implemented
3. **"500 Internal Server Error"** - Backend error
4. **Empty or null data** - Integration not configured
5. **Streaming not working** - SSE implementation issue

---

## 🔧 Troubleshooting

### **Server Not Starting**
```bash
# Check if ports are in use
netstat -an | findstr :8001
netstat -an | findstr :8002

# Kill processes if needed
taskkill /F /PID <process_id>
```

### **API Endpoints Not Responding**
```bash
# Test basic connectivity
curl http://localhost:8001/health

# Check server logs
# Look for error messages in the terminal
```

### **Real-Time Data Not Updating**
1. **Check environment variables** are set correctly
2. **Verify integrations** are properly configured
3. **Look for error messages** in server logs
4. **Test individual systems** (Weave, Sentry, WandB)

---

## 📊 Expected Test Results

### **Full Test Success**
```
============================================================
🧪 Real-Time Observability Data Testing
============================================================
Testing against: http://localhost:8001
Timestamp: 2025-08-01 03:15:30

============================================================
🧪 Testing All Observability Endpoints
============================================================
✅ Observability Overview: Status 200
✅ System Vitals: Status 200
✅ Weave Data: Status 200
✅ Sentry Data: Status 200
✅ WandB Data: Status 200
✅ Live Events: Status 200
✅ Service Status: Status 200

============================================================
🧪 Testing Real-Time Streaming Endpoint
============================================================
✅ Streaming endpoint: Status 200
📊 Event 1:
   Timestamp: 2025-08-01T03:15:30.123456
   Weave Status: ACTIVE
   Sentry Status: ACTIVE
   WandB Status: INACTIVE
   CPU Usage: 25.6%
✅ Received 3 streaming events

============================================================
🧪 Test Report
============================================================
📊 Test Results Summary:
   Total Tests: 8
   Passed: 8
   Failed: 0
   Success Rate: 100.0%

💡 Recommendations:
   🎉 All tests passed! Your real-time observability is working correctly.
```

### **Partial Test Success**
```
📊 Test Results Summary:
   Total Tests: 8
   Passed: 6
   Failed: 2
   Success Rate: 75.0%

📋 Detailed Results:
   ✅ Observability Overview: PASS
   ✅ System Vitals: PASS
   ❌ Weave Data: FAIL
      Error: HTTP 500
   ✅ Sentry Data: PASS
   ❌ WandB Data: FAIL
      Error: HTTP 500
   ✅ Live Events: PASS
   ✅ Service Status: PASS
   ✅ Streaming: PASS

💡 Recommendations:
   ⚠️  Some tests failed. Check the error messages above.
   📖 Review the REAL_TIME_OBSERVABILITY_GUIDE.md for setup instructions.
```

---

## 🚀 Advanced Testing

### **Load Testing**
```bash
# Test multiple concurrent requests
for i in {1..10}; do
  curl http://localhost:8001/api/system/vitals &
done
wait
```

### **Long-Running Stream Test**
```bash
# Test streaming for 1 minute
timeout 60 curl -N http://localhost:8001/api/observability/stream
```

### **Integration-Specific Testing**

#### **Weave Testing**
```bash
# Deploy a test mission to generate Weave data
curl -X POST http://localhost:8001/api/missions \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Test mission for observability","title":"Test Mission"}'
```

#### **Sentry Testing**
```bash
# Trigger a test error
curl http://localhost:8001/sentry-debug
```

#### **WandB Testing**
```bash
# Check if WandB is properly configured
python -c "import wandb; print('WandB available:', wandb.run is not None)"
```

---

## 📝 Test Checklist

- [ ] Server starts without errors
- [ ] Dashboard loads correctly
- [ ] All API endpoints return 200 status
- [ ] System vitals show realistic values
- [ ] Observability overview contains all systems
- [ ] Streaming endpoint provides continuous data
- [ ] Data updates in real-time
- [ ] Error handling works gracefully
- [ ] Integration status indicators are correct

---

## 🎯 Success Criteria

Your real-time observability is working correctly if:

1. **All endpoints respond** with proper JSON data
2. **System vitals update** in real-time
3. **Streaming provides** continuous data flow
4. **Dashboard displays** live information
5. **Error handling** works gracefully
6. **Integration status** shows correct states

If all tests pass, congratulations! Your Strategic Command Center is fully operational with real-time observability! 🎉 