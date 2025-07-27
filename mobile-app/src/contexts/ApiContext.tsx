import React, { createContext, useContext, useState, useEffect } from 'react';
import Constants from 'expo-constants';
import { ApiConfig } from '@/types';

interface ApiContextType {
  config: ApiConfig;
  baseUrl: string;
  railwayUrl: string;
  ngrokUrl: string;
  websocketUrl: string;
  isConnected: boolean;
  connectionError: string | null;
  switchToNgrok: () => void;
  switchToRailway: () => void;
}

const ApiContext = createContext<ApiContextType | undefined>(undefined);

// Get environment variables with fallbacks
const getEnvVar = (key: string, fallback: string) => {
  return Constants.expoConfig?.extra?.[key] || fallback;
};

const defaultConfig: ApiConfig = {
  railwayUrl: getEnvVar('railwayUrl', 'http://localhost:8080'),
  ngrokUrl: getEnvVar('ngrokUrl', 'https://thrush-real-lacewing.ngrok-free.app'),
  websocketUrl: getEnvVar('websocketUrl', 'ws://localhost:8080/ws'),
  useNgrok: false, // Start with local backend
};

export const ApiProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [config, setConfig] = useState<ApiConfig>(defaultConfig);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);

  const baseUrl = config.useNgrok ? config.ngrokUrl : config.railwayUrl;

  const testConnection = async (url: string) => {
    try {
      console.log(`Testing connection to: ${url}`);
      const response = await fetch(`${url}/health`, {
        method: 'GET',
        timeout: 10000, // Increased timeout
      });
      console.log(`Connection response: ${response.status}`);
      return response.ok;
    } catch (error) {
      console.error('Connection test failed:', error);
      return false;
    }
  };

  const switchToNgrok = () => {
    setConfig(prev => ({ ...prev, useNgrok: true }));
  };

  const switchToRailway = () => {
    setConfig(prev => ({ ...prev, useNgrok: false }));
  };

  useEffect(() => {
    const checkConnection = async () => {
      const connected = await testConnection(baseUrl);
      setIsConnected(connected);
      setConnectionError(connected ? null : `Failed to connect to ${baseUrl}`);
    };

    checkConnection();
  }, [baseUrl]);

  const value: ApiContextType = {
    config,
    baseUrl,
    railwayUrl: config.railwayUrl,
    ngrokUrl: config.ngrokUrl,
    websocketUrl: config.websocketUrl,
    isConnected,
    connectionError,
    switchToNgrok,
    switchToRailway,
  };

  return <ApiContext.Provider value={value}>{children}</ApiContext.Provider>;
};

export const useApi = () => {
  const context = useContext(ApiContext);
  if (context === undefined) {
    throw new Error('useApi must be used within an ApiProvider');
  }
  return context;
}; 