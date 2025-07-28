import React, { createContext, useContext, useState, useEffect } from 'react';
import Constants from 'expo-constants';
import { ApiConfig } from '@/types';

interface ApiContextType {
  config: ApiConfig;
  baseUrl: string;
  isConnected: boolean;
  connectionError: string | null;
}

const CONFIG_URL = 'https://thrush-real-lacewing.ngrok-free.app/static/sentinel-config.json'; // Updated to /static path
const DEFAULT_API_URL = 'https://thrush-real-lacewing.ngrok-free.app'; // fallback if config fetch fails

export const ApiContext = createContext<any>(null);

// Enhanced debug logging
const debugLog = (message: string, data?: any) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] DEBUG: ${message}`, data ? JSON.stringify(data, null, 2) : '');
};

// Get the API URL from environment
const getApiUrl = () => {
  const apiUrl = Constants.expoConfig?.extra?.apiUrl || 'https://sentinalai-production.up.railway.app';
  debugLog(`API URL from environment:`, { apiUrl });
  return apiUrl;
};

const defaultConfig: ApiConfig = {
  apiUrl: getApiUrl(),
};

debugLog('Initial configuration:', defaultConfig);

export const ApiProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [config, setConfig] = useState<{ apiUrl: string } | null>(null);
  const [baseUrl, setBaseUrl] = useState<string>('');
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);

  // Auto-fetch config on startup
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const res = await fetch(CONFIG_URL);
        if (!res.ok) throw new Error('Config not found');
        const data = await res.json();
        if (!data.apiUrl) throw new Error('Invalid config');
        setConfig(data);
        setBaseUrl(data.apiUrl);
      } catch (e) {
        setConnectionError('Failed to fetch API config. Using default URL.');
        setBaseUrl(DEFAULT_API_URL);
      }
    };
    fetchConfig();
  }, []);

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

  useEffect(() => {
    debugLog('Configuration changed, checking connection...');
    debugLog('Current config:', config);
    debugLog('Base URL:', baseUrl);
    
    const checkConnection = async () => {
      debugLog(`Starting connection check with baseUrl: ${baseUrl}`);
      const connected = await testConnection(baseUrl);
      
      debugLog(`Connection result:`, {
        connected,
        baseUrl
      });
      
      setIsConnected(connected);
      setConnectionError(connected ? null : `Failed to connect to ${baseUrl}`);
    };

    checkConnection();
  }, [baseUrl, config]);

  const value: ApiContextType = {
    config,
    baseUrl,
    isConnected,
    connectionError,
  };

  debugLog('ApiContext value:', value);

  return (
    <ApiContext.Provider value={{ config, baseUrl, isConnected, connectionError }}>
      {children}
    </ApiContext.Provider>
  );
};

export const useApi = () => {
  const context = useContext(ApiContext);
  if (context === undefined) {
    throw new Error('useApi must be used within an ApiProvider');
  }
  return context;
}; 