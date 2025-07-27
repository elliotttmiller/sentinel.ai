# 🎯 Getting Started - Sentinel Mobile App

Your Sentinel mobile app is now ready to run with your Railway backend and ngrok tunnel configuration!

## ✅ What's Been Set Up

- ✅ Complete React Native/Expo mobile app
- ✅ Railway backend integration
- ✅ ngrok tunnel support
- ✅ Automatic connection management
- ✅ Modern Material Design 3 UI
- ✅ Mission creation and monitoring
- ✅ Agent status tracking
- ✅ Settings and configuration management

## 🚀 Quick Start (3 Steps)

### 1. Configure Your URLs
```bash
npm run setup
```
Enter your Railway and ngrok URLs when prompted.

### 2. Start Your Backend
**Option A - Railway (Production):**
- Your Railway backend should already be running
- Verify it's accessible at your Railway URL

**Option B - ngrok (Local Development):**
```bash
# Start local backend
cd ../backend
uvicorn main:app --host 0.0.0.0 --port 8080

# In another terminal, start ngrok
ngrok http 8080
```

### 3. Launch the Mobile App
```bash
npm start
```
- Install Expo Go on your mobile device
- Scan the QR code
- The app will load on your device

## 📱 App Features

### Home Screen
- Real-time connection status
- Recent missions overview
- Available agents status
- Quick system health check

### Missions Tab
- Create new AI agent missions
- View mission execution plans
- Monitor mission progress
- Execute missions remotely

### Agents Tab
- View available AI agents
- Check agent capabilities
- Monitor agent status

### Settings Tab
- Connection configuration
- URL management
- Connection testing
- App information

## 🔧 Configuration Files

- **`.env`** - Your Railway and ngrok URLs
- **`app.config.js`** - Expo app configuration
- **`app.json`** - App metadata and settings

## 🔄 Connection Management

The app intelligently manages connections:

1. **Tries Railway first** (production)
2. **Falls back to ngrok** if Railway fails
3. **Manual switching** available in Settings
4. **Real-time status** indicators

## 🐛 Common Issues & Solutions

### "Connection Failed"
- Check URLs in `.env` file
- Verify backend is running
- Test connection in Settings

### "QR Code Not Working"
- Ensure device and computer on same network
- Try "Tunnel" connection in Expo
- Restart development server

### "App Crashes"
- Clear Expo Go cache
- Check for TypeScript errors
- Verify all dependencies installed

## 📊 Monitoring & Debugging

### App Logs
- Check Expo development server console
- Enable debug mode: `EXPO_PUBLIC_DEBUG=true`

### Backend Logs
- Railway: Check deployment logs
- Local: Check backend terminal
- ngrok: Visit `http://localhost:4040`

## 🎯 Next Steps

1. **Test the connection** using the Settings screen
2. **Create your first mission** from the mobile app
3. **Monitor mission execution** in real-time
4. **Customize the UI** to your preferences
5. **Deploy to app stores** using EAS Build

## 📚 Documentation

- **Main README**: `README.md` - Complete documentation
- **Quick Start**: `QUICK_START.md` - Step-by-step guide
- **Setup Script**: `setup.js` - Interactive configuration

## 🆘 Need Help?

1. Check the troubleshooting section in `QUICK_START.md`
2. Review backend logs for API errors
3. Verify all URLs and configurations
4. Test connections manually

---

**🎉 You're all set!** Your Sentinel mobile app is ready to control your AI agents from your mobile device.

Run `npm start` to launch your AI command center! 🤖📱 