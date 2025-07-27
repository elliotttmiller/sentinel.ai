export interface Mission {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'planning' | 'executing' | 'completed' | 'failed';
  createdAt: string;
  updatedAt: string;
  plan?: MissionPlan;
  result?: MissionResult;
}

export interface MissionPlan {
  id: string;
  missionId: string;
  steps: MissionStep[];
  estimatedDuration: number;
  createdAt: string;
}

export interface MissionStep {
  id: string;
  title: string;
  description: string;
  agent: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: any;
}

export interface MissionResult {
  id: string;
  missionId: string;
  success: boolean;
  output: any;
  logs: string[];
  completedAt: string;
}

export interface Agent {
  id: string;
  name: string;
  description: string;
  capabilities: string[];
  status: 'available' | 'busy' | 'offline';
}

export interface ApiConfig {
  railwayUrl: string;
  ngrokUrl: string;
  websocketUrl: string;
  useNgrok: boolean;
}

export interface AppState {
  missions: Mission[];
  agents: Agent[];
  isLoading: boolean;
  error: string | null;
}

export interface NavigationProps {
  navigation: any;
  route: any;
} 