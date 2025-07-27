import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { Mission, MissionPlan, MissionResult, Agent } from '@/types';

class ApiService {
  private client: AxiosInstance;
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.client = axios.create({
      baseURL: baseUrl,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for logging
    this.client.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Add response interceptor for logging
    this.client.interceptors.response.use(
      (response) => {
        console.log(`API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error('API Response Error:', error);
        return Promise.reject(error);
      }
    );
  }

  updateBaseUrl(newBaseUrl: string) {
    this.baseUrl = newBaseUrl;
    this.client.defaults.baseURL = newBaseUrl;
  }

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.client.get('/health');
      return response.status === 200;
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }

  // Missions
  async createMission(title: string, description: string): Promise<Mission> {
    const response: AxiosResponse<Mission> = await this.client.post('/missions', {
      title,
      description,
    });
    return response.data;
  }

  async getMissions(): Promise<Mission[]> {
    const response: AxiosResponse<Mission[]> = await this.client.get('/missions');
    return response.data;
  }

  async getMission(id: string): Promise<Mission> {
    const response: AxiosResponse<Mission> = await this.client.get(`/missions/${id}`);
    return response.data;
  }

  async updateMission(id: string, updates: Partial<Mission>): Promise<Mission> {
    const response: AxiosResponse<Mission> = await this.client.put(`/missions/${id}`, updates);
    return response.data;
  }

  async deleteMission(id: string): Promise<void> {
    await this.client.delete(`/missions/${id}`);
  }

  // Mission Plans
  async getMissionPlan(missionId: string): Promise<MissionPlan> {
    const response: AxiosResponse<MissionPlan> = await this.client.get(`/missions/${missionId}/plan`);
    return response.data;
  }

  async executeMission(missionId: string): Promise<MissionResult> {
    const response: AxiosResponse<MissionResult> = await this.client.post(`/missions/${missionId}/execute`);
    return response.data;
  }

  // Agents
  async getAgents(): Promise<Agent[]> {
    const response: AxiosResponse<Agent[]> = await this.client.get('/agents');
    return response.data;
  }

  async getAgent(id: string): Promise<Agent> {
    const response: AxiosResponse<Agent> = await this.client.get(`/agents/${id}`);
    return response.data;
  }

  // WebSocket connection for real-time updates
  getWebSocketUrl(): string {
    const wsUrl = this.baseUrl.replace('https://', 'wss://').replace('http://', 'ws://');
    return `${wsUrl}/ws`;
  }
}

export default ApiService; 