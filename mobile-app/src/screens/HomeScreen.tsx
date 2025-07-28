import React, { useEffect, useState } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl, TouchableOpacity } from 'react-native';
import { Text, Card, Button, Chip, useTheme, ActivityIndicator, IconButton, Divider } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons as Icon } from '@expo/vector-icons';

import { useApi } from '@/contexts/ApiContext';
import { Mission, Agent } from '@/types';
import ApiService from '@/services/api';

// Enhanced debug logging for HomeScreen
const debugLog = (message: string, data?: any) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] HOMESCREEN: ${message}`, data ? JSON.stringify(data, null, 2) : '');
};

const HomeScreen: React.FC = () => {
  const theme = useTheme();
  const api = useApi();
  const baseUrl = api?.baseUrl ?? '';
  const isConnected = api?.isConnected ?? false;
  const connectionError = api?.connectionError ?? null;
  const [missions, setMissions] = useState<Mission[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [systemStatus, setSystemStatus] = useState({
    backend: 'unknown',
    desktop: 'unknown',
    ngrok: 'unknown',
    railway: 'unknown'
  });

  debugLog('HomeScreen render state:', {
    baseUrl,
    isConnected,
    connectionError,
    loading,
    refreshing,
    systemStatus,
    missionsCount: missions.length,
    agentsCount: agents.length
  });

  const apiService = new ApiService(baseUrl);

  const loadData = async () => {
    debugLog('loadData called', { isConnected, baseUrl });
    
    if (!isConnected) {
      debugLog('Skipping data load - not connected');
      return;
    }
    
    try {
      setLoading(true);
      debugLog('Starting data load...');
      
      const [missionsData, agentsData, systemStatusData] = await Promise.all([
        apiService.getMissions(),
        apiService.getAgents(),
        apiService.getSystemStatus(),
      ]);
      
      debugLog('Data loaded successfully:', {
        missionsCount: missionsData.length,
        agentsCount: agentsData.length,
        systemStatus: systemStatusData
      });
      
      setMissions(missionsData);
      setAgents(agentsData);
      setSystemStatus(systemStatusData);
      
    } catch (error) {
      debugLog('Failed to load data:', error);
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
      debugLog('Data loading completed');
    }
  };

  const onRefresh = async () => {
    debugLog('Manual refresh triggered');
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
    debugLog('Manual refresh completed');
  };

  useEffect(() => {
    debugLog('HomeScreen useEffect triggered', { isConnected, baseUrl });
    loadData();
  }, [isConnected, baseUrl]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
      case 'online':
      case 'available':
        return theme.colors.primary;
      case 'executing':
      case 'running':
        return theme.colors.secondary;
      case 'failed':
      case 'offline':
      case 'error':
        return theme.colors.error;
      default:
        return theme.colors.outline;
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
                Connected to Railway
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
            {connectionError || 'Unable to connect to server'}
          </Text>
        </Card.Content>
      </Card>
    );
  };

  const getSystemStatusCard = () => (
    <Card style={styles.card}>
      <Card.Title title="System Status" left={(props) => <Icon {...props} name="monitor-dashboard" />} />
      <Card.Content>
        <View style={styles.statusGrid}>
          <View style={styles.statusItem}>
            <Icon 
              name={systemStatus.backend === 'online' ? 'server' : 'server-off'} 
              size={20} 
              color={getStatusColor(systemStatus.backend)} 
            />
            <Text variant="bodySmall">Backend</Text>
            <Chip 
              mode="outlined" 
              compact
              textStyle={{ color: getStatusColor(systemStatus.backend) }}
              style={{ borderColor: getStatusColor(systemStatus.backend) }}
            >
              {systemStatus.backend}
            </Chip>
          </View>
          <View style={styles.statusItem}>
            <Icon 
              name={systemStatus.desktop === 'online' ? 'desktop-tower' : 'desktop-tower-monitor'} 
              size={20} 
              color={getStatusColor(systemStatus.desktop)} 
            />
            <Text variant="bodySmall">Desktop</Text>
            <Chip 
              mode="outlined" 
              compact
              textStyle={{ color: getStatusColor(systemStatus.desktop) }}
              style={{ borderColor: getStatusColor(systemStatus.desktop) }}
            >
              {systemStatus.desktop}
            </Chip>
          </View>
          <View style={styles.statusItem}>
            <Icon 
              name={systemStatus.ngrok === 'online' ? 'tunnel' : 'tunnel-outline'} 
              size={20} 
              color={getStatusColor(systemStatus.ngrok)} 
            />
            <Text variant="bodySmall">ngrok</Text>
            <Chip 
              mode="outlined" 
              compact
              textStyle={{ color: getStatusColor(systemStatus.ngrok) }}
              style={{ borderColor: getStatusColor(systemStatus.ngrok) }}
            >
              {systemStatus.ngrok}
            </Chip>
          </View>
          <View style={styles.statusItem}>
            <Icon 
              name={systemStatus.railway === 'online' ? 'cloud' : 'cloud-outline'} 
              size={20} 
              color={getStatusColor(systemStatus.railway)} 
            />
            <Text variant="bodySmall">Railway</Text>
            <Chip 
              mode="outlined" 
              compact
              textStyle={{ color: getStatusColor(systemStatus.railway) }}
              style={{ borderColor: getStatusColor(systemStatus.railway) }}
            >
              {systemStatus.railway}
            </Chip>
          </View>
        </View>
      </Card.Content>
    </Card>
  );

  const getQuickActionsCard = () => (
    <Card style={styles.card}>
      <Card.Title title="Quick Actions" left={(props) => <Icon {...props} name="lightning-bolt" />} />
      <Card.Content>
        <View style={styles.actionsGrid}>
          <TouchableOpacity style={styles.actionButton}>
            <Icon name="plus-circle" size={32} color={theme.colors.primary} />
            <Text variant="bodySmall">New Mission</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.actionButton}>
            <Icon name="robot" size={32} color={theme.colors.secondary} />
            <Text variant="bodySmall">Manage Agents</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.actionButton}>
            <Icon name="cog" size={32} color={theme.colors.tertiary} />
            <Text variant="bodySmall">Settings</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.actionButton}>
            <Icon name="refresh" size={32} color={theme.colors.primary} />
            <Text variant="bodySmall">Refresh</Text>
          </TouchableOpacity>
        </View>
      </Card.Content>
    </Card>
  );

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
        {getSystemStatusCard()}
        {getQuickActionsCard()}

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
              <Card.Title title="Recent Missions" left={(props) => <Icon {...props} name="rocket-launch" />} />
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
              <Card.Title title="Available Agents" left={(props) => <Icon {...props} name="robot" />} />
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
  statusGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statusItem: {
    alignItems: 'center',
    width: '48%',
    marginBottom: 16,
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  actionButton: {
    alignItems: 'center',
    width: '48%',
    padding: 16,
    marginBottom: 16,
    borderRadius: 8,
    backgroundColor: 'rgba(0,0,0,0.05)',
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