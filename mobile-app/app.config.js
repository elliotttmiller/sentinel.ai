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
      "expo-notifications"
    ],
    scheme: "sentinel",
    extra: {
      // API configuration - this is the main URL the app uses
      apiUrl: process.env.EXPO_PUBLIC_API_URL || "https://sentinalai-production.up.railway.app",
      
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