import React, { useEffect, useState } from 'react';
import { View, StyleSheet, FlatList, RefreshControl, ScrollView } from 'react-native';
import { Text, Card, Chip, useTheme, ActivityIndicator, Searchbar, FAB, Menu, Divider, IconButton } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons as Icon } from '@expo/vector-icons';

import { useApi } from '@/contexts/ApiContext';
import { Mission } from '@/types';
import ApiService from '@/services/api';

const MissionsScreen: React.FC = () => {
  const theme = useTheme();
  const { baseUrl, isConnected } = useApi();
  const [missions, setMissions] = useState<Mission[]>([]);
  const [filteredMissions, setFilteredMissions] = useState<Mission[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [menuVisible, setMenuVisible] = useState(false);

  const apiService = new ApiService(baseUrl);

  const loadMissions = async () => {
    if (!isConnected) return;
    
    try {
      setLoading(true);
      const missionsData = await apiService.getMissions();
      setMissions(missionsData);
    } catch (error) {
      console.error('Failed to load missions:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadMissions();
    setRefreshing(false);
  };

  useEffect(() => {
    loadMissions();
  }, [isConnected, baseUrl]);

  useEffect(() => {
    let filtered = missions;

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(mission =>
        mission.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        mission.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Apply status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(mission => mission.status === statusFilter);
    }

    setFilteredMissions(filtered);
  }, [missions, searchQuery, statusFilter]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return theme.colors.primary;
      case 'executing': return theme.colors.secondary;
      case 'failed': return theme.colors.error;
      case 'pending': return theme.colors.tertiary;
      default: return theme.colors.outline;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return 'check-circle';
      case 'executing': return 'play-circle';
      case 'failed': return 'close-circle';
      case 'pending': return 'clock-outline';
      default: return 'help-circle';
    }
  };

  const renderMissionCard = ({ item }: { item: Mission }) => (
    <Card style={styles.missionCard} mode="outlined">
      <Card.Content>
        <View style={styles.missionHeader}>
          <View style={styles.missionTitle}>
            <Text variant="titleMedium" numberOfLines={1}>
              {item.title}
            </Text>
            <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
              ID: {item.id}
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
        
        <Text variant="bodyMedium" style={styles.description} numberOfLines={2}>
          {item.description}
        </Text>
        
        <View style={styles.missionMeta}>
          <View style={styles.metaItem}>
            <Icon name="calendar" size={16} color={theme.colors.onSurfaceVariant} />
            <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant, marginLeft: 4 }}>
              {new Date(item.created_at).toLocaleDateString()}
            </Text>
          </View>
          {item.completed_at && (
            <View style={styles.metaItem}>
              <Icon name="check" size={16} color={theme.colors.primary} />
              <Text variant="bodySmall" style={{ color: theme.colors.primary, marginLeft: 4 }}>
                {new Date(item.completed_at).toLocaleDateString()}
              </Text>
            </View>
          )}
        </View>

        {item.steps && item.steps.length > 0 && (
          <View style={styles.stepsPreview}>
            <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant, marginBottom: 4 }}>
              Steps: {item.steps.length}
            </Text>
            {item.steps.slice(0, 2).map((step, index) => (
              <View key={index} style={styles.stepItem}>
                <Icon 
                  name={step.status === 'completed' ? 'check' : 'circle-outline'} 
                  size={16} 
                  color={step.status === 'completed' ? theme.colors.primary : theme.colors.outline} 
                />
                <Text variant="bodySmall" style={{ marginLeft: 8, flex: 1 }}>
                  {step.description}
                </Text>
              </View>
            ))}
            {item.steps.length > 2 && (
              <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant, fontStyle: 'italic' }}>
                +{item.steps.length - 2} more steps
              </Text>
            )}
          </View>
        )}
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
          All ({missions.length})
        </Chip>
        <Chip 
          mode={statusFilter === 'pending' ? 'flat' : 'outlined'}
          onPress={() => setStatusFilter('pending')}
          style={styles.filterChip}
        >
          Pending ({missions.filter(m => m.status === 'pending').length})
        </Chip>
        <Chip 
          mode={statusFilter === 'executing' ? 'flat' : 'outlined'}
          onPress={() => setStatusFilter('executing')}
          style={styles.filterChip}
        >
          Executing ({missions.filter(m => m.status === 'executing').length})
        </Chip>
        <Chip 
          mode={statusFilter === 'completed' ? 'flat' : 'outlined'}
          onPress={() => setStatusFilter('completed')}
          style={styles.filterChip}
        >
          Completed ({missions.filter(m => m.status === 'completed').length})
        </Chip>
        <Chip 
          mode={statusFilter === 'failed' ? 'flat' : 'outlined'}
          onPress={() => setStatusFilter('failed')}
          style={styles.filterChip}
        >
          Failed ({missions.filter(m => m.status === 'failed').length})
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
            Loading missions...
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.header}>
        <Text variant="headlineSmall" style={styles.title}>
          Missions
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
          <Menu.Item onPress={() => {}} title="Sort by Date" />
          <Menu.Item onPress={() => {}} title="Sort by Status" />
          <Menu.Item onPress={() => {}} title="Export Missions" />
          <Divider />
          <Menu.Item onPress={() => {}} title="Clear Completed" />
        </Menu>
      </View>

      <Searchbar
        placeholder="Search missions..."
        onChangeText={setSearchQuery}
        value={searchQuery}
        style={styles.searchbar}
      />

      {getFilterChips()}

      <FlatList
        data={filteredMissions}
        renderItem={renderMissionCard}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Icon name="rocket-launch-outline" size={64} color={theme.colors.onSurfaceVariant} />
            <Text variant="titleMedium" style={{ color: theme.colors.onSurfaceVariant, marginTop: 16 }}>
              {searchQuery || statusFilter !== 'all' ? 'No missions found' : 'No missions yet'}
            </Text>
            <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant, textAlign: 'center' }}>
              {searchQuery || statusFilter !== 'all' 
                ? 'Try adjusting your search or filters' 
                : 'Create your first mission to get started!'
              }
            </Text>
          </View>
        }
      />

      <FAB
        icon="plus"
        style={[styles.fab, { backgroundColor: theme.colors.primary }]}
        onPress={() => {}}
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
  missionCard: {
    marginBottom: 12,
  },
  missionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  missionTitle: {
    flex: 1,
    marginRight: 8,
  },
  description: {
    marginBottom: 12,
  },
  missionMeta: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 16,
  },
  stepsPreview: {
    borderTopWidth: 1,
    borderTopColor: 'rgba(0,0,0,0.1)',
    paddingTop: 8,
  },
  stepItem: {
    flexDirection: 'row',
    alignItems: 'center',
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
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
  },
});

export default MissionsScreen; 