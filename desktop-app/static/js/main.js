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
        resourceMetrics: {
            cpu: 45,
            memory: 62,
            network: 28
        },
        eventSource: null,

        init() {
            this.initializeSidebar();
            this.loadMissions();
            this.loadRecentActivity();
            this.startRealTimeUpdates();
            this.updateSystemStatus();
            this.startLiveLogStream();
            this.updateResourceMetrics();
            this.initQuickActions();
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
                    icon: 'fa-chart-line',
                    message: 'Analysis Agent generated performance report',
                    time: '15 minutes ago'
                }
            ];
        },

        startRealTimeUpdates() {
            setInterval(() => {
                this.loadMissions();
                this.updateSystemStatus();
                this.updateResourceMetrics();
            }, 10000); // Update every 10 seconds
        },

        startLiveLogStream() {
            // Connect to the cognitive engine's live log stream
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
                // Try to reconnect after 5 seconds
                setTimeout(() => {
                    this.startLiveLogStream();
                }, 5000);
            };
        },

        addLiveLog(logData) {
            if (logData.type === 'keepalive') return;
            
            this.liveLogs.push(logData);
            if (this.liveLogs.length > 100) {
                this.liveLogs.shift();
            }
            this.updateLogDisplay();
        },

        updateLogDisplay() {
            const logContainer = document.getElementById('live-logs');
            if (!logContainer) return;

            const logEntries = this.liveLogs.map(log => {
                const timestamp = this.formatTimestamp(log.timestamp);
                const levelClass = log.level ? log.level.toLowerCase() : 'info';
                return `
                    <div class="log-entry">
                        <span class="log-timestamp">${timestamp}</span>
                        <span class="log-level ${levelClass}">${log.level || 'INFO'}</span>
                        <span class="log-message">${log.message}</span>
                    </div>
                `;
            }).join('');

            logContainer.innerHTML = logEntries;
            logContainer.scrollTop = logContainer.scrollHeight;
        },

        formatTimestamp(timestamp) {
            if (!timestamp) return '';
            const date = new Date(timestamp);
            return date.toLocaleTimeString();
        },

        async updateSystemStatus() {
            try {
                const response = await fetch('/health');
                if (response.ok) {
                    const data = await response.json();
                    this.systemStatus = {
                        apiServer: data.status === 'healthy' ? 'online' : 'offline',
                        cognitiveEngine: data.cognitive_engine === 'active' ? 'online' : 'offline',
                        database: 'online', // Assuming database is always online if API responds
                        aiModels: 'online' // Assuming AI models are ready if API responds
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
            // Update status badges based on system status
            const statusElements = document.querySelectorAll('.status-badge');
            statusElements.forEach(element => {
                const service = element.closest('.status-card').querySelector('h5').textContent.toLowerCase();
                if (service.includes('api')) {
                    element.className = `status-badge ${this.systemStatus.apiServer}`;
                    element.textContent = this.systemStatus.apiServer === 'online' ? 'Online' : 'Offline';
                } else if (service.includes('cognitive')) {
                    element.className = `status-badge ${this.systemStatus.cognitiveEngine}`;
                    element.textContent = this.systemStatus.cognitiveEngine === 'online' ? 'Active' : 'Inactive';
                } else if (service.includes('database')) {
                    element.className = `status-badge ${this.systemStatus.database}`;
                    element.textContent = this.systemStatus.database === 'online' ? 'Connected' : 'Disconnected';
                } else if (service.includes('ai models')) {
                    element.className = `status-badge ${this.systemStatus.aiModels}`;
                    element.textContent = this.systemStatus.aiModels === 'online' ? 'Ready' : 'Unavailable';
                }
            });
        },

        updateResourceMetrics() {
            // Simulate resource metrics updates
            this.resourceMetrics = {
                cpu: Math.floor(Math.random() * 30) + 30, // 30-60%
                memory: Math.floor(Math.random() * 40) + 40, // 40-80%
                network: Math.floor(Math.random() * 50) + 10 // 10-60%
            };

            // Update resource bars
            const resourceBars = document.querySelectorAll('.resource-fill');
            resourceBars.forEach((bar, index) => {
                const values = [this.resourceMetrics.cpu, this.resourceMetrics.memory, this.resourceMetrics.network];
                const percentage = values[index];
                bar.style.width = `${percentage}%`;
                
                // Update the percentage text
                const valueElement = bar.closest('.resource-item').querySelector('.resource-value');
                if (valueElement) {
                    valueElement.textContent = `${percentage}%`;
                }
            });
        },

        initQuickActions() {
            // Add event listeners for quick action buttons
            const quickActionButtons = document.querySelectorAll('.quick-actions .btn');
            quickActionButtons.forEach(button => {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    const action = button.textContent.trim();
                    this.handleQuickAction(action);
                });
            });
        },

        handleQuickAction(action) {
            switch(action) {
                case 'Create New Mission':
                    this.createNewMission();
                    break;
                case 'Generate Report':
                    this.generateReport();
                    break;
                case 'System Health Check':
                    this.performHealthCheck();
                    break;
                case 'Optimize Performance':
                    this.optimizePerformance();
                    break;
                default:
                    console.log(`Quick action: ${action}`);
            }
        },

        async createNewMission() {
            try {
                const response = await fetch('/api/missions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        prompt: 'New mission created via quick action',
                        agent_type: 'developer'
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    console.log('Mission created:', data);
                    this.loadMissions(); // Refresh missions list
                }
            } catch (error) {
                console.error('Error creating mission:', error);
            }
        },

        async generateReport() {
            try {
                const response = await fetch('/api/observability/report');
                if (response.ok) {
                    const data = await response.json();
                    console.log('Report generated:', data);
                    // Could trigger a download or display in modal
                }
            } catch (error) {
                console.error('Error generating report:', error);
            }
        },

        async performHealthCheck() {
            try {
                const response = await fetch('/health');
                if (response.ok) {
                    const data = await response.json();
                    console.log('Health check result:', data);
                    this.updateSystemStatus();
                }
            } catch (error) {
                console.error('Error performing health check:', error);
            }
        },

        async optimizePerformance() {
            try {
                const response = await fetch('/api/hybrid/analytics');
                if (response.ok) {
                    const data = await response.json();
                    console.log('Performance optimization data:', data);
                    // Could trigger optimization processes
                }
            } catch (error) {
                console.error('Error optimizing performance:', error);
            }
        },

        getActiveAgentCount() {
            return this.recentActivity.filter(activity => 
                activity.message.includes('Agent') && 
                !activity.message.includes('completed')
            ).length;
        },

        getSuccessRate() {
            if (this.missions.length === 0) return 0;
            const completedMissions = this.missions.filter(mission => mission.status === 'completed');
            return (completedMissions.length / this.missions.length) * 100;
        },

        getAverageResponseTime() {
            // Simulate average response time
            return (Math.random() * 2 + 0.5).toFixed(1);
        },

        getAllAgentStatuses() {
            return {
                planning: 'active',
                execution: 'active',
                review: 'active',
                debug: 'active',
                analysis: 'active'
            };
        },

        async submitMission(missionData) {
            try {
                const response = await fetch('/api/missions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(missionData)
                });
                
                if (response.ok) {
                    const data = await response.json();
                    console.log('Mission submitted:', data);
                    this.loadMissions();
                    return data;
                }
            } catch (error) {
                console.error('Error submitting mission:', error);
                throw error;
            }
        },

        async generateAIResponse(prompt) {
            try {
                const response = await fetch('/api/ai/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ prompt })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    return data.response;
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
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ code, language })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    return data.analysis;
                }
            } catch (error) {
                console.error('Error analyzing code:', error);
                throw error;
            }
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