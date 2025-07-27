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

// Enhanced debug logging
const debugLog = (message: string, data?: any) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] DEBUG: ${message}`, data ? JSON.stringify(data, null, 2) : '');
};

// Get environment variables with fallbacks
const getEnvVar = (key: string, fallback: string) => {
  const value = Constants.expoConfig?.extra?.[key] || fallback;
  debugLog(`Environment variable ${key}:`, { value, fallback });
  return value;
};

const defaultConfig: ApiConfig = {
  railwayUrl: getEnvVar('railwayUrl', 'http://localhost:8080'),
  ngrokUrl: getEnvVar('ngrokUrl', 'https://thrush-real-lacewing.ngrok-free.app'),
  websocketUrl: getEnvVar('websocketUrl', 'ws://localhost:8080/ws'),
  useNgrok: false, // Start with local backend
};

debugLog('Initial configuration:', defaultConfig);

export const ApiProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [config, setConfig] = useState<ApiConfig>(defaultConfig);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);

  const baseUrl = config.useNgrok ? config.ngrokUrl : config.railwayUrl;

  debugLog('Current configuration state:', {
    config,
    baseUrl,
    isConnected,
    connectionError
  });

  const testConnection = async (url: string) => {
    const startTime = Date.now();
    debugLog(`Starting connection test to: ${url}`);
    
    try {
      debugLog(`Making fetch request to: ${url}/health`);
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);
      
      const response = await fetch(`${url}/health`, {
        method: 'GET',
        signal: controller.signal,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        }
      });
      
      clearTimeout(timeoutId);
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      debugLog(`Connection test completed:`, {
        url: `${url}/health`,
        status: response.status,
        statusText: response.statusText,
        duration: `${duration}ms`,
        headers: Object.fromEntries(response.headers.entries())
      });

      if (response.ok) {
        try {
          const responseText = await response.text();
          debugLog(`Response body:`, responseText);
        } catch (e) {
          debugLog(`Could not read response body:`, e);
        }
      }

      return response.ok;
    } catch (error: any) {
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      debugLog(`Connection test failed:`, {
        url: `${url}/health`,
        error: error.message,
        errorType: error.constructor.name,
        duration: `${duration}ms`,
        stack: error.stack
      });

      if (error.name === 'AbortError') {
        debugLog('Connection timed out after 10 seconds');
      } else if (error.message.includes('Network request failed')) {
        debugLog('Network request failed - possible causes:');
        debugLog('- Server not running');
        debugLog('- Wrong port number');
        debugLog('- Firewall blocking connection');
        debugLog('- CORS issues');
      } else if (error.message.includes('fetch')) {
        debugLog('Fetch error - possible causes:');
        debugLog('- Invalid URL format');
        debugLog('- DNS resolution failed');
        debugLog('- SSL/TLS issues');
      }

      return false;
    }
  };

  const switchToNgrok = () => {
    debugLog('Switching to ngrok URL');
    setConfig(prev => ({ ...prev, useNgrok: true }));
  };

  const switchToRailway = () => {
    debugLog('Switching to Railway URL');
    setConfig(prev => ({ ...prev, useNgrok: false }));
  };

  useEffect(() => {
    debugLog('Configuration changed, checking connection...');
    debugLog('Current config:', config);
    debugLog('Base URL:', baseUrl);
    
    const checkConnection = async () => {
      debugLog(`Starting connection check with baseUrl: ${baseUrl}`);
      const connected = await testConnection(baseUrl);
      
      debugLog(`Connection result:`, {
        connected,
        baseUrl,
        useNgrok: config.useNgrok
      });
      
      setIsConnected(connected);
      setConnectionError(connected ? null : `Failed to connect to ${baseUrl}`);
    };

    checkConnection();
  }, [baseUrl, config]);

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

  debugLog('ApiContext value:', value);

  return <ApiContext.Provider value={value}>{children}</ApiContext.Provider>;
};

export const useApi = () => {
  const context = useContext(ApiContext);
  if (context === undefined) {
    throw new Error('useApi must be used within an ApiProvider');
  }
  return context;
}; 