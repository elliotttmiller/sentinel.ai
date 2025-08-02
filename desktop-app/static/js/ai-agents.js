// AI Agents Page JavaScript
function aiAgentsApp() {
    return {
        agents: [],
        newAgent: {
            name: '',
            type: 'general',
            description: '',
            capabilities: []
        },
        selectedAgent: null,
        isLoading: false,
        
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
            this.loadAgents();
            this.startRealTimeUpdates();
            this.initializeLiveStream();
            this.initializePageVisibilityDetection();
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
        
        loadAgents() {
            this.isLoading = true;
            // Simulate API call to load agents
            setTimeout(() => {
                this.agents = [
                    {
                        id: 1,
                        name: 'Code Reviewer',
                        type: 'code_reviewer',
                        status: 'active',
                        description: 'Specialized in code analysis and review',
                        capabilities: ['code_analysis', 'bug_detection', 'style_review'],
                        performance: 95,
                        missions_completed: 42,
                        last_active: '2 minutes ago'
                    },
                    {
                        id: 2,
                        name: 'Data Analyzer',
                        type: 'data_analyzer',
                        status: 'active',
                        description: 'Advanced data processing and analytics',
                        capabilities: ['data_processing', 'statistical_analysis', 'visualization'],
                        performance: 88,
                        missions_completed: 28,
                        last_active: '5 minutes ago'
                    },
                    {
                        id: 3,
                        name: 'System Monitor',
                        type: 'system_monitor',
                        status: 'idle',
                        description: 'Real-time system monitoring and alerts',
                        capabilities: ['system_monitoring', 'alert_management', 'performance_tracking'],
                        performance: 92,
                        missions_completed: 156,
                        last_active: '1 hour ago'
                    }
                ];
                this.isLoading = false;
            }, 1000);
        },
        
        createAgent() {
            if (!this.newAgent.name || !this.newAgent.type) {
                this.showNotification('Please fill in all required fields', 'error');
                return;
            }
            
            const agent = {
                id: Date.now(),
                ...this.newAgent,
                status: 'active',
                performance: 0,
                missions_completed: 0,
                last_active: 'Just now'
            };
            
            this.agents.push(agent);
            this.resetNewAgentForm();
            this.showNotification('Agent created successfully', 'success');
        },
        
        resetNewAgentForm() {
            this.newAgent = {
                name: '',
                type: 'general',
                description: '',
                capabilities: []
            };
        },
        
        selectAgent(agent) {
            this.selectedAgent = agent;
        },
        
        activateAgent(agentId) {
            const agent = this.agents.find(a => a.id === agentId);
            if (agent) {
                agent.status = 'active';
                agent.last_active = 'Just now';
                this.showNotification('Agent activated', 'success');
            }
        },
        
        deactivateAgent(agentId) {
            const agent = this.agents.find(a => a.id === agentId);
            if (agent) {
                agent.status = 'idle';
                this.showNotification('Agent deactivated', 'info');
            }
        },
        
        deleteAgent(agentId) {
            this.agents = this.agents.filter(a => a.id !== agentId);
            if (this.selectedAgent && this.selectedAgent.id === agentId) {
                this.selectedAgent = null;
            }
            this.showNotification('Agent deleted', 'success');
        },
        
        getStatusClass(status) {
            return {
                'active': 'online',
                'idle': 'warning',
                'offline': 'offline'
            }[status] || 'offline';
        },
        
        getTypeClass(type) {
            return {
                'code_reviewer': 'primary',
                'data_analyzer': 'info',
                'system_monitor': 'success',
                'general': 'secondary'
            }[type] || 'secondary';
        },
        
        getActiveCount() {
            return this.agents.filter(a => a.status === 'active').length;
        },
        
        getTotalCount() {
            return this.agents.length;
        },
        
        getAveragePerformance() {
            if (this.agents.length === 0) return 0;
            const total = this.agents.reduce((sum, agent) => sum + agent.performance, 0);
            return Math.round(total / this.agents.length);
        },
        
        getTotalMissions() {
            return this.agents.reduce((sum, agent) => sum + agent.missions_completed, 0);
        },
        
        startRealTimeUpdates() {
            setInterval(() => {
                // Simulate real-time updates
                this.agents.forEach(agent => {
                    if (agent.status === 'active' && Math.random() > 0.7) {
                        agent.performance = Math.max(0, Math.min(100, agent.performance + (Math.random() - 0.5) * 5));
                    }
                });
            }, 10000);
        },
        
        showNotification(message, type = 'info') {
            const alert = document.createElement('div');
            alert.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
            alert.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                min-width: 300px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            `;
            alert.innerHTML = `
                ${message}
                <button type="button" class="close" data-dismiss="alert">
                    <span>&times;</span>
                </button>
            `;
            
            document.body.appendChild(alert);
            
            setTimeout(() => {
                alert.remove();
            }, 5000);
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
                
                if (data.success) {
                    this.liveStreamEvents = data.events || [];
                    this.updateLiveStreamStats();
                }
            } catch (error) {
                console.error('Error loading live stream events:', error);
            }
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
    };
} 