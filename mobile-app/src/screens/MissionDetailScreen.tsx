import React, { useEffect, useState } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Text, Card, Button, Chip, useTheme, ActivityIndicator, Divider } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons as Icon } from '@expo/vector-icons';

import { useApi } from '@/contexts/ApiContext';
import { Mission, MissionPlan, MissionStep, NavigationProps } from '@/types';
import ApiService from '@/services/api';

const MissionDetailScreen: React.FC<NavigationProps> = ({ navigation, route }) => {
  const theme = useTheme();
  const { baseUrl, isConnected } = useApi();
  const [mission, setMission] = useState<Mission | null>(null);
  const [plan, setPlan] = useState<MissionPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [executing, setExecuting] = useState(false);

  const { missionId } = route.params as { missionId: string };
  const apiService = new ApiService(baseUrl);

  const loadMissionData = async () => {
    if (!isConnected) return;
    
    try {
      setLoading(true);
      const [missionData, planData] = await Promise.all([
        apiService.getMission(missionId),
        apiService.getMissionPlan(missionId).catch(() => null),
      ]);
      setMission(missionData);
      setPlan(planData);
    } catch (error) {
      console.error('Failed to load mission data:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadMissionData();
    setRefreshing(false);
  };

  const handleExecuteMission = async () => {
    if (!mission) return;

    try {
      setExecuting(true);
      await apiService.executeMission(mission.id);
      await loadMissionData(); // Refresh to get updated status
    } catch (error) {
      console.error('Failed to execute mission:', error);
    } finally {
      setExecuting(false);
    }
  };

  useEffect(() => {
    loadMissionData();
  }, [isConnected, baseUrl, missionId]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return theme.colors.primary;
      case 'executing': return theme.colors.secondary;
      case 'failed': return theme.colors.error;
      default: return theme.colors.outline;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return 'check-circle';
      case 'executing': return 'play-circle';
      case 'failed': return 'alert-circle';
      default: return 'clock-outline';
    }
  };

  const getStepStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return 'check';
      case 'running': return 'play';
      case 'failed': return 'close';
      default: return 'circle-outline';
    }
  };

  if (loading && !refreshing) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
          <Text variant="bodyMedium" style={{ marginTop: 16 }}>
            Loading mission details...
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  if (!mission) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
        <View style={styles.errorContainer}>
          <Icon name="alert-circle" size={64} color={theme.colors.error} />
          <Text variant="titleMedium" style={{ color: theme.colors.error, marginTop: 16 }}>
            Mission not found
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <ScrollView 
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        <Card style={styles.card}>
          <Card.Content>
            <View style={styles.missionHeader}>
              <Text variant="headlineSmall" style={styles.missionTitle}>
                {mission.title}
              </Text>
              <Icon 
                name={getStatusIcon(mission.status)} 
                size={32} 
                color={getStatusColor(mission.status)} 
              />
            </View>
            
            <Chip 
              mode="outlined" 
              textStyle={{ color: getStatusColor(mission.status) }}
              style={{ borderColor: getStatusColor(mission.status), alignSelf: 'flex-start' }}
            >
              {mission.status}
            </Chip>
            
            <Text variant="bodyLarge" style={styles.description}>
              {mission.description}
            </Text>
            
            <View style={styles.metaInfo}>
              <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                Created: {new Date(mission.createdAt).toLocaleString()}
              </Text>
              <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                Updated: {new Date(mission.updatedAt).toLocaleString()}
              </Text>
            </View>
          </Card.Content>
        </Card>

        {plan && (
          <Card style={styles.card}>
            <Card.Title title="Execution Plan" />
            <Card.Content>
              <Text variant="bodyMedium" style={{ marginBottom: 16 }}>
                Estimated duration: {plan.estimatedDuration} minutes
              </Text>
              
              {plan.steps.map((step: MissionStep, index: number) => (
                <View key={step.id} style={styles.stepContainer}>
                  <View style={styles.stepHeader}>
                    <Icon 
                      name={getStepStatusIcon(step.status)} 
                      size={20} 
                      color={getStatusColor(step.status)} 
                    />
                    <Text variant="titleSmall" style={styles.stepTitle}>
                      Step {index + 1}: {step.title}
                    </Text>
                  </View>
                  <Text variant="bodySmall" style={styles.stepDescription}>
                    {step.description}
                  </Text>
                  <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                    Agent: {step.agent}
                  </Text>
                  {index < plan.steps.length - 1 && <Divider style={styles.divider} />}
                </View>
              ))}
            </Card.Content>
          </Card>
        )}

        {mission.result && (
          <Card style={styles.card}>
            <Card.Title title="Mission Result" />
            <Card.Content>
              <View style={styles.resultHeader}>
                <Icon 
                  name={mission.result.success ? 'check-circle' : 'alert-circle'} 
                  size={24} 
                  color={mission.result.success ? theme.colors.primary : theme.colors.error} 
                />
                <Text variant="titleMedium" style={{ marginLeft: 8 }}>
                  {mission.result.success ? 'Success' : 'Failed'}
                </Text>
              </View>
              
              <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant, marginBottom: 8 }}>
                Completed: {new Date(mission.result.completedAt).toLocaleString()}
              </Text>
              
              <Text variant="bodyMedium" style={styles.resultOutput}>
                {JSON.stringify(mission.result.output, null, 2)}
              </Text>
            </Card.Content>
          </Card>
        )}

        {mission.status === 'pending' && (
          <Card style={styles.card}>
            <Card.Content>
              <Button
                mode="contained"
                onPress={handleExecuteMission}
                loading={executing}
                disabled={executing || !isConnected}
                style={styles.executeButton}
              >
                Execute Mission
              </Button>
            </Card.Content>
          </Card>
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
  card: {
    marginBottom: 16,
  },
  missionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  missionTitle: {
    flex: 1,
    marginRight: 16,
  },
  description: {
    marginTop: 16,
    marginBottom: 16,
  },
  metaInfo: {
    gap: 4,
  },
  stepContainer: {
    marginBottom: 16,
  },
  stepHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  stepTitle: {
    marginLeft: 8,
    flex: 1,
  },
  stepDescription: {
    marginBottom: 4,
  },
  divider: {
    marginTop: 16,
  },
  resultHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  resultOutput: {
    backgroundColor: 'rgba(0,0,0,0.05)',
    padding: 12,
    borderRadius: 8,
    fontFamily: 'monospace',
  },
  executeButton: {
    marginTop: 8,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
});

export default MissionDetailScreen; 