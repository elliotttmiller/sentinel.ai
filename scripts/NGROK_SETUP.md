# ngrok Setup Guide for Sentinel

This guide explains how to set up ngrok tunnels for local development with the Sentinel service manager.

## 🎯 What This Solves

✅ **Single ngrok Session**: Uses `ngrok start --all` with a config file  
✅ **Multiple Tunnels**: Both backend (8080) and engine (8001) tunnels in one session  
✅ **No Session Limit**: Avoids the "limited to 1 simultaneous agent sessions" error  

## 📋 Prerequisites

1. **ngrok Account**: Sign up at https://ngrok.com/
2. **Auth Token**: Get from https://dashboard.ngrok.com/get-started/your-authtoken
3. **ngrok CLI**: Install ngrok on your system

## 🚀 Quick Setup

### Step 1: Setup ngrok Auth Token

Run the setup script:
```bash
python scripts/setup_ngrok.py
```

The script will:
1. ✅ Check if ngrok CLI is installed
2. ✅ Validate your existing token (if any)
3. ✅ Automatically refresh expired tokens
4. ✅ Save the token to configuration
5. ✅ Test the token with ngrok API

### Step 2: Test the Setup (Optional)

Run the test script to verify everything works:
```bash
python scripts/test_ngrok_setup.py
```

### Step 3: Start Services

Use the service manager:
```bash
python scripts/manage_services.py
```

Choose option **2** to start both ngrok tunnels at once.

## 🔧 How It Works

The service manager creates a `ngrok.yml` configuration file:

```yaml
version: "2"
authtoken: YOUR_AUTH_TOKEN_HERE
tunnels:
  backend:
    addr: 8080
    proto: http
    subdomain: your-subdomain (optional)
  engine:
    addr: 8001
    proto: http
```

Then starts both tunnels with:
```bash
ngrok start --all --config ngrok.yml
```

## 📱 Mobile App Configuration

Once the tunnels are running, update your mobile app's `.env` file with the ngrok URLs:

```env
EXPO_PUBLIC_API_URL=https://your-backend-tunnel.ngrok.io
EXPO_PUBLIC_WEBSOCKET_URL=wss://your-engine-tunnel.ngrok.io
```

## 🛠️ Service Manager Options

- **Option 1**: Start Backend Server only
- **Option 2**: Start ngrok Tunnels (Backend + Engine) ⭐ **Recommended**
- **Option 3**: Start Agent Engine only
- **Option 4**: Start All Services
- **Option 11**: Setup ngrok Auth Token

## 🔍 Troubleshooting

### "Auth token not configured"
Run the setup script again:
```bash
python scripts/setup_ngrok.py
```

### "Token is invalid or expired"
The setup script will automatically detect this and prompt you to refresh your token.

### "ngrok CLI not found"
Install ngrok from https://ngrok.com/download and make sure it's in your PATH.

### "Limited to 1 simultaneous agent sessions"
This error occurs when trying to run multiple ngrok instances. The service manager solves this by using a single session with multiple tunnels.

### Tunnel URLs not working
1. Check that both services (backend and engine) are running
2. Verify the ngrok tunnels are active
3. Update mobile app URLs with the correct ngrok URLs

### Test Your Setup
Run the test script to diagnose issues:
```bash
python scripts/test_ngrok_setup.py
```

## 📝 Configuration Files

- **Service Config**: `scripts/service_config.json`
- **ngrok Config**: `ngrok.yml` (auto-generated)
- **Environment**: `NGROK_AUTHTOKEN` environment variable

## 🎉 Success!

Once everything is set up, you should see:
- ✅ Backend server running on port 8080
- ✅ Engine server running on port 8001
- ✅ ngrok tunnels providing public URLs
- ✅ Mobile app able to connect to both services

Your Sentinel system is now ready for local development with mobile access! 🚀 