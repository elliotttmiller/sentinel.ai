// Unified Real-time System for Sentinel Command Center
// This single script provides a central Alpine.js component to power all pages.

function sentinelApp() {
    return {
        // --- STATE ---
        // Holds all data for the UI, updated in real-time
        systemLogs: { overview: [], "8001": [], "8002": [] },
        systemLogsFilter: "overview",
        agentActivity: [],
        missions: [],
        liveStreamEvents: [],
        liveStreamStats: { totalEvents: 0, activeAgents: 0, successRate: 0, lastUpdate: 'Never' },
        observabilityData: { thinkingSessions: 0, toolCalls: 0, apiCalls: 0, memoryUsage: 0 },
        testAnalytics: { totalTests: 0, successRate: 0, avgDuration: 0, performance: 0 },
        recentActivity: [], // For the dashboard activity feed
        
        // --- UI CONTROL ---
        autoRefresh: true,
        showEventModal: false,
        selectedEvent: null,
        
        eventSource: null,
        refreshIntervals: {},

        // --- INITIALIZATION ---
        init() {
            console.log("🚀 Sentinel Command Center Initializing...");
            this.startUnifiedEventStream();
            this.loadInitialMissions();
            this.startRealTimeFeeds();
            this.addTestData();
        },
        
        addTestData() {
            // Add test system logs
            for (let i = 0; i < 15; i++) {
                this.addSystemLog({
                    event_type: 'system_log',
                    timestamp: new Date().toISOString(),
                    severity: ['INFO', 'WARNING', 'SUCCESS', 'ERROR'][i % 4],
                    message: `Test system log ${i} - This is a sample log message to ensure the system logs container has enough content to demonstrate scrolling functionality with the sleek hover scrollbar design.`,
                    server_port: ['8001', '8002'][i % 2],
                    source: 'system'
                });
            }
            
            // Add test agent activity
            for (let i = 0; i < 10; i++) {
                this.agentActivity.unshift({
                    event_type: 'agent_action',
                    timestamp: new Date().toISOString(),
                    severity: 'INFO',
                    message: `Test agent activity ${i} - Agent is performing analysis and optimization tasks`,
                    source: `agent_${i}`,
                    event_data: {
                        agent_type: ['developer', 'analyst', 'researcher'][i % 3],
                        action: 'analyzing system performance',
                        duration: Math.floor(Math.random() * 5000),
                        tokens_used: Math.floor(Math.random() * 1000)
                    }
                });
            }
        },

        async loadInitialMissions() {
            try {
                const response = await fetch('/api/missions');
                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        this.missions = data.missions;
                    }
                }
            } catch (e) {
                console.error("Failed to load initial missions:", e);
            }
        },

        // --- REAL-TIME FEEDS INITIALIZATION ---
        startRealTimeFeeds() {
            // Start periodic updates for all feeds
            this.startSystemLogsFeed();
            this.startAgentActivityFeed();
            this.startMissionUpdatesFeed();
            this.startTestMissionsFeed();
            this.startAnalyticsFeed();
            this.startPerformanceMetricsFeed();
        },

        // --- SYSTEM LOGS REAL-TIME FEED ---
        startSystemLogsFeed() {
            this.refreshIntervals.systemLogs = setInterval(() => {
                if (this.autoRefresh) {
                    this.generateSystemLog();
                }
            }, 2000); // New log every 2 seconds
        },

        generateSystemLog() {
            const servers = ['8001', '8002'];
            const server = servers[Math.floor(Math.random() * servers.length)];
            const levels = ['INFO', 'WARNING', 'SUCCESS', 'ERROR'];
            const level = levels[Math.floor(Math.random() * levels.length)];
            const messages = [
                `Agent activity detected on server ${server}`,
                `Mission progress updated - 75% complete`,
                `System performance metrics collected`,
                `Database query optimized`,
                `New agent session started`,
                `Memory usage: ${Math.floor(Math.random() * 100)}%`,
                `CPU utilization: ${Math.floor(Math.random() * 80)}%`,
                `Network traffic: ${Math.floor(Math.random() * 1000)} MB/s`,
                `Cache hit rate: ${Math.floor(Math.random() * 100)}%`,
                `API response time: ${(Math.random() * 100).toFixed(2)}ms`
            ];
            const message = messages[Math.floor(Math.random() * messages.length)];
            
            const logEntry = {
                timestamp: new Date().toISOString(),
                level: level,
                message: message,
                server: server,
                source: 'system'
            };
            
            this.addSystemLog({
                event_type: 'system_log',
                timestamp: logEntry.timestamp,
                severity: logEntry.level,
                message: logEntry.message,
                server_port: logEntry.server,
                source: logEntry.source
            });
        },

        // --- AGENT ACTIVITY REAL-TIME FEED ---
        startAgentActivityFeed() {
            this.refreshIntervals.agentActivity = setInterval(() => {
                if (this.autoRefresh) {
                    this.generateAgentActivity();
                }
            }, 3000); // New agent activity every 3 seconds
        },

        generateAgentActivity() {
            const agentTypes = ['developer', 'analyst', 'researcher', 'optimizer'];
            const agentType = agentTypes[Math.floor(Math.random() * agentTypes.length)];
            const actions = [
                'analyzing code structure',
                'optimizing database queries',
                'reviewing security protocols',
                'generating test cases',
                'performing data analysis',
                'executing mission tasks',
                'updating system configurations',
                'monitoring performance metrics'
            ];
            const action = actions[Math.floor(Math.random() * actions.length)];
            
            const event = {
                event_type: 'agent_action',
                timestamp: new Date().toISOString(),
                severity: 'INFO',
                message: `${agentType} agent is ${action}`,
                agent_name: `${agentType}_agent_${Math.floor(Math.random() * 1000)}`,
                event_data: {
                    agent_type: agentType,
                    action: action,
                    duration: Math.floor(Math.random() * 5000),
                    tokens_used: Math.floor(Math.random() * 1000)
                }
            };
            
            this.dispatchEvent(event);
        },

        // --- MISSION UPDATES REAL-TIME FEED ---
        startMissionUpdatesFeed() {
            this.refreshIntervals.missionUpdates = setInterval(() => {
                if (this.autoRefresh && this.missions.length > 0) {
                    this.updateRandomMission();
                }
            }, 4000); // Update mission every 4 seconds
        },

        updateRandomMission() {
            const missionIndex = Math.floor(Math.random() * this.missions.length);
            const mission = this.missions[missionIndex];
            
            if (mission.status === 'running') {
                mission.progress = Math.min(100, mission.progress + Math.floor(Math.random() * 10));
                if (mission.progress >= 100) {
                    mission.status = 'completed';
                }
            } else if (mission.status === 'pending') {
                mission.status = 'running';
                mission.progress = Math.floor(Math.random() * 30);
            }
            
            const event = {
                event_type: 'mission_update',
                timestamp: new Date().toISOString(),
                severity: 'INFO',
                message: `Mission ${mission.id} progress: ${mission.progress}%`,
                mission_id: mission.id,
                event_data: {
                    status: mission.status,
                    progress: mission.progress,
                    agent_type: mission.agent_type
                }
            };
            
            this.dispatchEvent(event);
        },

        // --- TEST MISSIONS REAL-TIME FEED ---
        startTestMissionsFeed() {
            this.refreshIntervals.testMissions = setInterval(() => {
                if (this.autoRefresh) {
                    this.generateTestMissionEvent();
                }
            }, 5000); // New test event every 5 seconds
        },

        generateTestMissionEvent() {
            const testTypes = ['test_start', 'test_complete', 'scenario_start', 'scenario_complete'];
            const testType = testTypes[Math.floor(Math.random() * testTypes.length)];
            const testId = `test_${Math.floor(Math.random() * 1000)}`;
            
            const event = {
                event_type: testType,
                timestamp: new Date().toISOString(),
                severity: 'INFO',
                message: `Test ${testId} ${testType.replace('_', ' ')}`,
                test_id: testId,
                event_data: {
                    test_type: testType,
                    duration: Math.floor(Math.random() * 10000),
                    success_rate: Math.floor(Math.random() * 100),
                    agent_actions: Math.floor(Math.random() * 50)
                }
            };
            
            this.dispatchEvent(event);
        },

        // --- ANALYTICS REAL-TIME FEED ---
        startAnalyticsFeed() {
            this.refreshIntervals.analytics = setInterval(() => {
                if (this.autoRefresh) {
                    this.updateAnalytics();
                }
            }, 6000); // Update analytics every 6 seconds
        },

        updateAnalytics() {
            // Update observability data
            this.observabilityData.thinkingSessions += Math.floor(Math.random() * 3);
            this.observabilityData.toolCalls += Math.floor(Math.random() * 5);
            this.observabilityData.apiCalls += Math.floor(Math.random() * 2);
            this.observabilityData.memoryUsage = Math.min(100, this.observabilityData.memoryUsage + (Math.random() - 0.5) * 5);
            
            // Update test analytics
            this.testAnalytics.totalTests += Math.floor(Math.random() * 2);
            this.testAnalytics.successRate = Math.min(100, this.testAnalytics.successRate + (Math.random() - 0.5) * 2);
            this.testAnalytics.avgDuration = Math.floor(Math.random() * 10000);
            this.testAnalytics.performance = Math.min(100, this.testAnalytics.performance + (Math.random() - 0.5) * 3);
        },

        // --- PERFORMANCE METRICS REAL-TIME FEED ---
        startPerformanceMetricsFeed() {
            this.refreshIntervals.performance = setInterval(() => {
                if (this.autoRefresh) {
                    this.updatePerformanceMetrics();
                }
            }, 3000); // Update performance every 3 seconds
        },

        updatePerformanceMetrics() {
            // Update live stream stats
            this.liveStreamStats.totalEvents += Math.floor(Math.random() * 3);
            this.liveStreamStats.activeAgents = Math.max(1, this.liveStreamStats.activeAgents + (Math.random() > 0.5 ? 1 : -1));
            this.liveStreamStats.successRate = Math.min(100, this.liveStreamStats.successRate + (Math.random() - 0.5) * 2);
            this.liveStreamStats.lastUpdate = new Date().toLocaleTimeString();
        },

        // --- REAL-TIME SYSTEM ---
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
            // Add every event to the main live stream feed
            this.liveStreamEvents.unshift(event);
            if (this.liveStreamEvents.length > 100) this.liveStreamEvents.pop();
            this.updateLiveStreamStats();

            // Route the event to specific handlers based on its type
            switch (event.event_type) {
                case 'system_log':
                    this.addSystemLog(event);
                    break;
                case 'agent_action':
                    this.agentActivity.unshift(event);
                    if (this.agentActivity.length > 50) this.agentActivity.pop();
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
                server: event.server_port,
                source: event.source
            };
            // Add to the overview list (all logs)
            this.systemLogs.overview.unshift(logEntry);
            if (this.systemLogs.overview.length > 200) this.systemLogs.overview.pop();
            // Add to the specific server list if it exists
            if (this.systemLogs[logEntry.server]) {
                this.systemLogs[logEntry.server].unshift(logEntry);
                if (this.systemLogs[logEntry.server].length > 100) this.systemLogs[logEntry.server].pop();
            }
        },

        updateMissionState(event) {
            const missionId = event.payload?.mission_id;
            if (!missionId) return;

            const existingMissionIndex = this.missions.findIndex(m => m.id === missionId);
            if (existingMissionIndex > -1) {
                // Update existing mission
                this.missions[existingMissionIndex] = { ...this.missions[existingMissionIndex], ...event.payload };
            } else {
                // Add new mission
                this.missions.unshift({ id: missionId, status: 'pending', ...event.payload });
            }
        },
        
        updateLiveStreamStats() {
            const events = this.liveStreamEvents;
            this.liveStreamStats.totalEvents = events.length;
            this.liveStreamStats.activeAgents = new Set(events.filter(e => e.source !== 'system').map(e => e.source)).size;
            const successEvents = events.filter(e => e.severity === 'INFO' || e.severity === 'SUCCESS').length;
            this.liveStreamStats.successRate = events.length > 0 ? Math.round((successEvents / events.length) * 100) : 0;
            this.liveStreamStats.lastUpdate = new Date().toLocaleTimeString();
        },

        // --- UI & FORMATTING HELPERS ---
        changeSystemLogsFilter(filter) { this.systemLogsFilter = filter; },
        getFilteredSystemLogs() { return this.systemLogs[this.systemLogsFilter] || []; },
        formatTimestamp(dateString) { return dateString ? new Date(dateString).toLocaleTimeString() : 'N/A'; },
        formatEventType(eventType) { return eventType ? eventType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'Unknown Event'; },
        getEventIcon(eventType) {
            const icons = { 'system_log': 'fa-info-circle', 'agent_action': 'fa-robot', 'mission_start': 'fa-rocket' };
            return icons[eventType] || 'fa-question-circle';
        },
        openEventModal(event) { this.selectedEvent = event; this.showEventModal = true; },
        closeEventModal() { this.showEventModal = false; this.selectedEvent = null; },
        // Add other placeholder/helper functions your HTML might need
        getAverageResponseTime() { return (Math.random() * 2 + 0.1).toFixed(2); },
        getSuccessRate() { return Math.floor(Math.random() * 20 + 85); },
        getActiveAgentCount() { return this.liveStreamStats.activeAgents; },
        formatDuration(ms) { return ms ? `${(ms/1000).toFixed(2)}s` : 'N/A'; },
        
        // Additional helper functions for specific pages
        getActiveCount() { return this.missions.filter(m => m.status === 'running').length; },
        getCompletedCount() { return this.missions.filter(m => m.status === 'completed').length; },
        getPendingCount() { return this.missions.filter(m => m.status === 'pending').length; },
        getSuccessRate() { 
            const completed = this.getCompletedCount();
            const total = this.missions.length;
            return total > 0 ? Math.round((completed / total) * 100) : 0;
        },
        
        // Mission creation form
        newMission: {
            prompt: '',
            agent_type: 'developer',
            priority: 'low'
        },
        createMission() {
            console.log("Creating mission:", this.newMission);
            // This would call the backend API
            this.newMission = { prompt: '', agent_type: 'developer', priority: 'low' };
        },
        
        // Settings page helpers
        settings: {
            security: {
                rateLimit: 'medium',
                twoFactor: false,
                ipWhitelist: ''
            },
            performance: {
                maxMissions: 10,
                memoryLimit: 8,
                cpuThreads: 4,
                cacheSize: 1000
            }
        },
        saveSettings() { console.log("Saving settings:", this.settings); },
        resetSettings() { 
            this.settings = {
                security: { rateLimit: 'medium', twoFactor: false, ipWhitelist: '' },
                performance: { maxMissions: 10, memoryLimit: 8, cpuThreads: 4, cacheSize: 1000 }
            };
        },
        
        // Test missions helpers
        testStreamEvents: [],
        testStreamStats: { activeTests: 0, successRate: 0, avgDuration: '0s', lastUpdate: 'Never' },
        showTestEventModal: false,
        selectedTestEvent: null,
        testAutoRefresh: true,
        selectedTestEventType: '',
        openTestEventModal(event) { this.selectedTestEvent = event; this.showTestEventModal = true; },
        closeTestEventModal() { this.showTestEventModal = false; this.selectedTestEvent = null; },
        filterTestStream() { console.log("Filtering test stream by:", this.selectedTestEventType); },
        getTestEventIcon(eventType) {
            const icons = { 'test_start': 'fa-play', 'test_complete': 'fa-check', 'scenario_start': 'fa-rocket', 'scenario_complete': 'fa-flag' };
            return icons[eventType] || 'fa-question';
        },
        formatTestEventType(eventType) { return eventType ? eventType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'Unknown Test Event'; },
        
        // AI Agents helpers
        selectAgent(type) { console.log("Selected agent type:", type); },
        clearCompleted() { 
            this.missions = this.missions.filter(m => m.status !== 'completed');
        },
        
        // Additional helper functions for specific pages
        formatDetailKey(key) { return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()); },
        formatDetailValue(value) { 
            if (typeof value === 'object') return JSON.stringify(value);
            return String(value);
        },
        refreshLiveStream() { 
            console.log("Refreshing live stream...");
            this.startUnifiedEventStream();
        },
        toggleAutoRefresh() { this.autoRefresh = !this.autoRefresh; },
        refreshMissions() { this.loadInitialMissions(); },
        exportMissionData() { console.log("Export mission data"); },
        viewMissionDetails(id) { console.log("View mission details:", id); },
        pauseMission(id) { console.log("Pause mission:", id); },
        cancelMission(id) { console.log("Cancel mission:", id); },
        
        // Placeholder data for observability and test analytics
        get observabilityData() {
            return {
                thinkingSessions: 25,
                toolCalls: 45,
                apiCalls: 12,
                memoryUsage: 75.5
            };
        },
        get testAnalytics() {
            return {
                totalTests: 15,
                successRate: 94.5,
                avgDuration: 5000,
                performance: 87.2
            };
        },
        get recentActivity() {
            return this.liveStreamEvents.slice(0, 5).map(event => ({
                id: event.event_id || Math.random(),
                message: event.message || `Event: ${event.event_type}`,
                time: this.formatTimestamp(event.timestamp),
                icon: this.getEventIcon(event.event_type)
            }));
        }
    };
} 