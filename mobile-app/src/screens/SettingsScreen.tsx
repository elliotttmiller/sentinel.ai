import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Text, Card, Button, Switch, useTheme, TextInput, Divider, List, IconButton, Chip } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons as Icon } from '@expo/vector-icons';

import { useApi } from '@/contexts/ApiContext';
import ApiService from '@/services/api';

const SettingsScreen: React.FC = () => {
  const theme = useTheme();
  const api = useApi();
  const baseUrl = api?.baseUrl ?? '';
  const isConnected = api?.isConnected ?? false;
  const connectionError = api?.connectionError ?? null;
  
  const [railwayInput, setRailwayInput] = useState(api?.railwayUrl ?? '');
  const [ngrokInput, setNgrokInput] = useState(api?.ngrokUrl ?? '');
  const [websocketInput, setWebsocketInput] = useState(api?.websocketUrl ?? '');
  const [isEditing, setIsEditing] = useState(false);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [analyticsEnabled, setAnalyticsEnabled] = useState(false);
  const [debugMode, setDebugMode] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [darkMode, setDarkMode] = useState(false);

  const apiService = new ApiService(baseUrl);

  const testConnection = async (url: string) => {
    try {
      const testService = new ApiService(url);
      await testService.healthCheck();
      Alert.alert('Success', 'Connection test successful!');
    } catch (error) {
      Alert.alert('Error', 'Connection test failed. Please check the URL and try again.');
    }
  };

  const saveSettings = () => {
    // In a real app, you would save these to AsyncStorage or your state management
    Alert.alert('Success', 'Settings saved successfully!');
    setIsEditing(false);
  };

  const resetSettings = () => {
    Alert.alert(
      'Reset Settings',
      'Are you sure you want to reset all settings to default?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Reset', 
          style: 'destructive',
          onPress: () => {
            setRailwayInput(api?.railwayUrl ?? '');
            setNgrokInput(api?.ngrokUrl ?? '');
            setWebsocketInput(api?.websocketUrl ?? '');
            setNotificationsEnabled(true);
            setAnalyticsEnabled(false);
            setDebugMode(false);
            setAutoRefresh(true);
            setDarkMode(false);
            Alert.alert('Success', 'Settings reset to default!');
          }
        }
      ]
    );
  };

  const getConnectionStatusCard = () => (
    <Card style={styles.card}>
      <Card.Title title="Connection Status" left={(props) => <Icon {...props} name="wifi" />} />
      <Card.Content>
        <View style={styles.connectionStatus}>
          <View style={styles.statusRow}>
            <Icon 
              name={isConnected ? 'check-circle' : 'close-circle'} 
              size={24} 
              color={isConnected ? theme.colors.primary : theme.colors.error} 
            />
            <Text variant="bodyMedium" style={{ marginLeft: 8, flex: 1 }}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </Text>
            <Chip 
              mode="outlined" 
              textStyle={{ color: isConnected ? theme.colors.primary : theme.colors.error }}
              style={{ borderColor: isConnected ? theme.colors.primary : theme.colors.error }}
            >
              {baseUrl.includes('ngrok') ? 'ngrok' : 'Railway'}
            </Chip>
          </View>
          
          {connectionError && (
            <Text variant="bodySmall" style={{ color: theme.colors.error, marginTop: 8 }}>
              Error: {connectionError}
            </Text>
          )}
          
          <View style={styles.connectionActions}>
            <Button 
              mode="outlined" 
              onPress={() => testConnection(baseUrl)}
              style={styles.actionButton}
            >
              Test Connection
            </Button>
            <Button 
              mode="outlined" 
              onPress={() => {}}
              style={styles.actionButton}
            >
              Switch to Railway
            </Button>
            <Button 
              mode="outlined" 
              onPress={() => {}}
              style={styles.actionButton}
            >
              Switch to ngrok
            </Button>
          </View>
        </View>
      </Card.Content>
    </Card>
  );

  const getUrlSettingsCard = () => (
    <Card style={styles.card}>
      <Card.Title 
        title="URL Configuration" 
        left={(props) => <Icon {...props} name="link" />}
        right={(props) => (
          <IconButton
            {...props}
            icon={isEditing ? 'check' : 'pencil'}
            onPress={() => isEditing ? saveSettings() : setIsEditing(true)}
          />
        )}
      />
      <Card.Content>
        <View style={styles.urlInput}>
          <Text variant="bodySmall" style={{ marginBottom: 4 }}>Railway API URL:</Text>
          <TextInput
            mode="outlined"
            value={railwayInput}
            onChangeText={setRailwayInput}
            disabled={!isEditing}
            placeholder="https://your-app.railway.app"
            style={styles.input}
          />
        </View>
        
        <View style={styles.urlInput}>
          <Text variant="bodySmall" style={{ marginBottom: 4 }}>ngrok API URL:</Text>
          <TextInput
            mode="outlined"
            value={ngrokInput}
            onChangeText={setNgrokInput}
            disabled={!isEditing}
            placeholder="https://your-tunnel.ngrok.io"
            style={styles.input}
          />
        </View>
        
        <View style={styles.urlInput}>
          <Text variant="bodySmall" style={{ marginBottom: 4 }}>WebSocket URL:</Text>
          <TextInput
            mode="outlined"
            value={websocketInput}
            onChangeText={setWebsocketInput}
            disabled={!isEditing}
            placeholder="wss://your-websocket-url"
            style={styles.input}
          />
        </View>
      </Card.Content>
    </Card>
  );

  const getAppSettingsCard = () => (
    <Card style={styles.card}>
      <Card.Title title="App Settings" left={(props) => <Icon {...props} name="cog" />} />
      <Card.Content>
        <List.Item
          title="Push Notifications"
          description="Receive notifications for mission updates"
          left={(props) => <List.Icon {...props} icon="bell" />}
          right={() => (
            <Switch
              value={notificationsEnabled}
              onValueChange={setNotificationsEnabled}
            />
          )}
        />
        <Divider />
        <List.Item
          title="Analytics"
          description="Send anonymous usage data"
          left={(props) => <List.Icon {...props} icon="chart-line" />}
          right={() => (
            <Switch
              value={analyticsEnabled}
              onValueChange={setAnalyticsEnabled}
            />
          )}
        />
        <Divider />
        <List.Item
          title="Debug Mode"
          description="Show detailed logs and debug information"
          left={(props) => <List.Icon {...props} icon="bug" />}
          right={() => (
            <Switch
              value={debugMode}
              onValueChange={setDebugMode}
            />
          )}
        />
        <Divider />
        <List.Item
          title="Auto Refresh"
          description="Automatically refresh data every 30 seconds"
          left={(props) => <List.Icon {...props} icon="refresh" />}
          right={() => (
            <Switch
              value={autoRefresh}
              onValueChange={setAutoRefresh}
            />
          )}
        />
        <Divider />
        <List.Item
          title="Dark Mode"
          description="Use dark theme (requires app restart)"
          left={(props) => <List.Icon {...props} icon="theme-light-dark" />}
          right={() => (
            <Switch
              value={darkMode}
              onValueChange={setDarkMode}
            />
          )}
        />
      </Card.Content>
    </Card>
  );

  const getAppInfoCard = () => (
    <Card style={styles.card}>
      <Card.Title title="App Information" left={(props) => <Icon {...props} name="information" />} />
      <Card.Content>
        <View style={styles.infoRow}>
          <Text variant="bodyMedium">App Name:</Text>
          <Text variant="bodyMedium" style={{ fontWeight: 'bold' }}>Sentinel Mobile</Text>
        </View>
        <View style={styles.infoRow}>
          <Text variant="bodyMedium">Version:</Text>
          <Text variant="bodyMedium" style={{ fontWeight: 'bold' }}>1.0.0</Text>
        </View>
        <View style={styles.infoRow}>
          <Text variant="bodyMedium">Build:</Text>
          <Text variant="bodyMedium" style={{ fontWeight: 'bold' }}>2024.1.0</Text>
        </View>
        <View style={styles.infoRow}>
          <Text variant="bodyMedium">SDK:</Text>
          <Text variant="bodyMedium" style={{ fontWeight: 'bold' }}>Expo SDK 53</Text>
        </View>
        <View style={styles.infoRow}>
          <Text variant="bodyMedium">React Native:</Text>
          <Text variant="bodyMedium" style={{ fontWeight: 'bold' }}>0.79.5</Text>
        </View>
      </Card.Content>
    </Card>
  );

  const getActionButtons = () => (
    <View style={styles.actionButtons}>
      <Button 
        mode="outlined" 
        onPress={resetSettings}
        style={styles.actionButton}
        textColor={theme.colors.error}
      >
        Reset Settings
      </Button>
      <Button 
        mode="outlined" 
        onPress={() => {}}
        style={styles.actionButton}
      >
        Export Logs
      </Button>
      <Button 
        mode="outlined" 
        onPress={() => {}}
        style={styles.actionButton}
      >
        Clear Cache
      </Button>
    </View>
  );

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <ScrollView style={styles.scrollView}>
        <Text variant="headlineMedium" style={styles.title}>
          Settings
        </Text>

        {getConnectionStatusCard()}
        {getUrlSettingsCard()}
        {getAppSettingsCard()}
        {getAppInfoCard()}
        {getActionButtons()}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
    padding: 16,
  },
  title: {
    marginBottom: 24,
    textAlign: 'center',
  },
  card: {
    marginBottom: 16,
  },
  connectionStatus: {
    gap: 16,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  connectionActions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  actionButton: {
    flex: 1,
    minWidth: 100,
  },
  urlInput: {
    marginBottom: 16,
  },
  input: {
    backgroundColor: 'transparent',
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 4,
  },
  actionButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginTop: 16,
  },
});

export default SettingsScreen; 