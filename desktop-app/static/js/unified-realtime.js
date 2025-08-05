/**
 * Unified Real-Time Controller for Sentinel Command Center v5.4
 * Handles all real-time data streams and UI updates with Phase 5 features
 */

function sentinelApp() {
    return {
        // --- STATE ---
        systemLogs: { overview: [], "8001": [], "8002": [] },
        agentActivity: [],
        missions: [],
        liveStreamEvents: [],
        agents: [],
        optimizationProposals: [],
        
        // --- UI & STATS ---
        systemLogsFilter: "overview",
        liveStreamStats: { totalEvents: 0, activeAgents: 0, successRate: 0, lastUpdate: 'Never' },
        preflightCheckResult: null,
        isCheckingPrompt: false,
        analyticsSummary: { missions: {}, performance: {} },
        performanceChart: null,
        
        // UI Control State
        liveStreamActive: false, // NEW: Track live stream state
        showEventModal: false,
        selectedEvent: null,

        // --- Mission Page State ---
        selectedMission: null,
        showMissionModal: false,

        newMission: { prompt: '', agent_type: 'developer', priority: 'medium' },
        
        // Phase 4 State Properties
        healingMissions: [],
        
        // Test Mission State Properties
        newTestMission: {
            prompt: '',
            test_type: 'unit',
            priority: 'low'
        },
        testStreamEvents: [],

        eventSource: null, // Single event source for all server events

        // --- COMPUTED PROPERTIES ---
        get recentActivity() {
            return this.agentActivity.slice(0, 10);
        },
        
        get activeMissions() {
            return this.missions.filter(m => m.status === 'running' || m.status === 'healing');
        },
        
        get completedMissions() {
            return this.missions.filter(m => m.status === 'completed');
        },
        
        get failedMissions() {
            return this.missions.filter(m => m.status === 'failed');
        },

        // --- INITIALIZATION ---
        init() {
            console.log("🚀 Sentinel Command Center v5.4 Initializing (Sentience Active)...");
            console.log("Initial modal state:", this.showMissionModal);
            this.startUnifiedEventStream();
            this.loadInitialData();
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
            console.log("Component initialized successfully");
        },

        async loadInitialData() {
            await this.loadMissions();
            await this.loadAgents();
            await this.loadSystemLogs();
            
            const path = window.location.pathname;
            if (path.includes('settings')) {
                await this.loadOptimizationProposals();
            }
            if (path.includes('analytics')) {
                await this.loadAnalyticsSummary();
                await this.loadPerformanceChartData();
            }
        },

        // --- EVENT STREAM MANAGEMENT ---
        startUnifiedEventStream() {
            // Used for always-on event stream (not the live stream feed)
            console.log('🔌 Starting unified event stream...');
            this.eventSource = new EventSource('/api/events/stream');
            this.eventSource.onopen = () => {
                console.log('✅ Event stream connected successfully');
            };
            this.eventSource.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.dispatchEvent(data);
                } catch (e) {
                    console.error('❌ Failed to parse event:', e);
                }
            };
            this.eventSource.onerror = (error) => {
                console.error('❌ Event stream error:', error);
                setTimeout(() => this.startUnifiedEventStream(), 5000);
            };
        },


        // --- LIVE STREAM TOGGLE LOGIC (simplified) ---
        startLiveStream() {
            if (this.liveStreamActive) { return; }
            this.liveStreamActive = true;
            this.liveStreamEvents = []; // Clear previous events on start
            console.log('✅ Live stream feed activated. State:', this.liveStreamActive);
        },

        pauseLiveStream() {
            if (!this.liveStreamActive) { return; }
            this.liveStreamActive = false;
            console.log('⏸️ Live stream feed paused. State:', this.liveStreamActive);
        },

        toggleLiveStream() {
            console.log('🔘 toggleLiveStream called. Current state:', this.liveStreamActive);
            if (this.liveStreamActive) {
                this.pauseLiveStream();
            } else {
                this.startLiveStream();
            }
        },

        getLiveStreamButtonClass() {
            return this.liveStreamActive ? 'btn-danger' : 'btn-success';
        },

        getLiveStreamIconClass() {
            return this.liveStreamActive ? 'fa-stop' : 'fa-play';
        },

        dispatchEvent(event) {
            console.log('🔄 Dispatching event:', event.event_type);
            
            switch (event.event_type) {
                case 'mission_update':
                case 'mission_complete':
                case 'mission_error':
                    this.updateMissionState(event);
                    break;
                case 'mission_insight':
                    this.updateMissionInsight(event.payload);
                    break;
                case 'agent_action':
                    this.addAgentActivity(event);
                    break;
                case 'system_log':
                    this.addSystemLog(event);
                    break;
                case 'live_stream_event':
                    if (this.liveStreamActive) {
                        this.addLiveStreamEvent(event);
                    }
                    break;
                case 'heartbeat':
                    // Keep connection alive
                    break;
                default:
                    console.log('❓ Unhandled event type:', event.event_type, event);
            }
        },

        updateMissionInsight(insight) {
            const missionIndex = this.missions.findIndex(m => m.mission_id_str === insight.mission_id_str);
            if (missionIndex > -1) {
                // Merge new insight data into the existing mission object
                this.missions[missionIndex] = { ...this.missions[missionIndex], ...insight };
                
                // If the updated mission is the selected one, update selectedMission as well
                if (this.selectedMission?.mission_id_str === insight.mission_id_str) {
                    this.selectedMission = { ...this.selectedMission, ...insight };
                }
            }
        },

        // --- MISSION STATE MANAGEMENT ---
        updateMissionState(event) {
            const missionData = event.payload || {};
            const missionId = missionData.mission_id_str || missionData.id;
            if (!missionId) { return; }

            console.log('🔄 Updating mission state:', missionId, missionData);

            const existingMissionIndex = this.missions.findIndex(m => m.mission_id_str === missionId);

            if (existingMissionIndex > -1) {
                this.missions[existingMissionIndex] = { ...this.missions[existingMissionIndex], ...missionData };
                console.log('✅ Updated existing mission:', this.missions[existingMissionIndex]);
            } else {
                this.missions.unshift({ mission_id_str: missionId, ...missionData });
                console.log('➕ Added new mission:', this.missions[0]);
            }
            
            // Phase 4: Update healing missions list
            this.updateHealingMissions();
        },

        // --- AGENT ACTIVITY MANAGEMENT ---
        addAgentActivity(event) {
            const activity = {
                id: Date.now(),
                agent: event.source,
                action: event.message,
                timestamp: event.timestamp || new Date().toISOString(),
                severity: event.severity || 'INFO'
            };
            
            this.agentActivity.unshift(activity);
            
            // Keep only last 50 activities
            if (this.agentActivity.length > 50) {
                this.agentActivity = this.agentActivity.slice(0, 50);
            }
            
            console.log('🤖 Added agent activity:', activity);
        },

        // --- SYSTEM LOG MANAGEMENT ---
        addSystemLog(event) {
            const log = {
                id: Date.now(),
                timestamp: event.timestamp || new Date().toISOString(),
                level: event.severity || 'INFO',
                source: event.source || 'system',
                message: event.message || ''
            };
            
            // Add to overview logs
            this.systemLogs.overview.unshift(log);
            
            // Add to specific source logs if it exists
            if (event.source && this.systemLogs[event.source]) {
                this.systemLogs[event.source].unshift(log);
            }
            
            // Keep only last 100 logs in overview
            if (this.systemLogs.overview.length > 100) {
                this.systemLogs.overview = this.systemLogs.overview.slice(0, 100);
            }
            
            // Keep only last 50 logs in specific sources
            if (event.source && this.systemLogs[event.source] && this.systemLogs[event.source].length > 50) {
                this.systemLogs[event.source] = this.systemLogs[event.source].slice(0, 50);
            }
            
            console.log('📝 Added system log:', log);
        },

        // --- LIVE STREAM EVENT MANAGEMENT ---
        addLiveStreamEvent(event) {
            const streamEvent = {
                id: Date.now(),
                timestamp: event.timestamp || new Date().toISOString(),
                type: event.event_type,
                source: event.source,
                message: event.message,
                severity: event.severity || 'INFO'
            };
            
            this.liveStreamEvents.unshift(streamEvent);
            
            // Keep only last 100 events
            if (this.liveStreamEvents.length > 100) {
                this.liveStreamEvents = this.liveStreamEvents.slice(0, 100);
            }
            
            this.updateLiveStreamStats();
            console.log('📡 Added live stream event:', streamEvent);
        },

        updateLiveStreamStats() {
            this.liveStreamStats = {
                totalEvents: this.liveStreamEvents.length,
                activeAgents: this.agents.filter(a => a.status === 'active').length,
                successRate: this.calculateSuccessRate(),
                lastUpdate: new Date().toLocaleTimeString()
            };
        },

        calculateSuccessRate() {
            const completed = this.missions.filter(m => m.status === 'completed').length;
            const total = this.missions.length;
            return total > 0 ? Math.round((completed / total) * 100) : 0;
        },

        // --- DATA LOADING FUNCTIONS ---
        async loadMissions() {
            try {
                const response = await fetch('/api/missions');
                const data = await response.json();
                if (data.success) {
                    console.log('📋 Loaded missions:', data.missions);
                    this.missions = data.missions.map(mission => ({
                        ...mission,
                        mission_id_str: mission.mission_id_str || mission.id,
                        progress: mission.progress || 0,
                        status: mission.status || 'pending'
                    }));
                }
            } catch (e) {
                console.error('Failed to load missions:', e);
            }
        },

        async loadAgents() {
            try {
                const response = await fetch('/api/agents');
                const data = await response.json();
                if (data.success) {
                    this.agents = data.agents;
                }
            } catch (e) {
                console.error('Failed to load agents:', e);
            }
        },

        async loadSystemLogs() {
            try {
                const response = await fetch('/api/system/logs');
                const data = await response.json();
                if (data.success) {
                    this.systemLogs = data.logs;
                }
            } catch (e) {
                console.error('Failed to load system logs:', e);
            }
        },

        // --- PHASE 4: OPTIMIZATION PROPOSALS MANAGEMENT ---
        async loadOptimizationProposals() {
            try {
                const response = await fetch('/api/optimizations');
                const data = await response.json();
                if (data.success) {
                    this.optimizationProposals = data.proposals;
                }
            } catch (e) {
                console.error('Failed to load optimization proposals:', e);
            }
        },

        async applyProposal(proposalId) {
            try {
                const response = await fetch(`/api/optimizations/${proposalId}/apply`, {
                    method: 'POST'
                });
                const data = await response.json();
                if (data.success) {
                    this.showNotification('Proposal approved and applied!', 'success');
                    this.optimizationProposals = this.optimizationProposals.filter(p => p.id !== proposalId);
                }
            } catch (e) {
                console.error('Failed to apply proposal:', e);
                this.showNotification('Failed to apply proposal', 'error');
            }
        },

        async rejectProposal(proposalId) {
            try {
                const response = await fetch(`/api/optimizations/${proposalId}/reject`, {
                    method: 'POST'
                });
                const data = await response.json();
                if (data.success) {
                    this.showNotification('Proposal rejected.', 'info');
                    this.optimizationProposals = this.optimizationProposals.filter(p => p.id !== proposalId);
                }
            } catch (e) {
                console.error('Failed to reject proposal:', e);
                this.showNotification('Failed to reject proposal', 'error');
            }
        },

        // --- PHASE 5: PRE-FLIGHT CHECK LOGIC ---
        runPreFlightCheck: _.debounce(async function() {
            if (!this.newMission.prompt || this.newMission.prompt.length < 10) {
                this.preflightCheckResult = null;
                return;
            }
            
            this.isCheckingPrompt = true;
            try {
                const response = await fetch('/api/missions/pre-flight-check', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: this.newMission.prompt })
                });
                this.preflightCheckResult = await response.json();
            } catch (e) {
                console.error('Pre-flight check failed:', e);
                this.preflightCheckResult = { 
                    go_no_go: false, 
                    feedback: "Error connecting to Guardian Protocol.",
                    clarity_score: 0.0,
                    risk_score: 0.0,
                    suggestions: ["Please try again"]
                };
            } finally {
                this.isCheckingPrompt = false;
            }
        }, 500), // Debounce for 500ms

        // --- PHASE 5: ANALYTICS LOGIC ---
        async loadAnalyticsSummary() {
            try {
                const response = await fetch('/api/analytics/summary');
                const data = await response.json();
                if (data.success) {
                    this.analyticsSummary = data.summary;
                }
            } catch (e) {
                console.error('Failed to load analytics summary:', e);
            }
        },

        async loadPerformanceChartData() {
            try {
                const response = await fetch('/api/analytics/performance-over-time');
                const data = await response.json();
                if (data.success) {
                    this.renderPerformanceChart(data.data);
                }
            } catch (e) {
                console.error('Failed to load performance data:', e);
            }
        },

        renderPerformanceChart(data) {
            const ctx = document.getElementById('performanceChart');
            if (!ctx) return;

            const labels = data.map(d => d.date);
            const successData = data.map(d => d.successful);
            const totalData = data.map(d => d.total);

            if (this.performanceChart) {
                this.performanceChart.destroy();
            }
            
            this.performanceChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Successful Missions',
                            data: successData,
                            backgroundColor: 'rgba(76, 175, 80, 0.6)',
                            borderColor: 'rgba(76, 175, 80, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Total Missions',
                            data: totalData,
                            backgroundColor: 'rgba(74, 144, 226, 0.6)',
                            borderColor: 'rgba(74, 144, 226, 1)',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true, ticks: { color: '#fff' } },
                        x: { ticks: { color: '#fff' } }
                    },
                    plugins: { legend: { labels: { color: '#fff' } } }
                }
            });
        },

        // --- MISSION CREATION ---
        async createMission() {
            if (!this.newMission.prompt.trim()) {
                this.showNotification('Please enter a mission prompt', 'warning');
                return;
            }

            // Check if pre-flight check passed
            if (this.preflightCheckResult && !this.preflightCheckResult.go_no_go) {
                this.showNotification('Mission blocked by Guardian Protocol. Please review the feedback.', 'warning');
                return;
            }

            try {
                const response = await fetch('/api/missions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.newMission)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                if (data.success) {
                    this.showNotification(`Mission ${data.mission.mission_id_str} successfully created!`, 'success');
                    this.newMission = { prompt: '', agent_type: 'developer', priority: 'medium' };
                    this.preflightCheckResult = null; // Clear pre-flight result
                }
            } catch (e) {
                console.error('Mission creation failed:', e);
                this.showNotification(e.message, 'error');
            }
        },

        // --- PHASE 4: HEALING MISSIONS MANAGEMENT ---
        updateHealingMissions() {
            this.healingMissions = this.missions.filter(m => m.status === 'healing');
        },

        // --- UI HELPERS ---
        getStatusClass(status) {
            const classes = { 
                'completed': 'online', 
                'running': 'warning', 
                'pending': 'offline', 
                'failed': 'offline', 
                'healing': 'info' // NEW: Healing status
            };
            return classes[status] || 'offline';
        },

        getStatusText(status) {
            const texts = {
                'completed': 'Completed',
                'running': 'Running',
                'pending': 'Pending',
                'failed': 'Failed',
                'healing': 'Healing' // NEW: Healing status text
            };
            return texts[status] || status;
        },

        formatDate(dateString) {
            if (!dateString) {
                return '';
            }
            const date = new Date(dateString);
            return date.toLocaleString();
        },

        formatDuration(seconds) {
            if (!seconds) {
                return '0s';
            }
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
        },

        formatTimestamp(timestamp) {
            if (!timestamp) {
                return 'N/A';
            }
            const date = new Date(timestamp);
            return date.toLocaleString();
        },

        // --- NOTIFICATIONS ---
        showNotification(message, type = 'info') {
            // Simple notification system
            const notification = document.createElement('div');
            notification.className = `alert alert-${type} alert-dismissible fade show`;
            notification.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            const container = document.querySelector('.content') || document.body;
            container.insertBefore(notification, container.firstChild);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 5000);
        },

        // --- PERIODIC UPDATES ---
        startPeriodicUpdates() {},

        // --- UTILITY FUNCTIONS ---
        truncateText(text, maxLength = 50) {
            if (!text) return '';
            return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
        },

        getPriorityClass(priority) {
            const classes = {
                'high': 'text-danger',
                'medium': 'text-warning',
                'low': 'text-info'
            };
            return classes[priority] || 'text-secondary';
        },

        getProgressClass(progress) {
            if (progress >= 100) return 'bg-success';
            if (progress >= 75) return 'bg-info';
            if (progress >= 50) return 'bg-warning';
            return 'bg-secondary';
        },

        // --- MODAL FUNCTIONS ---
        // Event Modal Functions (for Live Stream)
        openEventModal(event) { 
            this.selectedEvent = event; 
            this.showEventModal = true; 
        },
        
        closeEventModal() { 
            this.showEventModal = false; 
            this.selectedEvent = null; 
        },

        // --- Mission Page Functions (Updated for Alpine Modal) ---
        openMissionModal(mission) {
            this.selectedMission = mission;
            this.showMissionModal = true;
        },

        closeMissionModal() {
            this.showMissionModal = false;
            // It's good practice to nullify the selection after a delay to prevent visual glitches during transitions
            setTimeout(() => { this.selectedMission = null; }, 300);
        },

        async cancelMission(missionId) {
            if (!confirm('Are you sure you want to cancel this mission?')) {
                return;
            }
            try {
                const response = await fetch(`/api/missions/${missionId}/cancel`, { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    this.showNotification(`Mission ${missionId} canceled.`, 'success');
                    this.loadMissions(); // Refresh the mission list
                    if (this.selectedMission?.mission_id_str === missionId) {
                        this.closeMissionModal();
                    }
                } else {
                    throw new Error(data.detail || 'Failed to cancel mission');
                }
            } catch (e) {
                this.showNotification(e.message, 'error');
            }
        },

        // --- MISSION HELPER FUNCTIONS ---
        getProgress(mission) {
            return mission?.progress || 0;
        },

        getActiveCount() {
            return this.missions.filter(m => m.status === 'running' || m.status === 'healing').length;
        },

        getCompletedCount() {
            return this.missions.filter(m => m.status === 'completed').length;
        },

        getPendingCount() {
            return this.missions.filter(m => m.status === 'pending').length;
        },

        getSuccessRate() {
            const completed = this.getCompletedCount();
            const total = this.missions.length;
            return total > 0 ? Math.round((completed / total) * 100) : 0;
        },

        // --- TEST MISSION FUNCTIONS ---
        async createTestMission() {
            try {
                const response = await fetch('/api/test-missions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.newTestMission)
                });
                
                if (response.ok) {
                    this.showNotification('Test mission created successfully!', 'success');
                    this.newTestMission.prompt = '';
                    await this.loadMissions();
                } else {
                    throw new Error('Failed to create test mission');
                }
            } catch (e) {
                console.error('Test mission creation failed:', e);
                this.showNotification(e.message, 'error');
            }
        },

        getPassedTests() {
            return this.testStreamEvents.filter(e => e.status === 'passed').length;
        },

        getFailedTests() {
            return this.testStreamEvents.filter(e => e.status === 'failed').length;
        },

        getRunningTests() {
            return this.testStreamEvents.filter(e => e.status === 'running').length;
        },

        getTestSuccessRate() {
            const passed = this.getPassedTests();
            const total = this.testStreamEvents.length;
            return total > 0 ? Math.round((passed / total) * 100) : 0;
        },

        // --- PRE-FLIGHT CHECK FUNCTIONS ---
        async runPreFlightCheck() {
            if (!this.newMission.prompt.trim()) {
                this.preflightCheckResult = null;
                return;
            }

            this.isCheckingPrompt = true;
            
            try {
                const response = await fetch('/api/missions/pre-flight-check', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: this.newMission.prompt })
                });
                this.preflightCheckResult = await response.json();
            } catch (e) {
                console.error('Pre-flight check failed:', e);
                this.preflightCheckResult = { 
                    go_no_go: false, 
                    feedback: "Error connecting to Guardian Protocol.",
                    clarity_score: 0.0,
                    risk_score: 0.0,
                    suggestions: ["Please try again"]
                };
            } finally {
                this.isCheckingPrompt = false;
            }
        },

        // --- END LIVE STREAM TOGGLE LOGIC ---
    };
}