import React, { createContext, useContext, useReducer } from "react";

const initialState = {
  systemLogs: { overview: [], "8001": [], "8002": [] },
  agentActivity: [],
  missions: [],
  liveStreamEvents: [],
  agents: [],
  optimizationProposals: [],
  systemLogsFilter: "overview",
  liveStreamStats: { totalEvents: 0, activeAgents: 0, successRate: 0, lastUpdate: "Never" },
  preflightCheckResult: null,
  isCheckingPrompt: false,
  analyticsSummary: { missions: {}, performance: {} },
  performanceChart: null,
  liveStreamActive: false,
  showEventModal: false,
  selectedEvent: null,
  selectedMission: null,
  showMissionModal: false,
  activeEvent: null,
  showAllEvents: false,
  newMission: { prompt: '', agent_type: 'developer', priority: 'medium' },
  healingMissions: [],
  newTestMission: { prompt: '', test_type: 'unit', priority: 'low' },
  testStreamEvents: [],
};

function reducer(state, action) {
  switch (action.type) {
    case "SET_MISSIONS":
      return { ...state, missions: action.missions };
    case "SET_AGENT_ACTIVITY":
      return { ...state, agentActivity: action.agentActivity };
    case "SET_SYSTEM_LOGS":
      return { ...state, systemLogs: action.systemLogs };
    case "OPEN_MISSION_MODAL":
      return { ...state, showMissionModal: true, selectedMission: action.mission };
    case "CLOSE_MISSION_MODAL":
      return { ...state, showMissionModal: false, selectedMission: null };
    case "OPEN_EVENT_MODAL":
      return { ...state, showEventModal: true, selectedEvent: action.event };
    case "CLOSE_EVENT_MODAL":
      return { ...state, showEventModal: false, selectedEvent: null };
    default:
      return state;
  }
}

const SentinelContext = createContext();

export function SentinelProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  return (
    <SentinelContext.Provider value={{ state, dispatch }}>
      {children}
    </SentinelContext.Provider>
  );
}

export function useSentinel() {
  return useContext(SentinelContext);
}
