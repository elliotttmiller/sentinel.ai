// File: static/js/unified-realtime.js

// Unified Real-time System for Sentinel Command Center
// This single script provides a central Alpine.js component to power all pages.

function sentinelApp() {
    return {
        // --- STATE ---
        // Holds all data for the UI, updated in real-time from a single source
        systemLogs: { overview: [], "8001": [], "8002": [] },
        agentActivity: [],
        missions: [],
        liveStreamEvents: [],
        agents: [], // For ai-agents.html
        
        // Data for settings.html
        settings: {
            aiModel: 'gemini-1.5-pro',
            logLevel: 'info',
            refreshInterval: 10,
            theme: 'dark',
            dataRetention: 30,
            notifications: { email: true, push: true, sound: false },
            security: { sessionTimeout: 30, rateLimit: 'medium', twoFactor: false, ipWhitelist: '' },
            performance: { maxMissions: 10, memoryLimit: 8, cpuThreads: 4, cacheSize: 1000 }
        },

        // --- UI & STATS ---
        systemLogsFilter: "overview",
        liveStreamStats: { totalEvents: 1247, activeAgents: 8, successRate: 96, lastUpdate: '2m ago' },
        observabilityData: { thinkingSessions: 156, toolCalls: 89, apiCalls: 234, memoryUsage: 67 },
        testAnalytics: { totalTests: 42, successRate: 94, avgDuration: 2.3, performance: 87 },
        
        // UI Control State
        autoRefresh: true,
        showEventModal: false,
        selectedEvent: null,
        showMissionModal: false,
        selectedMission: null,
        
        // Page-specific UI state
        newMission: { prompt: '', agent_type: 'developer', priority: 'medium' },

        // --- CORE ---
        eventSource: null,

        // --- INITIALIZATION ---
        init() {
            console.log("🚀 Sentinel Command Center Unified Controller Initializing...");
            this.startUnifiedEventStream();
            this.loadInitialData();
            // Lucide Icons
            lucide.createIcons();
        },

        async loadInitialData() {
            // This function can be expanded to load data for any page
            await this.loadMissions();
            this.loadAgents(); // For ai-agents page
            // await this.loadSettings(); // For settings page
        },

        // --- REAL-TIME SYSTEM (SSE) ---
        startUnifiedEventStream() {
            if (this.eventSource) this.eventSource.close();
            
            console.log("📡 Connecting to Unified Real-Time Event Stream...");
            this.eventSource = new EventSource('/api/events/stream');

            this.eventSource.onmessage = (event) => {
                try {
                    const eventData = JSON.parse(event.data);
                    this.dispatchEvent(eventData);
                } catch (e) {
                    console.error("Error parsing SSE event:", e, event.data);
                }
            };

            this.eventSource.onerror = () => {
                console.error("SSE connection error. Reconnecting in 5 seconds...");
                this.eventSource.close();
                setTimeout(() => this.startUnifiedEventStream(), 5000);
            };
        },

        // --- CENTRAL EVENT DISPATCHER ---
        dispatchEvent(event) {
            // Add every event to the main live stream feed for the dashboard
            this.liveStreamEvents.unshift(event);
            if (this.liveStreamEvents.length > 200) this.liveStreamEvents.pop();
            this.updateLiveStreamStats();

            // Route the event to specific handlers to update different parts of the state
            switch (event.event_type) {
                case 'system_log':
                    this.addSystemLog(event);
                    break;
                case 'agent_action':
                    this.agentActivity.unshift(event);
                    if (this.agentActivity.length > 100) this.agentActivity.pop();
                    break;
                case 'mission_start':
                case 'mission_update':
                case 'mission_complete':
                    this.updateMissionState(event);
                    break;
            }
        },

        // --- EVENT HANDLERS ---
        addSystemLog(event) {
            const logEntry = {
                timestamp: event.timestamp,
                level: event.severity,
                message: event.message,
                server: event.server_port || 'N/A',
                source: event.source
            };

            // Add to the overview list (all logs)
            this.systemLogs.overview.unshift(logEntry);
            if (this.systemLogs.overview.length > 500) this.systemLogs.overview.pop();

            // Add to the specific server list if it exists
            if (this.systemLogs[logEntry.server]) {
                this.systemLogs[logEntry.server].unshift(logEntry);
                if (this.systemLogs[logEntry.server].length > 250) this.systemLogs[logEntry.server].pop();
            }
        },

        updateMissionState(event) {
            const missionData = event.payload || {};
            const missionId = missionData.id;
            if (!missionId) return;

            const existingMissionIndex = this.missions.findIndex(m => m.id === missionId);

            if (existingMissionIndex > -1) {
                // Update existing mission by merging new data
                this.missions[existingMissionIndex] = { ...this.missions[existingMissionIndex], ...missionData };
            } else if (event.event_type === 'mission_start') {
                // Add new mission
                this.missions.unshift({
                    status: 'pending',
                    progress: 0,
                    ...missionData
                });
            }
        },
        
        updateLiveStreamStats() {
            const events = this.liveStreamEvents;
            this.liveStreamStats.totalEvents = events.length;
            this.liveStreamStats.activeAgents = new Set(events.filter(e => e.source && e.source.startsWith('agent_')).map(e => e.source)).size;
            const successEvents = events.filter(e => e.severity === 'INFO' || e.severity === 'SUCCESS').length;
            this.liveStreamStats.successRate = events.length > 0 ? Math.round((successEvents / events.length) * 100) : 0;
            this.liveStreamStats.lastUpdate = new Date().toLocaleTimeString();
        },

        // --- PAGE-SPECIFIC LOGIC ---

        // Dashboard Page Helpers
        getAverageResponseTime() { return (Math.random() * 2 + 0.1).toFixed(2); },
        getActiveAgentCount() { return this.liveStreamStats.activeAgents; },
        get recentActivity() {
            return this.liveStreamEvents.slice(0, 5).map(event => ({
                id: event.event_id || Math.random(),
                message: event.message || `Event: ${event.event_type}`,
                time: this.formatTimestamp(event.timestamp),
                icon: this.getEventIcon(event.event_type)
            }));
        },

        // Missions Page Helpers
        async loadMissions() {
            try {
                const response = await fetch('/api/missions');
                if (response.ok) {
                    const data = await response.json();
                    if (data.success) this.missions = data.missions;
                }
            } catch (e) { console.error("Failed to load missions:", e); }
        },
        async createMission() {
            console.log("Creating mission:", this.newMission);
            // This would call the backend API
            this.showNotification('Mission creation request sent!', 'success');
            // Mock adding it to the list
            this.missions.unshift({
                id: `mission_${Date.now()}`,
                prompt: this.newMission.prompt,
                agent_type: this.newMission.agent_type,
                priority: this.newMission.priority,
                status: 'pending',
                progress: 0,
                created_at: new Date().toISOString()
            });
            this.newMission = { prompt: '', agent_type: 'developer', priority: 'medium' };
        },
        clearCompletedMissions() { this.missions = this.missions.filter(m => m.status !== 'completed'); },
        refreshMissions() { this.loadMissions(); },
        openMissionModal(mission) { 
            this.selectedMission = mission; 
            this.showMissionModal = true; 
        },
        closeMissionModal() { 
            this.showMissionModal = false; 
            this.selectedMission = null; 
        },
        pauseMission(id) { console.log("Pausing mission:", id); /* Add API call here */ },
        cancelMission(id) { console.log("Canceling mission:", id); /* Add API call here */ },

        // AI Agents Page Helpers
        loadAgents() {
            this.agents = [
                { id: 1, name: 'Code Reviewer', type: 'code_reviewer', status: 'active', performance: 95, missions_completed: 42, last_active: '2m ago' },
                { id: 2, name: 'Data Analyzer', type: 'data_analyzer', status: 'active', performance: 88, missions_completed: 28, last_active: '5m ago' },
                { id: 3, name: 'System Monitor', type: 'system_monitor', status: 'idle', performance: 92, missions_completed: 156, last_active: '1h ago' }
            ];
        },

        // Settings Page Helpers
        async saveSettings() {
             console.log("Saving settings:", this.settings);
             this.showNotification('Settings saved successfully!', 'success');
        },
        async resetSettings() {
            if (confirm('Reset settings to defaults?')) {
                // Re-fetch default settings or reset manually
                this.showNotification('Settings have been reset.', 'info');
            }
        },

        // --- UI & FORMATTING HELPERS (GLOBAL) ---
        changeSystemLogsFilter(filter) { this.systemLogsFilter = filter; },
        getFilteredSystemLogs() { return this.systemLogs[this.systemLogsFilter] || []; },
        formatTimestamp(dateString) { return dateString ? new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : 'N/A'; },
        formatDate(dateString) { return dateString ? new Date(dateString).toLocaleString() : 'N/A'; },
        formatEventType(eventType) { return eventType ? eventType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'Unknown Event'; },
        formatDetailKey(key) { return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()); },
        formatDetailValue(value) {
            if (typeof value === 'object' && value !== null) return JSON.stringify(value, null, 2);
            return String(value);
        },
        getEventIcon(eventType) {
            const icons = {
                'system_log': 'fa-info-circle', 'agent_action': 'fa-robot', 'mission_start': 'fa-rocket',
                'mission_complete': 'fa-check-circle', 'mission_update': 'fa-tasks', 'system_error': 'fa-exclamation-triangle',
                'test_start': 'fa-vial', 'test_complete': 'fa-check-double'
            };
            return icons[eventType] || 'fa-question-circle';
        },
        getStatusClass(status) {
            switch(status) {
                case 'running': return 'running';
                case 'paused': return 'paused';
                case 'completed': return 'completed';
                case 'failed': return 'failed';
                case 'pending': return 'pending';
                default: return 'pending';
            }
        },
        getPriorityClass(priority) {
            const classes = { 'critical': 'badge-danger', 'high': 'badge-warning', 'medium': 'badge-info', 'low': 'badge-secondary' };
            return classes[priority] || 'badge-secondary';
        },
        getProgress(mission) { return mission.progress || (mission.status === 'completed' ? 100 : 0); },
        openEventModal(event) { this.selectedEvent = event; this.showEventModal = true; },
        closeEventModal() { this.showEventModal = false; this.selectedEvent = null; },
        toggleAutoRefresh() { this.autoRefresh = !this.autoRefresh; },
        showNotification(message, type = 'info') {
            // A simple, non-blocking notification implementation
            const alert = document.createElement('div');
            alert.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
            alert.style.cssText = `position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 300px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);`;
            alert.innerHTML = `${message}<button type="button" class="close" data-dismiss="alert"><span>×</span></button>`;
            document.body.appendChild(alert);
            setTimeout(() => alert.remove(), 5000);
        },

        // Cleanup
        destroy() {
            if (this.eventSource) this.eventSource.close();
        }
    };
} 