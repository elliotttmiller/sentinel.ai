export interface Mission {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'planning' | 'executing' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
  completed_at?: string;
  steps?: MissionStep[];
  plan?: MissionPlan;
  result?: MissionResult;
}

export interface MissionPlan {
  id: string;
  mission_id: string;
  steps: MissionStep[];
  status: 'draft' | 'approved' | 'executing' | 'completed';
  created_at: string;
  updated_at: string;
}

export interface MissionStep {
  id: string;
  plan_id: string;
  order: number;
  title: string;
  description: string;
  agent_type: string;
  status: 'pending' | 'executing' | 'completed' | 'failed';
  result?: any;
}

export interface MissionResult {
  id: string;
  mission_id: string;
  status: 'success' | 'partial' | 'failed';
  summary: string;
  details: any;
  created_at: string;
}

export interface Agent {
  id: string;
  name: string;
  type?: string;
  description?: string;
  capabilities?: string[];
  status: 'available' | 'busy' | 'offline' | 'maintenance';
  last_active?: string;
  missions_completed?: number;
}

export interface ApiConfig {
  apiUrl: string;
}

export interface AppState {
  missions: Mission[];
  agents: Agent[];
  loading: boolean;
  error: string | null;
}

export interface NavigationProps {
  navigation: any;
  route: any;
} 