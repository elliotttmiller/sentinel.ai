# Sentinel Mobile App

A React Native mobile application for the Sentinel AI Agent Command Center, built with Expo.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Expo CLI (`npm install -g @expo/cli`)
- Expo Go app on your mobile device (for testing)

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   Copy `env.example` to `.env` and update with your configuration:
   ```bash
   cp env.example .env
   ```

3. **Update your configuration:**
   Edit `.env` with your actual URLs:
   ```
   EXPO_PUBLIC_RAILWAY_API_URL=https://your-railway-app.railway.app
   EXPO_PUBLIC_NGROK_API_URL=https://your-ngrok-subdomain.ngrok.io
   EXPO_PUBLIC_WEBSOCKET_URL=wss://your-railway-app.railway.app/ws
   ```

### Running the App

1. **Start the development server:**
   ```bash
   npx expo start
   ```

2. **Run on device:**
   - Install Expo Go on your mobile device
   - Scan the QR code displayed in the terminal
   - The app will load on your device

3. **Run on simulator/emulator:**
   ```bash
   # For iOS Simulator
   npx expo start --ios
   
   # For Android Emulator
   npx expo start --android
   ```

## 🔧 Configuration

### Railway Backend Setup

1. Deploy your backend to Railway
2. Get your Railway app URL (e.g., `https://sentinel-backend.railway.app`)
3. Update `EXPO_PUBLIC_RAILWAY_API_URL` in your `.env` file

### ngrok Tunnel Setup

1. Install ngrok: `npm install -g ngrok`
2. Authenticate: `ngrok config add-authtoken YOUR_TOKEN`
3. Start tunnel to your local backend:
   ```bash
   ngrok http 8080
   ```
4. Copy the ngrok URL and update `EXPO_PUBLIC_NGROK_API_URL`

### Connection Management

The app automatically manages connections between Railway and ngrok:

- **Railway**: Production backend deployment
- **ngrok**: Local development tunnel
- **Auto-switching**: App tries Railway first, falls back to ngrok if needed
- **Manual switching**: Use Settings screen to manually switch connections

## 📱 Features

### Home Screen
- Connection status indicator
- Recent missions overview
- Available agents status
- Quick system health check

### Missions
- Create new AI agent missions
- View mission execution plans
- Monitor mission progress
- Execute missions remotely

### Agents
- View available AI agents
- Check agent capabilities
- Monitor agent status

### Settings
- Connection configuration
- URL management
- Connection testing
- App information

## 🏗️ Architecture

```
Mobile App (React Native/Expo)
    ↓
API Context (Connection Management)
    ↓
API Service (HTTP Client)
    ↓
Railway Backend OR ngrok Tunnel
    ↓
Local Desktop Agent Engine
```

### Key Components

- **ApiContext**: Manages Railway/ngrok connections
- **ApiService**: HTTP client for backend communication
- **Navigation**: Tab-based navigation with stack screens
- **Theme**: Material Design 3 theming with React Native Paper

## 🔌 API Integration

The app communicates with your backend through these endpoints:

- `GET /health` - Health check
- `GET /missions` - List missions
- `POST /missions` - Create mission
- `GET /missions/{id}` - Get mission details
- `POST /missions/{id}/execute` - Execute mission
- `GET /agents` - List available agents

## 🎨 UI/UX Features

- **Material Design 3**: Modern, accessible design
- **Dark/Light Theme**: Automatic theme switching
- **Responsive Layout**: Works on phones and tablets
- **Pull-to-Refresh**: Real-time data updates
- **Loading States**: Smooth loading indicators
- **Error Handling**: User-friendly error messages

## 🛠️ Development

### Project Structure

```
src/
├── components/          # Reusable UI components
├── contexts/           # React contexts (API, theme)
├── navigation/         # Navigation configuration
├── screens/           # App screens
├── services/          # API and external services
├── types/             # TypeScript type definitions
└── utils/             # Utility functions and theme
```

### Adding New Features

1. **New Screen**: Add to `src/screens/` and update navigation
2. **New API Endpoint**: Add to `src/services/api.ts`
3. **New Type**: Add to `src/types/index.ts`
4. **New Component**: Add to `src/components/`

### Testing

```bash
# Run tests
npm test

# Run linting
npm run lint
```

## 📦 Building for Production

### EAS Build (Recommended)

1. **Install EAS CLI:**
   ```bash
   npm install -g @expo/eas-cli
   ```

2. **Configure EAS:**
   ```bash
   eas build:configure
   ```

3. **Build for platforms:**
   ```bash
   # iOS
   eas build --platform ios
   
   # Android
   eas build --platform android
   ```

### Manual Build

```bash
# Generate native code
npx expo prebuild

# Build for iOS
npx expo run:ios

# Build for Android
npx expo run:android
```

## 🔒 Security Considerations

- Environment variables are prefixed with `EXPO_PUBLIC_` for client-side access
- API keys and secrets should be handled server-side
- Use HTTPS for all production connections
- Implement proper authentication for production use

## 🐛 Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check your Railway/ngrok URLs
   - Verify backend is running
   - Test connection in Settings screen

2. **Expo Go Issues**
   - Update Expo Go to latest version
   - Clear app cache
   - Restart development server

3. **Build Errors**
   - Clear node_modules and reinstall
   - Update Expo SDK version
   - Check TypeScript errors

### Debug Mode

Enable debug logging by setting:
```
EXPO_PUBLIC_DEBUG=true
```

## 📚 Resources

- [Expo Documentation](https://docs.expo.dev/)
- [React Native Paper](https://callstack.github.io/react-native-paper/)
- [React Navigation](https://reactnavigation.org/)
- [Railway Documentation](https://docs.railway.app/)
- [ngrok Documentation](https://ngrok.com/docs)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

**Sentinel Mobile App** - Your AI agent command center in your pocket! 🤖📱 