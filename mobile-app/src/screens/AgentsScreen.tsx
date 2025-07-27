import React, { useEffect, useState } from 'react';
import { View, StyleSheet, FlatList, RefreshControl, ScrollView } from 'react-native';
import { Text, Card, Chip, useTheme, ActivityIndicator, Searchbar, IconButton, Menu, Divider, Button } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons as Icon } from '@expo/vector-icons';

import { useApi } from '@/contexts/ApiContext';
import { Agent } from '@/types';
import ApiService from '@/services/api';

const AgentsScreen: React.FC = () => {
  const theme = useTheme();
  const { baseUrl, isConnected } = useApi();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [filteredAgents, setFilteredAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [menuVisible, setMenuVisible] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);

  const apiService = new ApiService(baseUrl);

  const loadAgents = async () => {
    if (!isConnected) return;
    
    try {
      setLoading(true);
      const agentsData = await apiService.getAgents();
      setAgents(agentsData);
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

  useEffect(() => {
    let filtered = agents;

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(agent =>
        agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        agent.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        agent.capabilities?.some(cap => cap.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    // Apply status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(agent => agent.status === statusFilter);
    }

    setFilteredAgents(filtered);
  }, [agents, searchQuery, statusFilter]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available': return theme.colors.primary;
      case 'busy': return theme.colors.secondary;
      case 'offline': return theme.colors.error;
      case 'maintenance': return theme.colors.tertiary;
      default: return theme.colors.outline;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'available': return 'check-circle';
      case 'busy': return 'clock';
      case 'offline': return 'close-circle';
      case 'maintenance': return 'wrench';
      default: return 'help-circle';
    }
  };

  const getAgentTypeIcon = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'code_reviewer': return 'code-braces';
      case 'debugger': return 'bug';
      case 'planner': return 'clipboard-list';
      case 'executor': return 'play-circle';
      default: return 'robot';
    }
  };

  const renderAgentCard = ({ item }: { item: Agent }) => (
    <Card style={styles.agentCard} mode="outlined">
      <Card.Content>
        <View style={styles.agentHeader}>
          <View style={styles.agentInfo}>
            <View style={styles.agentTitle}>
              <Icon 
                name={getAgentTypeIcon(item.type)} 
                size={24} 
                color={theme.colors.primary} 
              />
              <Text variant="titleMedium" style={{ marginLeft: 8, flex: 1 }}>
                {item.name}
              </Text>
            </View>
            <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant, marginLeft: 32 }}>
              {item.type || 'Unknown Type'}
            </Text>
          </View>
          <Chip 
            mode="outlined" 
            textStyle={{ color: getStatusColor(item.status) }}
            style={{ borderColor: getStatusColor(item.status) }}
            icon={getStatusIcon(item.status)}
          >
            {item.status}
          </Chip>
        </View>
        
        {item.description && (
          <Text variant="bodyMedium" style={styles.description} numberOfLines={2}>
            {item.description}
          </Text>
        )}
        
        <View style={styles.agentMeta}>
          <View style={styles.metaItem}>
            <Icon name="clock" size={16} color={theme.colors.onSurfaceVariant} />
            <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant, marginLeft: 4 }}>
              {item.last_active ? new Date(item.last_active).toLocaleDateString() : 'Never'}
            </Text>
          </View>
          {item.missions_completed && (
            <View style={styles.metaItem}>
              <Icon name="check-circle" size={16} color={theme.colors.primary} />
              <Text variant="bodySmall" style={{ color: theme.colors.primary, marginLeft: 4 }}>
                {item.missions_completed} missions
              </Text>
            </View>
          )}
        </View>

        {item.capabilities && item.capabilities.length > 0 && (
          <View style={styles.capabilitiesContainer}>
            <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant, marginBottom: 8 }}>
              Capabilities:
            </Text>
            <View style={styles.capabilitiesList}>
              {item.capabilities.slice(0, 3).map((capability, index) => (
                <Chip 
                  key={index}
                  mode="outlined" 
                  compact
                  style={styles.capabilityChip}
                >
                  {capability}
                </Chip>
              ))}
              {item.capabilities.length > 3 && (
                <Chip 
                  mode="outlined" 
                  compact
                  style={styles.capabilityChip}
                >
                  +{item.capabilities.length - 3} more
                </Chip>
              )}
            </View>
          </View>
        )}

        <View style={styles.agentActions}>
          <Button 
            mode="outlined" 
            compact
            onPress={() => setSelectedAgent(item)}
            style={styles.actionButton}
          >
            Details
          </Button>
          {item.status === 'available' && (
            <Button 
              mode="contained" 
              compact
              onPress={() => {}}
              style={styles.actionButton}
            >
              Assign Mission
            </Button>
          )}
        </View>
      </Card.Content>
    </Card>
  );

  const getFilterChips = () => (
    <View style={styles.filterContainer}>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <Chip 
          mode={statusFilter === 'all' ? 'flat' : 'outlined'}
          onPress={() => setStatusFilter('all')}
          style={styles.filterChip}
        >
          All ({agents.length})
        </Chip>
        <Chip 
          mode={statusFilter === 'available' ? 'flat' : 'outlined'}
          onPress={() => setStatusFilter('available')}
          style={styles.filterChip}
        >
          Available ({agents.filter(a => a.status === 'available').length})
        </Chip>
        <Chip 
          mode={statusFilter === 'busy' ? 'flat' : 'outlined'}
          onPress={() => setStatusFilter('busy')}
          style={styles.filterChip}
        >
          Busy ({agents.filter(a => a.status === 'busy').length})
        </Chip>
        <Chip 
          mode={statusFilter === 'offline' ? 'flat' : 'outlined'}
          onPress={() => setStatusFilter('offline')}
          style={styles.filterChip}
        >
          Offline ({agents.filter(a => a.status === 'offline').length})
        </Chip>
      </ScrollView>
    </View>
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
      <View style={styles.header}>
        <Text variant="headlineSmall" style={styles.title}>
          AI Agents
        </Text>
        <Menu
          visible={menuVisible}
          onDismiss={() => setMenuVisible(false)}
          anchor={
            <IconButton
              icon="dots-vertical"
              onPress={() => setMenuVisible(true)}
            />
          }
        >
          <Menu.Item onPress={() => {}} title="Sort by Status" />
          <Menu.Item onPress={() => {}} title="Sort by Type" />
          <Menu.Item onPress={() => {}} title="Export Agents" />
          <Divider />
          <Menu.Item onPress={() => {}} title="Restart All" />
        </Menu>
      </View>

      <Searchbar
        placeholder="Search agents..."
        onChangeText={setSearchQuery}
        value={searchQuery}
        style={styles.searchbar}
      />

      {getFilterChips()}

      <FlatList
        data={filteredAgents}
        renderItem={renderAgentCard}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Icon name="robot-outline" size={64} color={theme.colors.onSurfaceVariant} />
            <Text variant="titleMedium" style={{ color: theme.colors.onSurfaceVariant, marginTop: 16 }}>
              {searchQuery || statusFilter !== 'all' ? 'No agents found' : 'No agents available'}
            </Text>
            <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant, textAlign: 'center' }}>
              {searchQuery || statusFilter !== 'all' 
                ? 'Try adjusting your search or filters' 
                : 'Agents will appear here when they are registered'
              }
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
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
  },
  title: {
    flex: 1,
  },
  searchbar: {
    marginHorizontal: 16,
    marginBottom: 8,
  },
  filterContainer: {
    paddingHorizontal: 16,
    marginBottom: 8,
  },
  filterChip: {
    marginRight: 8,
  },
  listContainer: {
    padding: 16,
  },
  agentCard: {
    marginBottom: 12,
  },
  agentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  agentInfo: {
    flex: 1,
    marginRight: 8,
  },
  agentTitle: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  description: {
    marginBottom: 12,
  },
  agentMeta: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 16,
  },
  capabilitiesContainer: {
    marginBottom: 12,
  },
  capabilitiesList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  capabilityChip: {
    marginRight: 8,
    marginBottom: 4,
  },
  agentActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 8,
  },
  actionButton: {
    minWidth: 80,
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