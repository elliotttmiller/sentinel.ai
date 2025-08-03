/**
 * Unified Real-Time Controller for Sentinel Command Center v5.4
 * Handles all real-time data streams and UI updates with Phase 5 features
 */

function sentinelApp() {
    return {
        // State properties
        missions: [],
        agents: [],
        systemLogs: [],
        liveStreamEvents: [],
        agentActivity: [],
        systemStatus: {
            api_server: { status: 'online', last_check: new Date().toISOString() },
            cognitive_engine: { status: 'online', last_check: new Date().toISOString() }
        },
        newMission: {
            prompt: '',
            agent_type: 'developer',
            priority: 'medium'
        },
        
        // Phase 4 State Properties
        optimizationProposals: [],
        healingMissions: [],
        
        // NEW: Phase 5 State Properties
        preflightCheckResult: null,
        isCheckingPrompt: false,
        analyticsSummary: { missions: {}, performance: {} },
        performanceChart: null,
        
        // Modal State Properties
        showMissionModal: false,
        selectedMission: null,
        
        // Test Mission State Properties
        newTestMission: {
            prompt: '',
            test_type: 'unit',
            priority: 'low'
        },
        testStreamEvents: [],
        
        // Computed properties
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

        // Initialize the application
        init() {
            this.loadInitialData();
            this.connectToEventStream();
            this.startPeriodicUpdates();
        },

        async loadInitialData() {
            await Promise.all([
                this.loadMissions(),
                this.loadAgents(),
                this.loadSystemLogs()
            ]);
            
            // Load Phase 4 data if on settings page
            if (window.location.pathname.includes('settings')) {
                await this.loadOptimizationProposals();
            }
            
            // Load Phase 5 data if on analytics page
            if (window.location.pathname.includes('analytics')) {
                await this.loadAnalyticsSummary();
                await this.loadPerformanceChartData();
            }
        },

        // Event stream connection
        connectToEventStream() {
            const eventSource = new EventSource('/api/events/stream');
            
            eventSource.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.dispatchEvent(data);
                } catch (e) {
                    console.error('Failed to parse event:', e);
                }
            };
            
            eventSource.onerror = (error) => {
                console.error('Event stream error:', error);
                setTimeout(() => this.connectToEventStream(), 5000);
            };
        },

        // Event dispatcher
        dispatchEvent(event) {
            switch (event.event_type) {
                case 'mission_update':
                case 'mission_complete':
                case 'mission_error':
                    this.updateMissionState(event);
                    break;
                case 'agent_action':
                    this.addAgentActivity(event);
                    break;
                case 'system_log':
                    this.addSystemLog(event);
                    break;
                case 'heartbeat':
                    // Keep connection alive
                    break;
                default:
                    console.log('Unhandled event type:', event.event_type);
            }
        },

        // Mission state management
        updateMissionState(event) {
            const missionData = event.payload || {};
            const missionId = missionData.mission_id_str || missionData.id;
            if (!missionId) return;

            const existingMissionIndex = this.missions.findIndex(m => m.mission_id_str === missionId);

            if (existingMissionIndex > -1) {
                this.missions[existingMissionIndex] = { ...this.missions[existingMissionIndex], ...missionData };
            } else {
                this.missions.unshift({ mission_id_str: missionId, ...missionData });
            }
            
            // Phase 4: Update healing missions list
            this.updateHealingMissions();
        },

        // Agent activity management
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
        },

        // System log management
        addSystemLog(event) {
            const log = {
                id: Date.now(),
                timestamp: event.timestamp || new Date().toISOString(),
                level: event.severity || 'INFO',
                source: event.source || 'system',
                message: event.message || ''
            };
            
            this.systemLogs.unshift(log);
            
            // Keep only last 100 logs
            if (this.systemLogs.length > 100) {
                this.systemLogs = this.systemLogs.slice(0, 100);
            }
        },

        // Data loading functions
        async loadMissions() {
            try {
                const response = await fetch('/api/missions');
                const data = await response.json();
                if (data.success) {
                    this.missions = data.missions;
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

        // Phase 4: Optimization proposals management
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

        // Phase 5: Pre-flight check logic
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

        // Phase 5: Analytics logic
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

        // Mission creation
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

        // Phase 4: Healing missions management
        updateHealingMissions() {
            this.healingMissions = this.missions.filter(m => m.status === 'healing');
        },

        // UI helpers
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
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleString();
        },

        formatDuration(seconds) {
            if (!seconds) return '0s';
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
        },

        // Notifications
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

        // Periodic updates
        startPeriodicUpdates() {
            setInterval(() => {
                this.loadMissions();
                this.loadAgents();
            }, 30000); // Update every 30 seconds
        },

        // Utility functions
        truncateText(text, maxLength = 50) {
            if (!text) return '';
            return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
        },

        getPriorityClass(priority) {
            const classes = {
                'low': 'badge bg-success',
                'medium': 'badge bg-warning',
                'high': 'badge bg-danger'
            };
            return classes[priority] || classes['medium'];
        },

        getProgressClass(progress) {
            if (progress >= 100) return 'bg-success';
            if (progress >= 75) return 'bg-info';
            if (progress >= 50) return 'bg-warning';
            return 'bg-secondary';
        },

        // Modal Functions
        openMissionModal(mission) {
            this.selectedMission = mission;
            this.showMissionModal = true;
        },

        closeMissionModal() {
            this.showMissionModal = false;
            this.selectedMission = null;
        },

        // Mission Helper Functions
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

        formatTimestamp(timestamp) {
            if (!timestamp) return 'N/A';
            const date = new Date(timestamp);
            return date.toLocaleString();
        },

        // Test Mission Functions
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

        // Pre-flight Check Functions
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
                
                if (response.ok) {
                    this.preflightCheckResult = await response.json();
                } else {
                    throw new Error('Pre-flight check failed');
                }
            } catch (e) {
                console.error('Pre-flight check error:', e);
                this.preflightCheckResult = {
                    go_no_go: false,
                    feedback: 'Pre-flight check failed. Please try again.',
                    clarity_score: 0,
                    risk_score: 0,
                    suggestions: []
                };
            } finally {
                this.isCheckingPrompt = false;
            }
        }
    };
} 