function settingsApp() {
    return {
        settings: {
            aiModel: 'gemini-1.5-pro',
            logLevel: 'info',
            refreshInterval: 10,
            theme: 'dark',
            dataRetention: 30,
            notifications: {
                email: true,
                push: true,
                sound: false
            },
            security: {
                sessionTimeout: 30,
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

        init() {
            this.loadSettings();
        },

        async loadSettings() {
            try {
                const response = await fetch('/api/settings');
                if (response.ok) {
                    const data = await response.json();
                    this.settings = { ...this.settings, ...data };
                }
            } catch (error) {
                console.error('Error loading settings:', error);
                // Use default settings if API is not available
            }
        },

        async saveSettings() {
            try {
                const response = await fetch('/api/settings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(this.settings)
                });
                
                if (response.ok) {
                    this.showNotification('Settings saved successfully!', 'success');
                    
                    // Apply theme change immediately
                    if (this.settings.theme === 'light') {
                        document.body.classList.add('light-theme');
                    } else {
                        document.body.classList.remove('light-theme');
                    }
                    
                    // Apply refresh interval
                    if (window.sentinelApp) {
                        window.sentinelApp.startRealTimeUpdates();
                    }
                }
            } catch (error) {
                console.error('Error saving settings:', error);
                this.showNotification('Failed to save settings', 'error');
            }
        },

        async resetSettings() {
            if (confirm('Are you sure you want to reset all settings to defaults?')) {
                this.settings = {
                    aiModel: 'gemini-1.5-pro',
                    logLevel: 'info',
                    refreshInterval: 10,
                    theme: 'dark',
                    dataRetention: 30,
                    notifications: {
                        email: true,
                        push: true,
                        sound: false
                    },
                    security: {
                        sessionTimeout: 30,
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
                };
                
                this.showNotification('Settings reset to defaults', 'info');
            }
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