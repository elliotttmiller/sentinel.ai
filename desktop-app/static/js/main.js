function sentinelApp() {
    return {
        // Data properties for UI
        systemLogs: {
            overview: [],
            "8001": [],
            "8002": []
        },
        systemLogsFilter: "overview",
        agentActivity: [],
        missions: [],
        observability: {
            metrics: {},
            analytics: {}
        },
        eventSource: null,

        // <<< ADDED: Missing properties for HTML template >>>
        liveStreamEvents: [],
        liveStreamStats: {
            totalEvents: 0,
            activeAgents: 0,
            successRate: 0,
            lastUpdate: 'Never'
        },
        observabilityData: {
            thinkingSessions: 0,
            toolCalls: 0,
            apiCalls: 0,
            memoryUsage: 0
        },
        testAnalytics: {
            totalTests: 0,
            successRate: 0,
            avgDuration: 0,
            performance: 0
        },
        recentActivity: [],
        autoRefresh: true,
        selectedEventType: "",
        showEventModal: false,
        selectedEvent: null,

        init() {
            console.log("🚀 Sentinel Command Center Initializing...");
            this.startUnifiedEventStream();
            this.loadInitialData();
        },

        async loadInitialData() {
            // Load initial data from API endpoints
            try {
                const response = await fetch('/api/missions');
                if (response.ok) {
                    this.missions = await response.json();
                }
            } catch (e) {
                console.error("Failed to load initial data:", e);
            }
        },

        startUnifiedEventStream() {
            if (this.eventSource) {
                this.eventSource.close();
            }
            console.log("📡 Connecting to Unified Real-Time Event Stream...");
            this.eventSource = new EventSource('/api/events/stream');

            this.eventSource.onmessage = (event) => {
                try {
                    const eventData = JSON.parse(event.data);
                    console.log("📨 Received event:", eventData.event_type, eventData.message);
                    this.dispatchEvent(eventData);
                } catch (e) {
                    console.error("Error parsing SSE event:", e);
                }
            };

            this.eventSource.onerror = () => {
                console.error("SSE connection error. Reconnecting in 5 seconds...");
                this.eventSource.close();
                setTimeout(() => this.startUnifiedEventStream(), 5000);
            };

            this.eventSource.onopen = () => {
                console.log("✅ SSE connection established successfully");
            };
        },

        // <<< NEW: Central Event Dispatcher >>> 
        dispatchEvent(event) {
            // A simple router to handle different event types from the unified stream
            switch (event.event_type) {
                case 'system_log':
                    this.addSystemLog(event);
                    break;
                case 'agent_action':
                    this.addAgentActivity(event);
                    break;
                case 'mission_start':
                    this.addMissionEvent(event);
                    break;
                case 'mission_complete':
                    this.addMissionEvent(event);
                    break;
                case 'agent_session_start':
                    this.addAgentSessionEvent(event);
                    break;
                case 'agent_session_complete':
                    this.addAgentSessionEvent(event);
                    break;
                case 'system_error':
                    this.addSystemError(event);
                    break;
                default:
                    // Add to live stream events
                    this.addLiveStreamEvent(event);
                    break;
            }
        },

        addSystemLog(event) {
            const logEntry = {
                timestamp: event.timestamp,
                level: event.severity,
                message: event.message,
                server: event.server_port,
                source: event.source
            };

            // Add to overview
            this.systemLogs.overview.unshift(logEntry);
            if (this.systemLogs.overview.length > 200) this.systemLogs.overview.pop();

            // Add to specific server log
            if (this.systemLogs[logEntry.server]) {
                this.systemLogs[logEntry.server].unshift(logEntry);
                if (this.systemLogs[logEntry.server].length > 100) {
                    this.systemLogs[logEntry.server].pop();
                }
            }

            // Update live stream
            this.addLiveStreamEvent(event);
        },

        addAgentActivity(event) {
            this.agentActivity.unshift(event);
            if (this.agentActivity.length > 200) this.agentActivity.pop();
            
            // Update live stream
            this.addLiveStreamEvent(event);
        },

        addMissionEvent(event) {
            // Update missions list
            const missionIndex = this.missions.findIndex(m => m.id === event.mission_id);
            if (missionIndex !== -1) {
                this.missions[missionIndex] = { ...this.missions[missionIndex], ...event.payload };
            } else if (event.event_type === 'mission_start') {
                this.missions.unshift({
                    id: event.mission_id,
                    prompt: event.message,
                    status: 'running',
                    created_at: event.timestamp,
                    progress: 0,
                    ...event.payload
                });
            }
            
            // Update live stream
            this.addLiveStreamEvent(event);
        },

        addAgentSessionEvent(event) {
            // Add to live stream
            this.addLiveStreamEvent(event);
        },

        addSystemError(event) {
            // Add to live stream
            this.addLiveStreamEvent(event);
        },

        // <<< ADDED: Live Stream Event Management >>>
        addLiveStreamEvent(event) {
            this.liveStreamEvents.unshift(event);
            if (this.liveStreamEvents.length > 100) this.liveStreamEvents.pop();
            
            // Update stats
            this.updateLiveStreamStats();
        },

        updateLiveStreamStats() {
            this.liveStreamStats.totalEvents = this.liveStreamEvents.length;
            this.liveStreamStats.activeAgents = this.agentActivity.filter(a => a.event_type === 'agent_action').length;
            this.liveStreamStats.successRate = this.liveStreamEvents.filter(e => e.severity !== 'error').length / Math.max(this.liveStreamEvents.length, 1) * 100;
            this.liveStreamStats.lastUpdate = new Date().toLocaleTimeString();
        },

        // <<< ADDED: UI Helper Functions >>>
        getAverageResponseTime() {
            return "0.5"; // Placeholder
        },

        getSuccessRate() {
            return 95.5; // Placeholder
        },

        getActiveAgentCount() {
            return this.agentActivity.filter(a => a.event_type === 'agent_action').length;
        },

        formatDuration(seconds) {
            if (!seconds) return "0s";
            return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
        },

        refreshLiveStream() {
            console.log("🔄 Refreshing live stream...");
            this.liveStreamEvents = [];
            this.updateLiveStreamStats();
        },

        toggleAutoRefresh() {
            this.autoRefresh = !this.autoRefresh;
            console.log("🔄 Auto refresh:", this.autoRefresh ? "enabled" : "disabled");
        },

        filterLiveStream() {
            console.log("🔍 Filtering live stream by:", this.selectedEventType);
        },

        openEventModal(event) {
            this.selectedEvent = event;
            this.showEventModal = true;
        },

        closeEventModal() {
            this.showEventModal = false;
            this.selectedEvent = null;
        },

        getEventIcon(eventType) {
            const icons = {
                'agent_action': 'fa-robot',
                'mission_start': 'fa-rocket',
                'mission_complete': 'fa-check-circle',
                'session_start': 'fa-play',
                'session_complete': 'fa-stop',
                'system_error': 'fa-exclamation-triangle',
                'system_log': 'fa-info-circle'
            };
            return icons[eventType] || 'fa-info-circle';
        },

        formatEventType(eventType) {
            return eventType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        },

        formatDetailKey(key) {
            return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        },

        formatDetailValue(value) {
            if (typeof value === 'boolean') return value ? 'Yes' : 'No';
            if (typeof value === 'number') return value.toString();
            return value || 'N/A';
        },

        refreshMissions() {
            console.log("🔄 Refreshing missions...");
            this.loadInitialData();
        },

        exportMissionData() {
            console.log("📤 Exporting mission data...");
        },

        clearCompletedMissions() {
            console.log("🗑️ Clearing completed missions...");
            this.missions = this.missions.filter(m => m.status !== 'completed');
        },

        viewMissionDetails(missionId) {
            console.log("👁️ Viewing mission details:", missionId);
        },

        pauseMission(missionId) {
            console.log("⏸️ Pausing mission:", missionId);
        },

        cancelMission(missionId) {
            console.log("❌ Canceling mission:", missionId);
        },

        formatTime(dateString) {
            if (!dateString) return 'N/A';
            return new Date(dateString).toLocaleTimeString();
        },

        formatTimestamp(dateString) {
            if (!dateString) return 'N/A';
            return new Date(dateString).toLocaleTimeString();
        },

        getEventClass(level) {
            const classes = {
                'info': 'text-info',
                'warning': 'text-warning',
                'error': 'text-danger',
                'critical': 'text-danger font-weight-bold'
            };
            return classes[level] || 'text-info';
        },

        changeSystemLogsFilter(filter) {
            this.systemLogsFilter = filter;
        },

        getFilteredSystemLogs() {
            return this.systemLogs[this.systemLogsFilter] || [];
        },

        destroy() {
            if (this.eventSource) {
                this.eventSource.close();
            }
        }
    };
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.sentinelApp = sentinelApp();
    window.sentinelApp.init();
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.sentinelApp) {
        window.sentinelApp.destroy();
    }
}); 