function sentinelApp() {
    return {
        missions: [],
        recentActivity: [],
        liveLogs: [],
        systemStatus: {
            apiServer: 'online',
            cognitiveEngine: 'online',
            database: 'online',
            aiModels: 'online'
        },

        observabilityData: {
            thinkingSessions: 0,
            toolCalls: 0,
            apiCalls: 0,
            memoryUsage: 0
        },
        testAnalytics: {
            testsRun: 0,
            successRate: 0,
            avgDuration: 0,
            performance: 0
        },
        eventSource: null,

        // Live Stream Data
        liveStreamEvents: [],
        liveStreamStats: {
            totalEvents: 0,
            activeAgents: 0,
            successRate: 0,
            lastUpdate: 'Never'
        },
        selectedEventType: '',
        autoRefresh: true,
        showEventModal: false,
        selectedEvent: null,
        isPageVisible: true,
        liveStreamInterval: null,

        init() {
            this.initializeSidebar();
            this.loadMissions();
            this.loadRecentActivity();
            this.startRealTimeUpdates();
            this.updateSystemStatus();
            this.startLiveLogStream();
            this.loadObservabilityData();
            this.loadTestAnalytics();
            this.initQuickActions();
            this.initializeLiveStream();
            this.initializePageVisibilityDetection();
        },

        initializeSidebar() {
            // Ensure sidebar has the correct classes
            const sidebar = document.querySelector('.sidebar');
            if (sidebar) {
                sidebar.classList.add('sidebar-mini');
                
                // Ensure all nav items are properly structured
                const navItems = sidebar.querySelectorAll('.nav-item');
                navItems.forEach(item => {
                    const link = item.querySelector('.nav-link');
                    if (link) {
                        // Remove any existing text elements
                        const textElements = link.querySelectorAll('p');
                        textElements.forEach(el => el.style.display = 'none');
                        
                        // Ensure icon is properly displayed
                        const icon = link.querySelector('i');
                        if (icon) {
                            icon.style.display = 'block';
                            icon.style.margin = '0';
                            icon.style.fontSize = '18px';
                        }
                    }
                });
            }

            // Adjust main panel
            const mainPanel = document.querySelector('.main-panel');
            if (mainPanel) {
                mainPanel.style.marginLeft = '60px';
                mainPanel.style.width = 'calc(100% - 60px)';
            }
        },

        async loadMissions() {
            try {
                const response = await fetch('/missions');
                if (response.ok) {
                    const data = await response.json();
                    this.missions = data.missions || [];
                }
            } catch (error) {
                console.error('Error loading missions:', error);
            }
        },

        async loadRecentActivity() {
            // Simulate recent activity data
            this.recentActivity = [
                {
                    id: 1,
                    icon: 'fa-robot',
                    message: 'Planning Agent started mission analysis',
                    time: '2 minutes ago'
                },
                {
                    id: 2,
                    icon: 'fa-rocket',
                    message: 'Execution Agent completed task #156',
                    time: '5 minutes ago'
                },
                {
                    id: 3,
                    icon: 'fa-check-circle',
                    message: 'Review Agent validated mission results',
                    time: '8 minutes ago'
                },
                {
                    id: 4,
                    icon: 'fa-lightbulb',
                    message: 'Debug Agent identified optimization opportunity',
                    time: '12 minutes ago'
                },
                {
                    id: 5,
                    icon: 'fa-brain',
                    message: 'AI Agent completed thinking session',
                    time: '15 minutes ago'
                }
            ];
        },

        startRealTimeUpdates() {
            setInterval(() => {
                this.updateSystemStatus();
                this.updateObservabilityData();
                this.updateTestAnalytics();
                if (this.autoRefresh) {
                    this.loadLiveStreamEvents();
                }
            }, 5000);
        },

        startLiveLogStream() {
            this.eventSource = new EventSource('/api/events/stream');
            
            this.eventSource.onmessage = (event) => {
                try {
                    const logData = JSON.parse(event.data);
                    this.addLiveLog(logData);
                } catch (error) {
                    console.error('Error parsing log data:', error);
                }
            };

            this.eventSource.onerror = (error) => {
                console.error('EventSource error:', error);
                setTimeout(() => {
                    this.startLiveLogStream();
                }, 5000);
            };
        },

        addLiveLog(logData) {
            const timestamp = this.formatTimestamp(new Date());
            const logEntry = `[${timestamp}] ${logData.level}: ${logData.message}`;
            
            this.liveLogs.push(logEntry);
            
            // Keep only the last 100 logs
            if (this.liveLogs.length > 100) {
                this.liveLogs.shift();
            }
            
            this.updateLogDisplay();
        },

        updateLogDisplay() {
            const logContainer = document.getElementById('live-logs');
            if (logContainer) {
                logContainer.innerHTML = this.liveLogs.map(log => 
                    `<div class="log-entry">${log}</div>`
                ).join('');
                
                // Auto-scroll to bottom
                logContainer.scrollTop = logContainer.scrollHeight;
            }
        },

        formatTimestamp(date) {
            return date.toLocaleTimeString('en-US', {
                hour12: false,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        },

        async updateSystemStatus() {
            try {
                const response = await fetch('/health');
                if (response.ok) {
                    const data = await response.json();
                    this.systemStatus = {
                        apiServer: data.api_server || 'online',
                        cognitiveEngine: data.cognitive_engine || 'online',
                        database: data.database || 'online',
                        aiModels: data.ai_models || 'online'
                    };
                }
            } catch (error) {
                console.error('Error updating system status:', error);
                this.systemStatus = {
                    apiServer: 'offline',
                    cognitiveEngine: 'offline',
                    database: 'offline',
                    aiModels: 'offline'
                };
            }
            
            this.updateStatusIndicators();
        },

        updateStatusIndicators() {
            const statusElements = document.querySelectorAll('.status-badge-compact');
            statusElements.forEach(element => {
                const label = element.previousElementSibling;
                if (label) {
                    const statusText = label.textContent.toLowerCase();
                    let status = 'offline';
                    
                    if (statusText.includes('api server')) {
                        status = this.systemStatus.apiServer;
                    } else if (statusText.includes('cognitive engine')) {
                        status = this.systemStatus.cognitiveEngine;
                    } else if (statusText.includes('database')) {
                        status = this.systemStatus.database;
                    } else if (statusText.includes('ai models')) {
                        status = this.systemStatus.aiModels;
                    }
                    
                    element.className = `status-badge-compact ${status}`;
                    element.textContent = status === 'online' ? 'Online' : 
                                       status === 'offline' ? 'Offline' : 'Warning';
                }
            });
        },



        // Live Stream Functions
        async initializeLiveStream() {
            await this.loadLiveStreamEvents();
            if (this.autoRefresh) {
                this.startLiveStreamUpdates();
            }
        },

        async loadLiveStreamEvents() {
            try {
                const response = await fetch('/api/observability/live-stream');
                const data = await response.json();
                
                console.log('Live stream data received:', data);
                
                if (data.success) {
                    this.liveStreamEvents = data.events || [];
                    console.log('Live stream events loaded:', this.liveStreamEvents);
                    this.updateLiveStreamStats();
                }
            } catch (error) {
                console.error('Error loading live stream events:', error);
            }
        },

        initializePageVisibilityDetection() {
            // Handle page visibility changes
            document.addEventListener('visibilitychange', () => {
                this.isPageVisible = !document.hidden;
                if (this.isPageVisible) {
                    this.startLiveStreamUpdates();
                } else {
                    this.stopLiveStreamUpdates();
                }
            });

            // Handle page focus/blur
            window.addEventListener('focus', () => {
                this.isPageVisible = true;
                this.startLiveStreamUpdates();
            });

            window.addEventListener('blur', () => {
                this.isPageVisible = false;
                this.stopLiveStreamUpdates();
            });
        },

        startLiveStreamUpdates() {
            if (this.liveStreamInterval) {
                clearInterval(this.liveStreamInterval);
            }
            
            // Only start updates if page is visible and auto-refresh is enabled
            if (this.isPageVisible && this.autoRefresh) {
                this.liveStreamInterval = setInterval(() => {
                    if (this.isPageVisible && this.autoRefresh) {
                        this.loadLiveStreamEvents();
                    }
                }, 2000); // Update every 2 seconds for real-time feel
            }
        },

        stopLiveStreamUpdates() {
            if (this.liveStreamInterval) {
                clearInterval(this.liveStreamInterval);
                this.liveStreamInterval = null;
            }
        },

        updateLiveStreamStats() {
            const events = this.liveStreamEvents;
            const totalEvents = events.length;
            const successEvents = events.filter(e => e.severity === 'info').length;
            const activeAgents = new Set(events.filter(e => e.agent_name).map(e => e.agent_name)).size;
            
            this.liveStreamStats = {
                totalEvents: totalEvents,
                activeAgents: activeAgents,
                successRate: totalEvents > 0 ? Math.round((successEvents / totalEvents) * 100) : 0,
                lastUpdate: new Date().toLocaleTimeString()
            };
        },

        refreshLiveStream() {
            this.loadLiveStreamEvents();
        },

        toggleAutoRefresh() {
            this.autoRefresh = !this.autoRefresh;
            if (this.autoRefresh && this.isPageVisible) {
                this.startLiveStreamUpdates();
            } else {
                this.stopLiveStreamUpdates();
            }
        },

        filterLiveStream() {
            // Filter events based on selected event type
            if (this.selectedEventType) {
                this.loadLiveStreamEvents();
            } else {
                this.loadLiveStreamEvents();
            }
        },

        openEventModal(event) {
            console.log('Opening event modal for:', event);
            console.log('Event type:', event?.event_type);
            console.log('Event data:', event?.event_data);
            this.selectedEvent = event;
            this.showEventModal = true;
            console.log('Modal should now be visible. showEventModal:', this.showEventModal);
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
                'session_start': 'fa-play-circle',
                'session_complete': 'fa-stop-circle',
                'system_error': 'fa-exclamation-triangle',
                'thinking': 'fa-brain',
                'decision': 'fa-sitemap',
                'response': 'fa-comment',
                'tool_call': 'fa-wrench',
                'api_call': 'fa-network-wired',
                'test_execution': 'fa-vial',
                'planning': 'fa-map',
                'analysis': 'fa-chart-line',
                'optimization': 'fa-cogs',
                'validation': 'fa-check-square'
            };
            return icons[eventType] || 'fa-info-circle';
        },

        formatEventType(eventType) {
            const types = {
                'agent_action': 'Agent Action',
                'mission_start': 'Mission Start',
                'mission_complete': 'Mission Complete',
                'session_start': 'Session Start',
                'session_complete': 'Session Complete',
                'system_error': 'System Error',
                'thinking': 'Agent Thinking',
                'decision': 'Agent Decision',
                'response': 'Agent Response',
                'tool_call': 'Tool Call',
                'api_call': 'API Call',
                'test_execution': 'Test Execution',
                'planning': 'Agent Planning',
                'analysis': 'Agent Analysis',
                'optimization': 'Agent Optimization',
                'validation': 'Agent Validation'
            };
            return types[eventType] || eventType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        },

        formatDetailKey(key) {
            return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        },

        formatDetailValue(value) {
            if (value === null || value === undefined) {
                return 'N/A';
            }
            if (typeof value === 'boolean') {
                return value ? 'Yes' : 'No';
            }
            if (typeof value === 'number') {
                if (value > 1000 && value < 60000) { // Duration in milliseconds
                    return this.formatDuration(value);
                }
                if (value > 1000000) { // Memory in bytes
                    return (value / 1024 / 1024).toFixed(2) + ' MB';
                }
                if (value <= 100) { // CPU percentage
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
            if (typeof value === 'object') {
                try {
                    return JSON.stringify(value, null, 2);
                } catch (e) {
                    return String(value);
                }
            }
            return String(value);
        },

        // Enhanced observability functions
        async loadObservabilityData() {
            try {
                const response = await fetch('/api/observability/agent-analytics');
                const data = await response.json();
                
                if (data.success && data.analytics) {
                    const analytics = data.analytics;
                    this.observabilityData = {
                        thinkingSessions: analytics.summary?.total_tokens || 0,
                        toolCalls: analytics.summary?.total_tool_calls || 0,
                        apiCalls: analytics.summary?.total_api_calls || 0,
                        memoryUsage: analytics.summary?.avg_memory_usage_mb || 0
                    };
                }
            } catch (error) {
                console.error('Error loading observability data:', error);
            }
        },

        async loadTestAnalytics() {
            try {
                const response = await fetch('/api/test-missions/analysis');
                const data = await response.json();
                
                if (data.success) {
                    this.testAnalytics = {
                        totalTests: data.total_tests || 0,
                        successRate: data.success_rate || 0,
                        avgDuration: data.avg_duration_ms || 0,
                        performance: data.performance_score || 0
                    };
                }
            } catch (error) {
                console.error('Error loading test analytics:', error);
            }
        },

        updateObservabilityData() {
            // Simulate real-time updates
            this.observabilityData.thinkingSessions += Math.floor(Math.random() * 3);
            this.observabilityData.toolCalls += Math.floor(Math.random() * 2);
            this.observabilityData.apiCalls += Math.floor(Math.random() * 1);
            this.observabilityData.memoryUsage = Math.max(0, this.observabilityData.memoryUsage + (Math.random() - 0.5) * 2);
        },

        updateTestAnalytics() {
            // Simulate real-time updates
            this.testAnalytics.totalTests += Math.floor(Math.random() * 1);
            this.testAnalytics.successRate = Math.min(100, Math.max(0, this.testAnalytics.successRate + (Math.random() - 0.5) * 2));
            this.testAnalytics.avgDuration = Math.max(100, this.testAnalytics.avgDuration + (Math.random() - 0.5) * 50);
            this.testAnalytics.performance = Math.min(100, Math.max(0, this.testAnalytics.performance + (Math.random() - 0.5) * 1));
        },

        initQuickActions() {
            // Add event listeners to quick action buttons
            const quickActionButtons = document.querySelectorAll('.quick-action-btn');
            quickActionButtons.forEach(button => {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    const action = button.dataset.action;
                    this.handleQuickAction(action);
                });
            });
        },

        handleQuickAction(action) {
            switch (action) {
                case 'create-mission':
                    this.createNewMission();
                    break;
                case 'generate-report':
                    this.generateReport();
                    break;
                case 'health-check':
                    this.performHealthCheck();
                    break;
                case 'optimize':
                    this.optimizePerformance();
                    break;
                default:
                    console.log('Unknown action:', action);
            }
        },

        async createNewMission() {
            try {
                const response = await fetch('/api/missions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        prompt: 'New mission created via quick action',
                        agent_type: 'general'
                    })
                });
                
                if (response.ok) {
                    this.showNotification('Mission created successfully', 'success');
                    this.loadMissions();
                }
            } catch (error) {
                console.error('Error creating mission:', error);
                this.showNotification('Failed to create mission', 'error');
            }
        },

        async generateReport() {
            try {
                const response = await fetch('/api/observability/report');
                if (response.ok) {
                    const report = await response.json();
                    this.showNotification('Report generated successfully', 'success');
                    console.log('Generated report:', report);
                }
            } catch (error) {
                console.error('Error generating report:', error);
                this.showNotification('Failed to generate report', 'error');
            }
        },

        async performHealthCheck() {
            try {
                const response = await fetch('/health');
                if (response.ok) {
                    this.showNotification('Health check completed', 'success');
                } else {
                    this.showNotification('Health check failed', 'error');
                }
            } catch (error) {
                console.error('Error performing health check:', error);
                this.showNotification('Health check failed', 'error');
            }
        },

        async optimizePerformance() {
            try {
                const response = await fetch('/api/optimize', {
                    method: 'POST'
                });
                
                if (response.ok) {
                    this.showNotification('Performance optimization completed', 'success');
                } else {
                    this.showNotification('Optimization failed', 'error');
                }
            } catch (error) {
                console.error('Error optimizing performance:', error);
                this.showNotification('Optimization failed', 'error');
            }
        },

        getActiveAgentCount() {
            return this.recentActivity.filter(activity => 
                activity.message.includes('Agent') && 
                !activity.message.includes('completed')
            ).length;
        },

        getSuccessRate() {
            // Simulate success rate calculation
            return Math.floor(Math.random() * 20) + 80;
        },

        getAverageResponseTime() {
            // Simulate average response time
            return (Math.random() * 2 + 0.5).toFixed(1);
        },

        getAllAgentStatuses() {
            return {
                planning: 'active',
                execution: 'active',
                review: 'idle',
                debug: 'active'
            };
        },

        async submitMission(missionData) {
            try {
                const response = await fetch('/api/missions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(missionData)
                });
                
                if (response.ok) {
                    const result = await response.json();
                    this.showNotification('Mission submitted successfully', 'success');
                    this.loadMissions();
                    return result;
                } else {
                    throw new Error('Failed to submit mission');
                }
            } catch (error) {
                console.error('Error submitting mission:', error);
                this.showNotification('Failed to submit mission', 'error');
                throw error;
            }
        },

        async generateAIResponse(prompt) {
            try {
                const response = await fetch('/api/ai/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ prompt })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    return result.response;
                } else {
                    throw new Error('Failed to generate AI response');
                }
            } catch (error) {
                console.error('Error generating AI response:', error);
                throw error;
            }
        },

        async analyzeCode(code, language = 'python') {
            try {
                const response = await fetch('/api/ai/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ code, language })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    return result.analysis;
                } else {
                    throw new Error('Failed to analyze code');
                }
            } catch (error) {
                console.error('Error analyzing code:', error);
                throw error;
            }
        },

        // Enhanced mission management functions
        async refreshMissions() {
            await this.loadMissions();
            this.showNotification('Missions refreshed', 'success');
        },

        async exportMissionData() {
            try {
                const response = await fetch('/api/observability/export');
                if (response.ok) {
                    const data = await response.json();
                    this.showNotification('Data exported successfully', 'success');
                    console.log('Exported data:', data);
                }
            } catch (error) {
                console.error('Error exporting data:', error);
                this.showNotification('Export failed', 'error');
            }
        },

        async clearCompletedMissions() {
            this.missions = this.missions.filter(mission => mission.status !== 'completed');
            this.showNotification('Completed missions cleared', 'success');
        },

        async viewMissionDetails(missionId) {
            try {
                const response = await fetch(`/api/missions/${missionId}`);
                if (response.ok) {
                    const mission = await response.json();
                    this.showNotification('Mission details loaded', 'success');
                    console.log('Mission details:', mission);
                }
            } catch (error) {
                console.error('Error loading mission details:', error);
                this.showNotification('Failed to load mission details', 'error');
            }
        },

        async pauseMission(missionId) {
            try {
                const response = await fetch(`/api/missions/${missionId}/pause`, {
                    method: 'POST'
                });
                if (response.ok) {
                    this.showNotification('Mission paused', 'success');
                    this.loadMissions();
                }
            } catch (error) {
                console.error('Error pausing mission:', error);
                this.showNotification('Failed to pause mission', 'error');
            }
        },

        async cancelMission(missionId) {
            try {
                const response = await fetch(`/api/missions/${missionId}/cancel`, {
                    method: 'POST'
                });
                if (response.ok) {
                    this.showNotification('Mission cancelled', 'success');
                    this.loadMissions();
                }
            } catch (error) {
                console.error('Error cancelling mission:', error);
                this.showNotification('Failed to cancel mission', 'error');
            }
        },

        showNotification(message, type = 'info') {
            // Create notification element
            const notification = document.createElement('div');
            notification.className = `alert alert-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} alert-dismissible fade show`;
            notification.style.position = 'fixed';
            notification.style.top = '20px';
            notification.style.right = '20px';
            notification.style.zIndex = '9999';
            notification.style.minWidth = '300px';
            
            notification.innerHTML = `
                ${message}
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            `;
            
            document.body.appendChild(notification);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 5000);
        },

        destroy() {
            if (this.eventSource) {
                this.eventSource.close();
            }
        }
    };
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Alpine.js app
    if (typeof Alpine !== 'undefined') {
        Alpine.data('sentinelApp', sentinelApp);
    }
}); 