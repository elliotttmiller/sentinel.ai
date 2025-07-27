import React, { useEffect, useState } from 'react';
import { View, StyleSheet, FlatList, RefreshControl } from 'react-native';
import { Text, Card, Chip, useTheme, ActivityIndicator } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons as Icon } from '@expo/vector-icons';

import { useApi } from '@/contexts/ApiContext';
import { Agent } from '@/types';
import ApiService from '@/services/api';

const AgentsScreen: React.FC = () => {
  const theme = useTheme();
  const { baseUrl, isConnected } = useApi();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const apiService = new ApiService(baseUrl);

  const loadAgents = async () => {
    if (!isConnected) return;
    
    try {
      setLoading(true);
      const data = await apiService.getAgents();
      setAgents(data);
    } catch (error) {
      console.error('Failed to load agents:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadAgents();
    setRefreshing(false);
  };

  useEffect(() => {
    loadAgents();
  }, [isConnected, baseUrl]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available': return theme.colors.primary;
      case 'busy': return theme.colors.secondary;
      case 'offline': return theme.colors.error;
      default: return theme.colors.outline;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'available': return 'robot';
      case 'busy': return 'robot-industrial';
      case 'offline': return 'robot-off';
      default: return 'robot-outline';
    }
  };

  const renderAgent = ({ item }: { item: Agent }) => (
    <Card style={styles.agentCard}>
      <Card.Content>
        <View style={styles.agentHeader}>
          <Icon 
            name={getStatusIcon(item.status)} 
            size={32} 
            color={getStatusColor(item.status)} 
          />
          <View style={styles.agentInfo}>
            <Text variant="titleMedium" style={styles.agentName}>
              {item.name}
            </Text>
            <Chip 
              mode="outlined" 
              compact
              textStyle={{ color: getStatusColor(item.status) }}
              style={{ borderColor: getStatusColor(item.status) }}
            >
              {item.status}
            </Chip>
          </View>
        </View>
        
        <Text variant="bodyMedium" style={styles.agentDescription}>
          {item.description}
        </Text>
        
        <View style={styles.capabilitiesContainer}>
          <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant, marginBottom: 8 }}>
            Capabilities:
          </Text>
          <View style={styles.capabilitiesList}>
            {item.capabilities.map((capability, index) => (
              <Chip 
                key={index} 
                mode="outlined" 
                compact
                style={styles.capabilityChip}
              >
                {capability}
              </Chip>
            ))}
          </View>
        </View>
      </Card.Content>
    </Card>
  );

  if (loading && !refreshing) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
          <Text variant="bodyMedium" style={{ marginTop: 16 }}>
            Loading agents...
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <FlatList
        data={agents}
        renderItem={renderAgent}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Icon name="robot-outline" size={64} color={theme.colors.outline} />
            <Text variant="titleMedium" style={{ color: theme.colors.onSurfaceVariant, marginTop: 16 }}>
              No agents available
            </Text>
            <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant, textAlign: 'center' }}>
              AI agents will appear here when the system is running
            </Text>
          </View>
        }
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  listContainer: {
    padding: 16,
  },
  agentCard: {
    marginBottom: 16,
  },
  agentHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  agentInfo: {
    flex: 1,
    marginLeft: 16,
  },
  agentName: {
    marginBottom: 8,
  },
  agentDescription: {
    marginBottom: 16,
  },
  capabilitiesContainer: {
    marginTop: 8,
  },
  capabilitiesList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  capabilityChip: {
    marginBottom: 4,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 64,
  },
});

export default AgentsScreen; 