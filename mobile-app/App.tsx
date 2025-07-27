import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { Provider as PaperProvider } from 'react-native-paper';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { theme } from '@/utils/theme';
import { ApiProvider } from '@/contexts/ApiContext';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import AppNavigator from '@/navigation/AppNavigator';
import CreateMissionScreen from '@/screens/CreateMissionScreen';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <SafeAreaProvider>
      <PaperProvider theme={theme}>
        <ApiProvider>
          <NavigationContainer>
            <Stack.Navigator>
              <Stack.Screen name="Root" component={AppNavigator} options={{ headerShown: false }} />
              <Stack.Screen name="CreateMission" component={CreateMissionScreen} options={{ title: 'Create Mission' }} />
            </Stack.Navigator>
          </NavigationContainer>
          <StatusBar style="auto" />
        </ApiProvider>
      </PaperProvider>
    </SafeAreaProvider>
  );
} 