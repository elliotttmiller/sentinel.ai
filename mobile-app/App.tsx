import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { Provider as PaperProvider } from 'react-native-paper';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { theme } from '@/utils/theme';
import { ApiProvider } from '@/contexts/ApiContext';
import HomeScreen from '@/screens/HomeScreen';

export default function App() {
  return (
    <SafeAreaProvider>
      <PaperProvider theme={theme}>
        <ApiProvider>
          <HomeScreen />
          <StatusBar style="auto" />
        </ApiProvider>
      </PaperProvider>
    </SafeAreaProvider>
  );
} 