import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Text, Card, Switch, Button, TextInput, useTheme, Divider } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons as Icon } from '@expo/vector-icons';

import { useApi } from '@/contexts/ApiContext';

const SettingsScreen: React.FC = () => {
  const theme = useTheme();
  const { 
    config, 
    baseUrl, 
    isConnected, 
    connectionError, 
    switchToNgrok, 
    switchToRailway 
  } = useApi();
  
  const [railwayUrl, setRailwayUrl] = useState(config.railwayUrl);
  const [ngrokUrl, setNgrokUrl] = useState(config.ngrokUrl);
  const [useNgrok, setUseNgrok] = useState(config.useNgrok);

  const handleConnectionSwitch = (useNgrokConnection: boolean) => {
    setUseNgrok(useNgrokConnection);
    if (useNgrokConnection) {
      switchToNgrok();
    } else {
      switchToRailway();
    }
  };

  const handleTestConnection = async () => {
    const testUrl = useNgrok ? ngrokUrl : railwayUrl;
    try {
      const response = await fetch(`${testUrl}/health`, {
        method: 'GET',
        timeout: 5000,
      });
      
      if (response.ok) {
        Alert.alert('Success', 'Connection test successful!');
      } else {
        Alert.alert('Error', 'Connection test failed. Server returned an error.');
      }
    } catch (error) {
      Alert.alert('Error', 'Connection test failed. Please check your URL and try again.');
    }
  };

  const getConnectionStatus = () => {
    if (isConnected) {
      return (
        <View style={styles.statusContainer}>
          <Icon name="wifi" size={24} color={theme.colors.primary} />
          <Text variant="titleMedium" style={{ color: theme.colors.primary, marginLeft: 8 }}>
            Connected
          </Text>
        </View>
      );
    }

    return (
      <View style={styles.statusContainer}>
        <Icon name="wifi-off" size={24} color={theme.colors.error} />
        <Text variant="titleMedium" style={{ color: theme.colors.error, marginLeft: 8 }}>
          Disconnected
        </Text>
      </View>
    );
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <ScrollView style={styles.scrollView}>
        <Card style={styles.card}>
          <Card.Title title="Connection Status" />
          <Card.Content>
            {getConnectionStatus()}
            {connectionError && (
              <Text variant="bodySmall" style={{ color: theme.colors.error, marginTop: 8 }}>
                {connectionError}
              </Text>
            )}
            <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant, marginTop: 8 }}>
              Current URL: {baseUrl}
            </Text>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Title title="Connection Settings" />
          <Card.Content>
            <View style={styles.settingRow}>
              <Text variant="bodyMedium">Use ngrok tunnel</Text>
              <Switch
                value={useNgrok}
                onValueChange={handleConnectionSwitch}
                color={theme.colors.primary}
              />
            </View>
            
            <Divider style={styles.divider} />
            
            <Text variant="titleSmall" style={styles.sectionTitle}>
              Railway Backend URL
            </Text>
            <TextInput
              label="Railway URL"
              value={railwayUrl}
              onChangeText={setRailwayUrl}
              mode="outlined"
              style={styles.input}
              placeholder="https://your-app.railway.app"
            />
            
            <Text variant="titleSmall" style={styles.sectionTitle}>
              ngrok Tunnel URL
            </Text>
            <TextInput
              label="ngrok URL"
              value={ngrokUrl}
              onChangeText={setNgrokUrl}
              mode="outlined"
              style={styles.input}
              placeholder="https://your-subdomain.ngrok.io"
            />
            
            <Button
              mode="outlined"
              onPress={handleTestConnection}
              style={styles.testButton}
            >
              Test Connection
            </Button>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Title title="App Information" />
          <Card.Content>
            <View style={styles.infoRow}>
              <Text variant="bodyMedium">App Name</Text>
              <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant }}>
                Sentinel
              </Text>
            </View>
            <View style={styles.infoRow}>
              <Text variant="bodyMedium">Version</Text>
              <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant }}>
                1.0.0
              </Text>
            </View>
            <View style={styles.infoRow}>
              <Text variant="bodyMedium">Platform</Text>
              <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant }}>
                React Native / Expo
              </Text>
            </View>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Title title="About" />
          <Card.Content>
            <Text variant="bodyMedium" style={styles.aboutText}>
              Sentinel is your personal AI agent command center. Create missions and let AI agents 
              execute complex tasks on your local desktop through secure cloud orchestration.
            </Text>
            <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant, marginTop: 16 }}>
              Built with React Native, Expo, and powered by AI agents running on your desktop.
            </Text>
          </Card.Content>
        </Card>
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
  card: {
    marginBottom: 16,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  divider: {
    marginVertical: 16,
  },
  sectionTitle: {
    marginBottom: 8,
  },
  input: {
    marginBottom: 16,
  },
  testButton: {
    marginTop: 8,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  aboutText: {
    lineHeight: 24,
  },
});

export default SettingsScreen; 