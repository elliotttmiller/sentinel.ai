// Test Missions Dashboard Application
function testMissionsApp() {
    return {
        // Data
        availableMissions: [],
        executions: [],
        recentExecutions: [],
        agentAnalytics: {},
        currentExecution: null,
        loading: false,
        error: null,

        // Live Stream Data
        testStreamEvents: [],
        testStreamStats: {
            activeTests: 0,
            successRate: 0,
            avgDuration: 0,
            lastUpdate: 'Never'
        },
        selectedTestEventType: '',
        testAutoRefresh: true,
        showTestEventModal: false,
        selectedTestEvent: null,
        isPageVisible: true,
        testStreamInterval: null,
        showExecutionModal: false,
        selectedExecution: null,

        // Initialize the application
        init() {
            this.loadAvailableMissions();
            this.loadTestExecutions();
            this.loadAgentAnalytics();
            this.startRealTimeUpdates();
            this.initializeTestStream();
            this.initializePageVisibilityDetection();
        },

        initializePageVisibilityDetection() {
            // Handle page visibility changes
            document.addEventListener('visibilitychange', () => {
                this.isPageVisible = !document.hidden;
                if (this.isPageVisible) {
                    this.startTestStreamUpdates();
                } else {
                    this.stopTestStreamUpdates();
                }
            });

            // Handle page focus/blur
            window.addEventListener('focus', () => {
                this.isPageVisible = true;
                this.startTestStreamUpdates();
            });

            window.addEventListener('blur', () => {
                this.isPageVisible = false;
                this.stopTestStreamUpdates();
            });
        },

        // Load available test missions
        async loadAvailableMissions() {
            try {
                this.loading = true;
                const response = await fetch('/api/test-missions');
                const data = await response.json();
                
                if (data.success) {
                    this.availableMissions = data.missions;
                } else {
                    throw new Error('Failed to load test missions');
                }
            } catch (error) {
                console.error('Error loading test missions:', error);
                this.error = error.message;
            } finally {
                this.loading = false;
            }
        },

        // Load test executions
        async loadTestExecutions() {
            try {
                const response = await fetch('/api/test-missions/executions');
                const data = await response.json();
                
                if (data.success) {
                    this.executions = data.executions;
                    this.recentExecutions = data.executions.slice(-10); // Last 10 executions
                } else {
                    throw new Error('Failed to load test executions');
                }
            } catch (error) {
                console.error('Error loading test executions:', error);
                this.error = error.message;
            }
        },

        // Load agent analytics
        async loadAgentAnalytics() {
            try {
                const response = await fetch('/api/observability/agent-analytics');
                const data = await response.json();
                
                if (data.success) {
                    this.agentAnalytics = data.analytics;
                } else {
                    throw new Error('Failed to load agent analytics');
                }
            } catch (error) {
                console.error('Error loading agent analytics:', error);
                this.error = error.message;
            }
        },

        // Run a test mission
        async runTestMission(missionId) {
            try {
                this.loading = true;
                this.error = null;
                
                const response = await fetch(`/api/test-missions/${missionId}/run`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        user_request: `Running test mission: ${missionId}`
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.currentExecution = data;
                    this.showNotification('Test mission started successfully!', 'success');
                    
                    // Reload data after execution
                    setTimeout(() => {
                        this.loadTestExecutions();
                        this.loadAgentAnalytics();
                    }, 2000);
                } else {
                    throw new Error(data.detail || 'Failed to run test mission');
                }
            } catch (error) {
                console.error('Error running test mission:', error);
                this.error = error.message;
                this.showNotification('Failed to run test mission', 'error');
            } finally {
                this.loading = false;
            }
        },

        // View mission details
        viewMissionDetails(mission) {
            // Create a modal or expand the mission card to show details
            console.log('Mission details:', mission);
            this.showNotification(`Viewing details for: ${mission.name}`, 'info');
        },

        // Test Stream Functions
        async initializeTestStream() {
            await this.loadTestStreamEvents();
            if (this.testAutoRefresh) {
                this.startTestStreamUpdates();
            }
        },

        async loadTestStreamEvents() {
            try {
                const response = await fetch('/api/observability/test-mission-live-stream');
                const data = await response.json();
                
                if (data.success) {
                    this.testStreamEvents = data.events || [];
                    
                    // Update stats from the API response
                    if (data.stats) {
                        this.testStreamStats = {
                            activeTests: data.stats.active_tests || 0,
                            successRate: data.stats.success_rate || 0,
                            avgDuration: this.formatDuration(data.stats.avg_duration || 0),
                            lastUpdate: new Date(data.stats.last_update).toLocaleTimeString()
                        };
                    } else {
                        this.updateTestStreamStats();
                    }
                }
            } catch (error) {
                console.error('Error loading test stream events:', error);
            }
        },

        startTestStreamUpdates() {
            if (this.testStreamInterval) {
                clearInterval(this.testStreamInterval);
            }
            
            // Only start updates if page is visible and auto-refresh is enabled
            if (this.isPageVisible && this.testAutoRefresh) {
                this.testStreamInterval = setInterval(() => {
                    if (this.isPageVisible && this.testAutoRefresh) {
                        this.loadTestStreamEvents();
                    }
                }, 2000);
            }
        },

        stopTestStreamUpdates() {
            if (this.testStreamInterval) {
                clearInterval(this.testStreamInterval);
                this.testStreamInterval = null;
            }
        },

        updateTestStreamStats() {
            const events = this.testStreamEvents;
            const totalEvents = events.length;
            const successEvents = events.filter(e => e.severity === 'info').length;
            const activeTests = new Set(events.filter(e => e.mission_id).map(e => e.mission_id)).size;
            
            this.testStreamStats = {
                activeTests: activeTests,
                successRate: totalEvents > 0 ? Math.round((successEvents / totalEvents) * 100) : 0,
                avgDuration: this.calculateAverageDuration(events),
                lastUpdate: new Date().toLocaleTimeString()
            };
        },

        calculateAverageDuration(events) {
            const durations = events
                .filter(e => e.event_data?.duration)
                .map(e => e.event_data.duration);
            
            if (durations.length === 0) return '0s';
            
            const avgMs = durations.reduce((sum, d) => sum + d, 0) / durations.length;
            return this.formatDuration(avgMs);
        },

        refreshTestStream() {
            this.loadTestStreamEvents();
        },

        toggleTestAutoRefresh() {
            this.testAutoRefresh = !this.testAutoRefresh;
            if (this.testAutoRefresh && this.isPageVisible) {
                this.startTestStreamUpdates();
            } else {
                this.stopTestStreamUpdates();
            }
        },

        filterTestStream() {
            // Filter events based on selected event type
            if (this.selectedTestEventType) {
                this.loadTestStreamEvents();
            } else {
                this.loadTestStreamEvents();
            }
        },

        openTestEventModal(event) {
            console.log('Opening test event modal for:', event);
            this.selectedTestEvent = event;
            this.showTestEventModal = true;
        },

        closeTestEventModal() {
            this.showTestEventModal = false;
            this.selectedTestEvent = null;
        },

        getTestEventIcon(eventType) {
            const icons = {
                'test_start': 'fa-play-circle',
                'test_complete': 'fa-check-circle',
                'scenario_start': 'fa-rocket',
                'scenario_complete': 'fa-stop-circle',
                'agent_action': 'fa-robot',
                'test_error': 'fa-exclamation-triangle',
                'test_execution': 'fa-vial',
                'test_validation': 'fa-check-square'
            };
            return icons[eventType] || 'fa-info-circle';
        },

        formatTestEventType(eventType) {
            const types = {
                'test_start': 'Test Start',
                'test_complete': 'Test Complete',
                'scenario_start': 'Scenario Start',
                'scenario_complete': 'Scenario Complete',
                'agent_action': 'Agent Action',
                'test_error': 'Test Error',
                'test_execution': 'Test Execution',
                'test_validation': 'Test Validation'
            };
            return types[eventType] || eventType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        },

        // Enhanced execution details modal
        async viewExecutionDetails(executionId) {
            try {
                const response = await fetch(`/api/test-missions/executions/${executionId}`);
                const data = await response.json();
                
                if (data.success) {
                    this.selectedExecution = data.execution;
                    this.showExecutionModal = true;
                } else {
                    this.showNotification('Failed to load execution details', 'error');
                }
            } catch (error) {
                console.error('Error loading execution details:', error);
                this.showNotification('Error loading execution details', 'error');
            }
        },

        closeExecutionModal() {
            this.showExecutionModal = false;
            this.selectedExecution = null;
        },

        formatDetailKey(key) {
            return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        },

        formatDetailValue(value) {
            if (typeof value === 'boolean') {
                return value ? 'Yes' : 'No';
            }
            if (typeof value === 'number') {
                if (key.includes('duration') || key.includes('time')) {
                    return this.formatDuration(value);
                }
                if (key.includes('memory')) {
                    return value + ' MB';
                }
                if (key.includes('cpu')) {
                    return value + '%';
                }
                return value.toString();
            }
            if (typeof value === 'string') {
                if (value.length > 100) {
                    return value.substring(0, 100) + '...';
                }
                return value;
            }
            return JSON.stringify(value);
        },

        formatTimestamp(timestamp) {
            if (!timestamp) return 'Unknown';
            const date = new Date(timestamp);
            return date.toLocaleString();
        },

        formatDuration(ms) {
            if (ms < 1000) return ms + 'ms';
            if (ms < 60000) return Math.round(ms / 1000) + 's';
            return Math.round(ms / 60000) + 'm';
        },

        // Export execution data
        async exportExecutionData(executionId) {
            try {
                const response = await fetch(`/api/test-missions/executions/${executionId}`);
                const data = await response.json();
                
                if (data.success) {
                    // Create and download JSON file
                    const blob = new Blob([JSON.stringify(data.execution, null, 2)], {
                        type: 'application/json'
                    });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `execution_${executionId}.json`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                    
                    this.showNotification('Execution data exported successfully!', 'success');
                } else {
                    throw new Error('Failed to export execution data');
                }
            } catch (error) {
                console.error('Error exporting execution data:', error);
                this.showNotification('Failed to export execution data', 'error');
            }
        },

        // Display execution details in a modal or expanded view
        displayExecutionDetails(execution) {
            // Create a detailed view of the execution
            const details = `
                <div class="execution-details">
                    <h5>${execution.mission_name}</h5>
                    <div class="execution-stats">
                        <div class="stat">
                            <label>Status:</label>
                            <span class="badge ${execution.execution_success ? 'badge-success' : 'badge-danger'}">
                                ${execution.execution_success ? 'Success' : 'Failed'}
                            </span>
                        </div>
                        <div class="stat">
                            <label>Duration:</label>
                            <span>${this.formatDuration(execution.duration_seconds)}</span>
                        </div>
                        <div class="stat">
                            <label>Scenarios:</label>
                            <span>${execution.scenarios_executed}</span>
                        </div>
                    </div>
                    ${execution.performance_metrics ? `
                        <div class="performance-metrics">
                            <h6>Performance Metrics</h6>
                            <div class="metrics-grid">
                                <div class="metric">
                                    <label>Success Rate:</label>
                                    <span>${(execution.performance_metrics.success_rate * 100).toFixed(1)}%</span>
                                </div>
                                <div class="metric">
                                    <label>Avg Duration:</label>
                                    <span>${execution.performance_metrics.avg_scenario_duration_ms.toFixed(0)}ms</span>
                                </div>
                                <div class="metric">
                                    <label>Issues Found:</label>
                                    <span>${execution.performance_metrics.total_issues_found}</span>
                                </div>
                            </div>
                        </div>
                    ` : ''}
                </div>
            `;
            
            // You could show this in a modal or expand the table row
            console.log('Execution details HTML:', details);
        },

        // Helper methods
        getDifficultyClass(difficulty) {
            const classes = {
                'easy': 'badge-success',
                'medium': 'badge-warning',
                'hard': 'badge-danger',
                'expert': 'badge-dark'
            };
            return classes[difficulty] || 'badge-secondary';
        },

        getSuccessRate() {
            if (this.executions.length === 0) return 0;
            const successful = this.executions.filter(e => e.execution_success).length;
            return ((successful / this.executions.length) * 100).toFixed(1);
        },

        getAverageDuration() {
            if (this.executions.length === 0) return 0;
            const total = this.executions.reduce((sum, e) => sum + e.duration_seconds, 0);
            return (total / this.executions.length).toFixed(1);
        },

        getExecutionSuccessRate(execution) {
            if (!execution.performance_metrics) return 0;
            return (execution.performance_metrics.success_rate * 100).toFixed(1);
        },

        formatDuration(seconds) {
            if (seconds < 60) {
                return `${seconds.toFixed(1)}s`;
            } else if (seconds < 3600) {
                const minutes = Math.floor(seconds / 60);
                const remainingSeconds = seconds % 60;
                return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
            } else {
                const hours = Math.floor(seconds / 3600);
                const remainingMinutes = Math.floor((seconds % 3600) / 60);
                return `${hours}h ${remainingMinutes}m`;
            }
        },

        // Real-time updates
        startRealTimeUpdates() {
            setInterval(() => {
                this.loadAvailableMissions();
                this.loadTestExecutions();
                this.loadAgentAnalytics();
                if (this.testAutoRefresh) {
                    this.loadTestStreamEvents();
                }
            }, 30000);
        },

        // Show notification
        showNotification(message, type = 'info') {
            // Create a simple notification
            const notification = document.createElement('div');
            notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
            notification.style.position = 'fixed';
            notification.style.top = '20px';
            notification.style.right = '20px';
            notification.style.zIndex = '9999';
            notification.style.minWidth = '300px';
            
            notification.innerHTML = `
                ${message}
                <button type="button" class="close" data-dismiss="alert">
                    <span>&times;</span>
                </button>
            `;
            
            document.body.appendChild(notification);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 5000);
        }
    };
}

// Initialize the application when the page loads
document.addEventListener('alpine:init', () => {
    Alpine.data('testMissionsApp', testMissionsApp);
}); 