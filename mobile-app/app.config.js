import 'dotenv/config';

export default {
  expo: {
    name: "Sentinel",
    slug: "sentinel-mobile",
    version: "1.0.0",
    orientation: "portrait",
    icon: "./assets/icon.png",
    userInterfaceStyle: "light",
    splash: {
      image: "./assets/splash.png",
      resizeMode: "contain",
      backgroundColor: "#ffffff"
    },
    assetBundlePatterns: [
      "**/*"
    ],
    ios: {
      supportsTablet: true,
      bundleIdentifier: "com.sentinel.mobile"
    },
    android: {
      adaptiveIcon: {
        foregroundImage: "./assets/adaptive-icon.png",
        backgroundColor: "#ffffff"
      },
      package: "com.sentinel.mobile"
    },
    web: {
      favicon: "./assets/favicon.png",
      bundler: "metro"
    },
    plugins: [
      "expo-router",
      "expo-notifications"
    ],
    scheme: "sentinel",
    extra: {
      // Railway configuration
      railwayUrl: process.env.EXPO_PUBLIC_RAILWAY_API_URL || "https://your-railway-app.railway.app",
      
      // ngrok configuration
      ngrokUrl: process.env.EXPO_PUBLIC_NGROK_API_URL || "https://your-ngrok-subdomain.ngrok.io",
      
      // WebSocket configuration
      websocketUrl: process.env.EXPO_PUBLIC_WEBSOCKET_URL || "wss://your-railway-app.railway.app/ws",
      
      // App configuration
      appName: process.env.EXPO_PUBLIC_APP_NAME || "Sentinel",
      appVersion: process.env.EXPO_PUBLIC_APP_VERSION || "1.0.0",
      
      // Feature flags
      enableNotifications: process.env.EXPO_PUBLIC_ENABLE_NOTIFICATIONS === "true",
      enableAnalytics: process.env.EXPO_PUBLIC_ENABLE_ANALYTICS === "true",
      
      // Debug mode
      debug: process.env.EXPO_PUBLIC_DEBUG === "true",
      
      eas: {
        projectId: process.env.EXPO_PUBLIC_EAS_PROJECT_ID || "your-project-id-here"
      }
    }
  }
}; 