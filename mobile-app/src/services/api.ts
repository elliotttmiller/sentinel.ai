import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { Mission, MissionPlan, MissionResult, Agent } from '@/types';

// Centralized debugLog utility
export function debugLog(...args: any[]) {
  if (typeof console !== 'undefined' && console.log) {
    console.log('[DEBUG]', ...args);
  }
}

class ApiService {
  private client: AxiosInstance;
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    debugLog('ApiService initialized', { baseUrl });
    
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
        debugLog(`API Request:`, {
          method: config.method?.toUpperCase(),
          url: config.url,
          baseURL: config.baseURL,
          fullUrl: `${config.baseURL}${config.url}`,
          headers: config.headers,
          timeout: config.timeout
        });
        return config;
      },
      (error) => {
        debugLog('API Request Error:', {
          message: error.message,
          code: error.code,
          config: error.config
        });
        return Promise.reject(error);
      }
    );

    // Add response interceptor for logging
    this.client.interceptors.response.use(
      (response) => {
        debugLog(`API Response:`, {
          status: response.status,
          statusText: response.statusText,
          url: response.config.url,
          data: response.data,
          headers: response.headers
        });
        return response;
      },
      (error) => {
        debugLog('API Response Error:', {
          message: error.message,
          status: error.response?.status,
          statusText: error.response?.statusText,
          url: error.config?.url,
          data: error.response?.data,
          headers: error.response?.headers
        });
        return Promise.reject(error);
      }
    );
  }

  updateBaseUrl(newBaseUrl: string) {
    debugLog('Updating base URL:', { oldUrl: this.baseUrl, newUrl: newBaseUrl });
    this.baseUrl = newBaseUrl;
    this.client.defaults.baseURL = newBaseUrl;
  }

  // Health check
  async healthCheck(): Promise<boolean> {
    debugLog('Starting health check');
    try {
      const response = await this.client.get('/health');
      const result = response.status === 200;
      debugLog('Health check result:', { success: result, status: response.status });
      return result;
    } catch (error: any) {
      debugLog('Health check failed:', {
        error: error.message,
        status: error.response?.status,
        data: error.response?.data
      });
      return false;
    }
  }

  // Missions
  async createMission(title: string, description: string): Promise<Mission> {
    debugLog('Creating mission:', { title, description });
    const response: AxiosResponse<Mission> = await this.client.post('/missions', {
      title,
      description,
    });
    debugLog('Mission created:', response.data);
    return response.data;
  }

  async getMissions(): Promise<Mission[]> {
    debugLog('Fetching missions');
    const response: AxiosResponse<Mission[]> = await this.client.get('/missions');
    debugLog('Missions fetched:', { count: response.data.length });
    return response.data;
  }

  async getMission(id: string): Promise<Mission> {
    debugLog('Fetching mission:', { id });
    const response: AxiosResponse<Mission> = await this.client.get(`/missions/${id}`);
    debugLog('Mission fetched:', response.data);
    return response.data;
  }

  async updateMission(id: string, updates: Partial<Mission>): Promise<Mission> {
    debugLog('Updating mission:', { id, updates });
    const response: AxiosResponse<Mission> = await this.client.put(`/missions/${id}`, updates);
    debugLog('Mission updated:', response.data);
    return response.data;
  }

  async deleteMission(id: string): Promise<void> {
    debugLog('Deleting mission:', { id });
    await this.client.delete(`/missions/${id}`);
    debugLog('Mission deleted:', { id });
  }

  // Mission Plans
  async getMissionPlan(missionId: string): Promise<MissionPlan> {
    debugLog('Fetching mission plan:', { missionId });
    const response: AxiosResponse<MissionPlan> = await this.client.get(`/missions/${missionId}/plan`);
    debugLog('Mission plan fetched:', response.data);
    return response.data;
  }

  async executeMission(missionId: string): Promise<MissionResult> {
    debugLog('Executing mission:', { missionId });
    const response: AxiosResponse<MissionResult> = await this.client.post(`/missions/${missionId}/execute`);
    debugLog('Mission executed:', response.data);
    return response.data;
  }

  // Agents
  async getAgents(): Promise<Agent[]> {
    debugLog('Fetching agents');
    const response: AxiosResponse<Agent[]> = await this.client.get('/agents');
    debugLog('Agents fetched:', { count: response.data.length });
    return response.data;
  }

  async getAgent(id: string): Promise<Agent> {
    debugLog('Fetching agent:', { id });
    const response: AxiosResponse<Agent> = await this.client.get(`/agents/${id}`);
    debugLog('Agent fetched:', response.data);
    return response.data;
  }

  // System Status
  async getSystemStatus(): Promise<{
    backend: string;
    desktop: string;
    railway: string;
    ngrok: string;
    details?: any;
  }> {
    debugLog('Fetching system status');
    const response: AxiosResponse<{
      backend: string;
      desktop: string;
      railway: string;
      ngrok: string;
      details?: any;
    }> = await this.client.get('/system-status');
    debugLog('System status fetched:', response.data);
    return response.data;
  }

  // WebSocket connection for real-time updates
  getWebSocketUrl(): string {
    const wsUrl = this.baseUrl.replace('https://', 'wss://').replace('http://', 'ws://');
    const fullWsUrl = `${wsUrl}/ws`;
    debugLog('WebSocket URL generated:', { baseUrl: this.baseUrl, wsUrl: fullWsUrl });
    return fullWsUrl;
  }
}

export default ApiService; 