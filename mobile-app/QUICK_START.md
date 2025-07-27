# 🚀 Quick Start Guide - Sentinel Mobile App

This guide will help you run your Sentinel mobile app using your Railway backend and ngrok tunnel configuration.

## 📋 Prerequisites

1. **Node.js 18+** installed
2. **Expo Go** app installed on your mobile device
3. **Railway backend** deployed and running
4. **ngrok** installed and configured (for local development)
5. **Local agent engine** running (optional, for full functionality)

## 🔧 Step 1: Configure Your Environment

Run the setup script to configure your Railway and ngrok URLs:

```bash
npm run setup
```

This will prompt you for:
- **Railway URL**: Your deployed backend URL (e.g., `https://sentinel-backend.railway.app`)
- **ngrok URL**: Your ngrok tunnel URL (e.g., `https://abc123.ngrok.io`)
- **WebSocket URL**: Your WebSocket endpoint (e.g., `wss://sentinel-backend.railway.app/ws`)

## 🌐 Step 2: Start Your Backend Services

### Option A: Railway Backend (Production)
Your Railway backend should already be deployed and running. Verify it's accessible at your Railway URL.

### Option B: ngrok Tunnel (Local Development)
If you want to test with your local backend:

1. **Start your local backend:**
   ```bash
   cd ../backend
   python -m venv venv
   venv\Scripts\activate  # On Windows
   pip install -r requirements.txt
   uvicorn main:app --host 0.0.0.0 --port 8080
   ```

2. **Start ngrok tunnel:**
   ```bash
   ngrok http 8080
   ```

3. **Copy the ngrok URL** and update your `.env` file:
   ```
   EXPO_PUBLIC_NGROK_API_URL=https://your-ngrok-url.ngrok.io
   ```

## 📱 Step 3: Start the Mobile App

1. **Install dependencies** (if not already done):
   ```bash
   npm install
   ```

2. **Start the Expo development server:**
   ```bash
   npm start
   ```

3. **Run on your device:**
   - Open **Expo Go** on your mobile device
   - Scan the QR code displayed in the terminal
   - The app will load on your device

## 🔍 Step 4: Test the Connection

1. **Check Home Screen:**
   - Look for the connection status indicator
   - Should show "Connected to Railway" or "Connected to ngrok"

2. **Test in Settings:**
   - Go to Settings tab
   - Use "Test Connection" button
   - Should show "Connection test successful!"

3. **Create a Test Mission:**
   - Go to Missions tab
   - Tap the + button
   - Create a simple test mission
   - Verify it appears in the list

## 🔄 Connection Management

The app automatically manages connections:

- **Primary**: Tries Railway first
- **Fallback**: Switches to ngrok if Railway fails
- **Manual**: Use Settings screen to manually switch

### Switching Connections

1. **Settings Tab** → **Connection Settings**
2. Toggle "Use ngrok tunnel" on/off
3. Update URLs if needed
4. Test connection

## 🐛 Troubleshooting

### Connection Issues

**Problem**: "Connection Failed" on Home screen
**Solutions**:
- Check your Railway/ngrok URLs in `.env`
- Verify backend is running
- Test connection in Settings screen
- Check network connectivity

**Problem**: "Failed to load missions"
**Solutions**:
- Verify backend API endpoints are working
- Check backend logs for errors
- Ensure proper CORS configuration

### Expo Issues

**Problem**: QR code not working
**Solutions**:
- Make sure device and computer are on same network
- Try "Tunnel" connection type in Expo
- Restart Expo development server

**Problem**: App crashes on startup
**Solutions**:
- Clear Expo Go cache
- Restart development server
- Check for TypeScript errors

### Backend Issues

**Problem**: Railway backend not responding
**Solutions**:
- Check Railway dashboard for deployment status
- Verify environment variables are set
- Check Railway logs for errors

**Problem**: ngrok tunnel not working
**Solutions**:
- Verify ngrok is authenticated: `ngrok config add-authtoken YOUR_TOKEN`
- Check if port 8080 is correct
- Ensure local backend is running

## 📊 Monitoring

### App Logs
- Check Expo development server console
- Use `console.log()` in your code
- Enable debug mode in `.env`: `EXPO_PUBLIC_DEBUG=true`

### Backend Logs
- Railway: Check deployment logs in Railway dashboard
- Local: Check terminal where backend is running
- ngrok: Check ngrok web interface at `http://localhost:4040`

## 🎯 Next Steps

Once your app is running successfully:

1. **Create your first mission** using the mobile app
2. **Monitor mission execution** in real-time
3. **Test different agent capabilities**
4. **Customize the UI** to match your preferences
5. **Deploy to app stores** using EAS Build

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the main README.md for detailed documentation
3. Check your backend logs for API errors
4. Verify all URLs and configurations are correct

---

**🎉 Congratulations!** Your Sentinel mobile app is now running with Railway and ngrok! 

You can now control your AI agents from your mobile device and monitor mission execution in real-time. 