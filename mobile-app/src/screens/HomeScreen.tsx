import React, { useEffect, useState } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Text, Card, Button, Chip, useTheme, ActivityIndicator } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons as Icon } from '@expo/vector-icons';

import { useApi } from '@/contexts/ApiContext';
import { Mission, Agent } from '@/types';
import ApiService from '@/services/api';

const HomeScreen: React.FC = () => {
  const theme = useTheme();
  const { baseUrl, isConnected, connectionError, switchToNgrok, switchToRailway } = useApi();
  const [missions, setMissions] = useState<Mission[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const apiService = new ApiService(baseUrl);

  const loadData = async () => {
    if (!isConnected) return;
    
    try {
      setLoading(true);
      const [missionsData, agentsData] = await Promise.all([
        apiService.getMissions(),
        apiService.getAgents(),
      ]);
      setMissions(missionsData);
      setAgents(agentsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  useEffect(() => {
    loadData();
  }, [isConnected, baseUrl]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return theme.colors.primary;
      case 'executing': return theme.colors.secondary;
      case 'failed': return theme.colors.error;
      default: return theme.colors.outline;
    }
  };

  const getConnectionStatus = () => {
    if (isConnected) {
      return (
        <Card style={[styles.card, { backgroundColor: theme.colors.primaryContainer }]}>
          <Card.Content>
            <View style={styles.connectionRow}>
              <Icon name="wifi" size={24} color={theme.colors.primary} />
              <Text variant="titleMedium" style={{ color: theme.colors.primary }}>
                Connected to {baseUrl.includes('ngrok') ? 'ngrok' : 'Railway'}
              </Text>
            </View>
            <Text variant="bodySmall" style={{ color: theme.colors.onPrimaryContainer }}>
              {baseUrl}
            </Text>
          </Card.Content>
        </Card>
      );
    }

    return (
      <Card style={[styles.card, { backgroundColor: theme.colors.errorContainer }]}>
        <Card.Content>
          <View style={styles.connectionRow}>
            <Icon name="wifi-off" size={24} color={theme.colors.error} />
            <Text variant="titleMedium" style={{ color: theme.colors.error }}>
              Connection Failed
            </Text>
          </View>
          <Text variant="bodySmall" style={{ color: theme.colors.onErrorContainer }}>
            {connectionError}
          </Text>
          <View style={styles.buttonRow}>
            <Button 
              mode="outlined" 
              onPress={switchToRailway}
              style={styles.switchButton}
            >
              Try Railway
            </Button>
            <Button 
              mode="outlined" 
              onPress={switchToNgrok}
              style={styles.switchButton}
            >
              Try ngrok
            </Button>
          </View>
        </Card.Content>
      </Card>
    );
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <ScrollView 
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        <Text variant="headlineMedium" style={styles.title}>
          Sentinel Command Center
        </Text>

        {getConnectionStatus()}

        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={theme.colors.primary} />
            <Text variant="bodyMedium" style={{ marginTop: 16 }}>
              Loading system status...
            </Text>
          </View>
        ) : (
          <>
            <Card style={styles.card}>
              <Card.Title title="Recent Missions" />
              <Card.Content>
                {missions.length === 0 ? (
                  <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant }}>
                    No missions yet. Create your first mission to get started!
                  </Text>
                ) : (
                  missions.slice(0, 3).map((mission) => (
                    <View key={mission.id} style={styles.missionItem}>
                      <Text variant="titleSmall">{mission.title}</Text>
                      <Chip 
                        mode="outlined" 
                        textStyle={{ color: getStatusColor(mission.status) }}
                        style={{ borderColor: getStatusColor(mission.status) }}
                      >
                        {mission.status}
                      </Chip>
                    </View>
                  ))
                )}
              </Card.Content>
            </Card>

            <Card style={styles.card}>
              <Card.Title title="Available Agents" />
              <Card.Content>
                {agents.length === 0 ? (
                  <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant }}>
                    No agents available
                  </Text>
                ) : (
                  agents.map((agent) => (
                    <View key={agent.id} style={styles.agentItem}>
                      <Icon 
                        name="robot" 
                        size={20} 
                        color={agent.status === 'available' ? theme.colors.primary : theme.colors.outline} 
                      />
                      <Text variant="bodyMedium" style={{ flex: 1, marginLeft: 8 }}>
                        {agent.name}
                      </Text>
                      <Chip 
                        mode="outlined" 
                        compact
                        textStyle={{ color: getStatusColor(agent.status) }}
                        style={{ borderColor: getStatusColor(agent.status) }}
                      >
                        {agent.status}
                      </Chip>
                    </View>
                  ))
                )}
              </Card.Content>
            </Card>
          </>
        )}
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
  connectionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  buttonRow: {
    flexDirection: 'row',
    marginTop: 16,
    gap: 8,
  },
  switchButton: {
    flex: 1,
  },
  loadingContainer: {
    alignItems: 'center',
    padding: 32,
  },
  missionItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0,0,0,0.1)',
  },
  agentItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0,0,0,0.1)',
  },
});

export default HomeScreen; 