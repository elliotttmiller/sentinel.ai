# Sentry API Setup Guide

## 🎯 Your Sentry Configuration

Based on your Sentry project, here are your credentials:

### Current Configuration:
- **Project ID:** `4509764514938880`
- **Org Slug:** `adminai`
- **DSN:** `https://bab9b47561dd7ee4f5d1db13fda02c37@o4509683080822784.ingest.us.sentry.io/4509764514938880`

## 📝 Add to Your .env File

Add these lines to your `.env` file:

```bash
# Existing Sentry DSN (for error reporting)
SENTRY_DSN=https://bab9b47561dd7ee4f5d1db13fda02c37@o4509683080822784.ingest.us.sentry.io/4509764514938880

# NEW: Sentry API credentials (for automated debugging)
SENTRY_AUTH_TOKEN=your_auth_token_here
SENTRY_ORG_SLUG=adminai
SENTRY_PROJECT_ID=4509764514938880
```

## 🔑 How to Get Your Auth Token

1. **Go to your Sentry project dashboard**
2. **Settings → Auth Tokens**
3. **Create New Token**
4. **Select permissions:**
   - `project:read`
   - `org:read`
   - `event:read`
5. **Copy the token and add it to your .env file**

## 🚀 Test the Setup

After adding the credentials:

1. **Restart your server**
2. **Run the test:**
   ```bash
   python test_automated_debugging.py
   ```
3. **Check the automated debugger:**
   ```bash
   curl http://localhost:8001/automated-debugger/status
   ```

## 🎯 What This Enables

With these credentials, your system will:
- ✅ **Fetch real errors** from your Sentry project
- ✅ **Automatically detect** new issues
- ✅ **Trigger Fix-AI** to resolve problems
- ✅ **Provide real-time** error analysis
- ✅ **Enable continuous** self-healing

## 🔧 API Endpoints

Once configured, you can:

- **Start automated debugging:** `POST /automated-debugger/start`
- **Check status:** `GET /automated-debugger/status`
- **Stop debugging:** `POST /automated-debugger/stop`
- **Test Sentry:** `GET /sentry-test`
- **Trigger error:** `GET /sentry-debug`

## 📊 Expected Results

After setup, you should see:
- No more "simulated data" warnings
- Real error data from your Sentry project
- Automated Fix-AI triggering for actual issues
- Real-time error pattern recognition 