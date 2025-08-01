function missionsApp() {
    return {
        missions: [],
        newMission: {
            prompt: '',
            agent_type: 'developer',
            priority: 'medium'
        },

        init() {
            this.loadMissions();
            this.startRealTimeUpdates();
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

        async createMission() {
            if (!this.newMission.prompt.trim()) {
                alert('Please enter a mission description');
                return;
            }

            try {
                const response = await fetch('/api/missions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        prompt: this.newMission.prompt,
                        agent_type: this.newMission.agent_type,
                        priority: this.newMission.priority
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    console.log('Mission created:', data);
                    
                    // Reset form
                    this.newMission = {
                        prompt: '',
                        agent_type: 'developer',
                        priority: 'medium'
                    };
                    
                    // Refresh missions list
                    this.loadMissions();
                    
                    // Show success message
                    this.showNotification('Mission created successfully!', 'success');
                }
            } catch (error) {
                console.error('Error creating mission:', error);
                this.showNotification('Failed to create mission', 'error');
            }
        },

        async refreshMissions() {
            await this.loadMissions();
            this.showNotification('Missions refreshed', 'info');
        },

        async clearCompleted() {
            if (confirm('Are you sure you want to clear all completed missions?')) {
                this.missions = this.missions.filter(mission => mission.status !== 'completed');
                this.showNotification('Completed missions cleared', 'info');
            }
        },

        viewMission(mission) {
            // Open mission details modal or navigate to mission detail page
            console.log('Viewing mission:', mission);
            this.showNotification('Mission details opened', 'info');
        },

        async pauseMission(mission) {
            try {
                const response = await fetch(`/api/missions/${mission.mission_id_str}/pause`, {
                    method: 'POST'
                });
                
                if (response.ok) {
                    await this.loadMissions();
                    this.showNotification('Mission paused', 'warning');
                }
            } catch (error) {
                console.error('Error pausing mission:', error);
                this.showNotification('Failed to pause mission', 'error');
            }
        },

        async cancelMission(mission) {
            if (confirm('Are you sure you want to cancel this mission?')) {
                try {
                    const response = await fetch(`/api/missions/${mission.mission_id_str}/cancel`, {
                        method: 'POST'
                    });
                    
                    if (response.ok) {
                        await this.loadMissions();
                        this.showNotification('Mission cancelled', 'warning');
                    }
                } catch (error) {
                    console.error('Error cancelling mission:', error);
                    this.showNotification('Failed to cancel mission', 'error');
                }
            }
        },

        getStatusClass(status) {
            switch (status) {
                case 'completed':
                    return 'badge-success';
                case 'active':
                case 'running':
                    return 'badge-primary';
                case 'pending':
                    return 'badge-warning';
                case 'failed':
                case 'cancelled':
                    return 'badge-danger';
                default:
                    return 'badge-secondary';
            }
        },

        getPriorityClass(priority) {
            switch (priority) {
                case 'critical':
                    return 'badge-danger';
                case 'high':
                    return 'badge-warning';
                case 'medium':
                    return 'badge-info';
                case 'low':
                    return 'badge-secondary';
                default:
                    return 'badge-secondary';
            }
        },

        getProgress(mission) {
            switch (mission.status) {
                case 'completed':
                    return 100;
                case 'active':
                case 'running':
                    return 75;
                case 'pending':
                    return 25;
                case 'failed':
                case 'cancelled':
                    return 0;
                default:
                    return 0;
            }
        },

        formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        },

        getActiveCount() {
            return this.missions.filter(m => m.status === 'active' || m.status === 'running').length;
        },

        getCompletedCount() {
            return this.missions.filter(m => m.status === 'completed').length;
        },

        getPendingCount() {
            return this.missions.filter(m => m.status === 'pending').length;
        },

        getSuccessRate() {
            if (this.missions.length === 0) return 0;
            const completed = this.missions.filter(m => m.status === 'completed').length;
            return Math.round((completed / this.missions.length) * 100);
        },

        startRealTimeUpdates() {
            setInterval(() => {
                this.loadMissions();
            }, 10000); // Update every 10 seconds
        },

        showNotification(message, type = 'info') {
            // Create a simple notification
            const notification = document.createElement('div');
            notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
            notification.style.position = 'fixed';
            notification.style.top = '20px';
            notification.style.right = '20px';
            notification.style.zIndex = '9999';
            notification.innerHTML = `
                ${message}
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            `;
            
            document.body.appendChild(notification);
            
            // Auto-remove after 3 seconds
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 3000);
        }
    };
} 