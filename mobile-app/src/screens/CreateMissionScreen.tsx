import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Text, TextInput, Button, Card, useTheme, HelperText } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';

import { useApi } from '@/contexts/ApiContext';
import { NavigationProps } from '@/types';
import ApiService from '@/services/api';

const CreateMissionScreen: React.FC<NavigationProps> = ({ navigation }) => {
  const theme = useTheme();
  const { baseUrl, isConnected } = useApi();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const apiService = new ApiService(baseUrl);

  const debugLog = (message: string, data?: any) => {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] CREATE_MISSION_SCREEN: ${message}`, data ? JSON.stringify(data, null, 2) : '');
  };

  const handleCreateMission = async () => {
    debugLog('Create button pressed', { title, description, isConnected, baseUrl });
    if (!title.trim() || !description.trim()) {
      setError('Please fill in all fields');
      debugLog('Validation failed: missing fields', { title, description });
      Alert.alert('Validation Error', 'Please fill in all fields');
      return;
    }

    if (!isConnected) {
      setError('Not connected to backend');
      debugLog('Validation failed: not connected to backend', { isConnected, baseUrl });
      Alert.alert('Connection Error', 'Not connected to backend');
      return;
    }

    try {
      setLoading(true);
      setError('');
      debugLog('Attempting to create mission', { title: title.trim(), description: description.trim() });
      const result = await apiService.createMission(title.trim(), description.trim());
      debugLog('Mission created successfully', result);
      Alert.alert('Success', 'Mission created successfully!', [
        { text: 'OK', onPress: () => { debugLog('Navigating back after success'); navigation.goBack(); } }
      ]);
    } catch (error: any) {
      console.error('Failed to create mission:', error);
      setError('Failed to create mission. Please try again.');
      debugLog('Mission creation failed', { error: error?.message || error });
      Alert.alert('Error', 'Failed to create mission. Please try again.');
    } finally {
      setLoading(false);
      debugLog('Mission creation flow ended', { loading: false });
    }
  };

  // Add debug logging for input changes
  const handleTitleChange = (text: string) => {
    debugLog('Title input changed', { text });
    setTitle(text);
  };
  const handleDescriptionChange = (text: string) => {
    debugLog('Description input changed', { text });
    setDescription(text);
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <ScrollView style={styles.scrollView}>
        <Card style={styles.card}>
          <Card.Content>
            <Text variant="headlineSmall" style={styles.title}>
              Create New Mission
            </Text>
            
            <TextInput
              label="Mission Title"
              value={title}
              onChangeText={handleTitleChange}
              mode="outlined"
              style={styles.input}
              disabled={loading}
              maxLength={100}
            />
            
            <TextInput
              label="Mission Description"
              value={description}
              onChangeText={handleDescriptionChange}
              mode="outlined"
              multiline
              numberOfLines={4}
              style={styles.input}
              disabled={loading}
              maxLength={500}
            />
            
            <HelperText type="info" visible>
              Describe what you want the AI agents to accomplish
            </HelperText>

            {error ? (
              <HelperText type="error" visible>
                {error}
              </HelperText>
            ) : null}

            <View style={styles.buttonContainer}>
              <Button
                mode="outlined"
                onPress={() => { debugLog('Cancel button pressed'); navigation.goBack(); }}
                style={styles.button}
                disabled={loading}
              >
                Cancel
              </Button>
              <Button
                mode="contained"
                onPress={handleCreateMission}
                style={styles.button}
                loading={loading}
                disabled={loading || !title.trim() || !description.trim()}
              >
                Create Mission
              </Button>
            </View>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={styles.sectionTitle}>
              Mission Examples
            </Text>
            
            <View style={styles.exampleContainer}>
              <Text variant="bodyMedium" style={styles.exampleTitle}>
                Code Review
              </Text>
              <Text variant="bodySmall" style={styles.exampleDescription}>
                "Review the authentication system in the backend and suggest security improvements"
              </Text>
            </View>
            
            <View style={styles.exampleContainer}>
              <Text variant="bodyMedium" style={styles.exampleTitle}>
                Feature Development
              </Text>
              <Text variant="bodySmall" style={styles.exampleDescription}>
                "Add a new API endpoint for user profile management with proper validation"
              </Text>
            </View>
            
            <View style={styles.exampleContainer}>
              <Text variant="bodyMedium" style={styles.exampleTitle}>
                Bug Fix
              </Text>
              <Text variant="bodySmall" style={styles.exampleDescription}>
                "Investigate and fix the memory leak issue in the mobile app"
              </Text>
            </View>
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
  title: {
    marginBottom: 24,
    textAlign: 'center',
  },
  input: {
    marginBottom: 16,
  },
  buttonContainer: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 16,
  },
  button: {
    flex: 1,
  },
  sectionTitle: {
    marginBottom: 16,
  },
  exampleContainer: {
    marginBottom: 16,
    padding: 12,
    backgroundColor: 'rgba(0,0,0,0.05)',
    borderRadius: 8,
  },
  exampleTitle: {
    fontWeight: 'bold',
    marginBottom: 4,
  },
  exampleDescription: {
    fontStyle: 'italic',
  },
});

export default CreateMissionScreen; 