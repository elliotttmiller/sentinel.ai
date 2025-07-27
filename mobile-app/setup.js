#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const question = (query) => new Promise((resolve) => rl.question(query, resolve));

async function setup() {
  console.log('🚀 Sentinel Mobile App Setup\n');
  console.log('This script will help you configure your Railway and ngrok URLs.\n');

  // Check if .env already exists
  const envPath = path.join(__dirname, '.env');
  const envExists = fs.existsSync(envPath);

  if (envExists) {
    const overwrite = await question('A .env file already exists. Overwrite? (y/N): ');
    if (overwrite.toLowerCase() !== 'y') {
      console.log('Setup cancelled.');
      rl.close();
      return;
    }
  }

  console.log('\n📋 Configuration Setup\n');

  // Railway URL
  const railwayUrl = await question('Enter your Railway backend URL (e.g., https://sentinel-backend.railway.app): ');
  
  // ngrok URL
  const ngrokUrl = await question('Enter your ngrok tunnel URL (e.g., https://abc123.ngrok.io): ');
  
  // WebSocket URL
  const wsUrl = await question('Enter your WebSocket URL (e.g., wss://sentinel-backend.railway.app/ws): ');

  // App settings
  const appName = await question('App name (default: Sentinel): ') || 'Sentinel';
  const appVersion = await question('App version (default: 1.0.0): ') || '1.0.0';

  // Feature flags
  const enableNotifications = await question('Enable notifications? (Y/n): ') !== 'n';
  const enableAnalytics = await question('Enable analytics? (y/N): ') === 'y';
  const debug = await question('Enable debug mode? (y/N): ') === 'y';

  // Generate .env content
  const envContent = `# Railway Backend Configuration
EXPO_PUBLIC_RAILWAY_API_URL=${railwayUrl}

# ngrok Tunnel Configuration (for local development)
EXPO_PUBLIC_NGROK_API_URL=${ngrokUrl}

# WebSocket Configuration
EXPO_PUBLIC_WEBSOCKET_URL=${wsUrl}

# App Configuration
EXPO_PUBLIC_APP_NAME=${appName}
EXPO_PUBLIC_APP_VERSION=${appVersion}

# Feature Flags
EXPO_PUBLIC_ENABLE_NOTIFICATIONS=${enableNotifications}
EXPO_PUBLIC_ENABLE_ANALYTICS=${enableAnalytics}
EXPO_PUBLIC_DEBUG=${debug}
`;

  // Write .env file
  try {
    fs.writeFileSync(envPath, envContent);
    console.log('\n✅ Configuration saved to .env file!\n');
  } catch (error) {
    console.error('❌ Error saving .env file:', error.message);
    rl.close();
    return;
  }

  // Display next steps
  console.log('📱 Next Steps:\n');
  console.log('1. Start your backend services:');
  console.log('   - Railway backend should be deployed');
  console.log('   - ngrok tunnel should be running (if using)');
  console.log('   - Local agent engine should be running\n');
  
  console.log('2. Start the mobile app:');
  console.log('   npm start\n');
  
  console.log('3. Test the connection:');
  console.log('   - Open the app on your device');
  console.log('   - Check the connection status on the Home screen');
  console.log('   - Use the Settings screen to test connections\n');

  console.log('🔧 Configuration Summary:');
  console.log(`   Railway URL: ${railwayUrl}`);
  console.log(`   ngrok URL: ${ngrokUrl}`);
  console.log(`   WebSocket URL: ${wsUrl}`);
  console.log(`   App Name: ${appName}`);
  console.log(`   Notifications: ${enableNotifications ? 'Enabled' : 'Disabled'}`);
  console.log(`   Analytics: ${enableAnalytics ? 'Enabled' : 'Disabled'}`);
  console.log(`   Debug Mode: ${debug ? 'Enabled' : 'Disabled'}\n`);

  console.log('🎉 Setup complete! You can now run "npm start" to launch the app.');

  rl.close();
}

setup().catch(console.error); 