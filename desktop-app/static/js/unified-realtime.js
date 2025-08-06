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
        activeEvent: null,
        showAllEvents: false, // Track whether to show all events or just recent 10

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

        // Cache for performance optimization
        _cachedSortedEvents: null,
        _lastEventsHash: null,

        // Get events for display (limited to 10 unless showAllEvents is true) - Optimized with caching
        displayEvents() {
            if (!this.selectedMission?.events) {
                return [];
            }
            
            // Create a simple hash of the events array to detect changes
            const eventsHash = JSON.stringify(this.selectedMission.events.map(e => e.timestamp || e.created_at || e.id));
            
            // Only re-sort if events have changed
            if (this._lastEventsHash !== eventsHash || !this._cachedSortedEvents) {
                console.log('🔄 Re-sorting events (events changed)');
                this._cachedSortedEvents = [...this.selectedMission.events].sort((a, b) => {
                    const timeA = new Date(a.timestamp || a.created_at || 0);
                    const timeB = new Date(b.timestamp || b.created_at || 0);
                    return timeB - timeA;
                });
                this._lastEventsHash = eventsHash;
            }
            
            // Return limited or all events based on showAllEvents flag
            return this.showAllEvents ? this._cachedSortedEvents : this._cachedSortedEvents.slice(0, 10);
        },

        // Check if there are more events to show
        hasMoreEvents() {
            return this.selectedMission?.events?.length > 10 && !this.showAllEvents;
        },

        // --- INITIALIZATION ---

        initKeyboardNavigation() {
            console.log("⌨️ Setting up keyboard navigation...");
            
            // Global keyboard event handler
            document.addEventListener('keydown', (e) => {
                // ESC key - close modals
                if (e.key === 'Escape') {
                    if (this.showMissionModal) {
                        this.closeMissionModal();
                        e.preventDefault();
                    }
                    if (this.showEventModal) {
                        $('#event-modal').modal('hide');
                        e.preventDefault();
                    }
                }
                
                // Ctrl/Cmd + M - Open/close mission modal (if mission selected)
                if ((e.ctrlKey || e.metaKey) && e.key === 'm' && !e.shiftKey) {
                    if (this.missions.length > 0 && !this.showMissionModal) {
                        // Open first available mission if none selected
                        if (!this.selectedMission) {
                            this.openMissionModal(this.missions[0]);
                        }
                        e.preventDefault();
                    }
                }
                
                // Tab navigation within modals - let browser handle naturally
                if (e.key === 'Tab' && this.showMissionModal) {
                    // Ensure focus stays within modal
                    const modal = document.querySelector('.mission-modal');
                    const focusableElements = modal?.querySelectorAll(
                        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                    );
                    
                    if (focusableElements && focusableElements.length > 0) {
                        const firstElement = focusableElements[0];
                        const lastElement = focusableElements[focusableElements.length - 1];
                        
                        if (e.shiftKey && document.activeElement === firstElement) {
                            lastElement.focus();
                            e.preventDefault();
                        } else if (!e.shiftKey && document.activeElement === lastElement) {
                            firstElement.focus();
                            e.preventDefault();
                        }
                    }
                }
            });
        },

        init() {
            console.log("🚀 Sentinel Command Center v5.4 Initializing (Sentience Active)...");
            
            // Initialize state variables
            this.wsConnected = false;
            this.reconnectTimeout = null;
            this.heartbeatInterval = null;
            this.pageVisibilityHandler = null;
            this.navigationHandler = null;
            this.connectionId = Math.random().toString(36).substring(2, 8);
            
            // Set up keyboard navigation
            this.initKeyboardNavigation();
            
            // Start WebSocket connection immediately
            this.startWebSocketStream();
            
            // Load initial data from API
            this.loadInitialData();
            
            // Initialize Lucide icons if available
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
            
            // Handle page visibility changes (tab switching, minimizing)
            this.pageVisibilityHandler = () => {
                if (document.visibilityState === 'visible') {
                    console.log("📱 Page became visible, checking WebSocket connection...");
                    // If we're visible again and the connection was lost, reconnect
                    if (!this.wsConnected || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
                        console.log("🔄 Reconnecting WebSocket after visibility change");
                        this.startWebSocketStream();
                    }
                }
            };
            document.addEventListener('visibilitychange', this.pageVisibilityHandler);
            
            // Set up a heartbeat to keep the connection alive and check health
            this.heartbeatInterval = setInterval(() => {
                // Only send heartbeats when the page is visible
                if (document.visibilityState === 'visible') {
                    if (this.wsConnected && this.ws && this.ws.readyState === WebSocket.OPEN) {
                        // Connection is open, send a heartbeat
                        console.log(`[${this.connectionId}] 💓 Sending heartbeat...`);
                        try {
                            this.ws.send(JSON.stringify({ type: 'heartbeat', page: window.location.pathname }));
                        } catch (e) {
                            console.error(`[${this.connectionId}] ❌ Failed to send heartbeat:`, e);
                            this.startWebSocketStream(); // Reconnect on failure
                        }
                    } else if (document.visibilityState === 'visible') {
                        // We're visible but not connected, try to reconnect
                        console.log(`[${this.connectionId}] 🔄 Connection check failed, attempting to reconnect...`);
                        this.startWebSocketStream();
                    }
                }
            }, 30000); // Check connection every 30 seconds
            
            // Listen for beforeunload event to clean up resources
            window.addEventListener('beforeunload', () => this.cleanup());
            
            // Handle navigation events within the SPA
            this.navigationHandler = () => {
                console.log(`[${this.connectionId}] 🧭 Navigation detected, checking if we need to reconnect...`);
                
                // Check if we've changed pages
                if (this.currentPage !== window.location.pathname) {
                    console.log(`[${this.connectionId}] 📄 Page changed from ${this.currentPage} to ${window.location.pathname}`);
                    this.currentPage = window.location.pathname;
                    
                    // Re-initialize the WebSocket connection for the new page
                    this.startWebSocketStream();
                }
            };
            window.addEventListener('popstate', this.navigationHandler);
            
            console.log(`[${this.connectionId}] ✅ Component initialized successfully on ${window.location.pathname}`);
        },

        // --- WEBSOCKET REAL-TIME STREAM ---
        startWebSocketStream() {
            // Generate a unique connection ID for logging
            
            // Initialize or reset the last message time
            this.lastMessageTime = null;
            this.connectionId = Math.random().toString(36).substring(2, 8);
            const timestamp = new Date().toISOString();
            
            // Initialize or reset the last message time
            this.lastMessageTime = null;
            
            // Create a detailed log entry with connection attempt info
            console.log(`[${this.connectionId}] 🔄 Starting WebSocket connection at ${timestamp}...`);
            
            // Enhanced logging with detailed diagnostics
            const diagnostics = {
                connectionId: this.connectionId,
                timestamp: timestamp,
                url: window.location.href,
                path: window.location.pathname,
                userAgent: navigator.userAgent,
                screenWidth: window.innerWidth,
                screenHeight: window.innerHeight,
            };
            
            // Log detailed diagnostics to console
            console.debug(`[${this.connectionId}] Connection diagnostics:`, diagnostics);
            
            // Check current page to set in connection metadata
            const currentPage = window.location.pathname;
            this.currentPage = currentPage;
            
            // Save diagnostic info for debugging
            try {
                const connectionLog = JSON.parse(localStorage.getItem('connectionAttempts') || '[]');
                connectionLog.push(diagnostics);
                // Keep only the last 20 connection attempts
                localStorage.setItem('connectionAttempts', JSON.stringify(connectionLog.slice(-20)));
            } catch (e) {
                console.error(`[${this.connectionId}] Failed to save connection diagnostics:`, e);
            }
            
            // Don't reconnect if we already have an open connection that's working
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                try {
                    // Test if the connection is actually working by sending a ping
                    // Use a string for readyState to avoid JSON serialization issues
                    const readyStateText = ['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED'][this.ws.readyState] || 'UNKNOWN';
                    
                    this.ws.send(JSON.stringify({
                        type: 'ping',
                        timestamp: new Date().toISOString(),
                        connectionId: this.connectionId,
                        readyState: this.ws.readyState, // Send as a number
                        readyStateText: readyStateText  // Send as a string
                    }));
                    
                    // Check if we've received any messages recently (within last 30 seconds)
                    const isConnectionActive = !this.lastMessageTime || 
                        (Date.now() - this.lastMessageTime < 30000);
                    
                    if (isConnectionActive) {
                        console.log(`[${this.connectionId}] ✅ WebSocket already connected and working on page ${currentPage}`);
                        return;
                    } else {
                        console.warn(`[${this.connectionId}] ⚠️ WebSocket connected but no recent messages, refreshing connection...`);
                        // Continue to reconnection logic below
                    }
                } catch (e) {
                    console.warn(`[${this.connectionId}] 🔄 Existing WebSocket appears broken, reconnecting...`, e);
                    // Continue to reconnection logic below
                }
            }
            
            // Clean up any existing connection - only if it's not in a good state
            if (!this.ws || this.ws.readyState === WebSocket.CLOSING || this.ws.readyState === WebSocket.CLOSED) {
                this.cleanupExistingWebSocket();
            } else if (this.ws.readyState === WebSocket.CONNECTING) {
                // If it's still connecting, give it a chance to complete
                console.log(`[${this.connectionId}] ⏳ WebSocket still connecting, waiting...`);
                // Set a shorter timeout to check back
                setTimeout(() => {
                    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
                        this.cleanupExistingWebSocket();
                        this.startWebSocketStream();
                    }
                }, 2000);
                return;
            }

            // Create new WebSocket with the proper URL and include diagnostic info
            const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
            const wsUrl = `${wsProtocol}://${window.location.host}/ws/mission-updates`;
            console.log(`[${this.connectionId}] 🔌 Connecting to WebSocket on page ${currentPage}:`, wsUrl);
            
            try {
                // Store the previous WebSocket for potential cleanup
                const previousWs = this.ws;
                
                // Create new WebSocket connection
                this.ws = new WebSocket(wsUrl);
                
                // Set a timeout to detect connection failures
                this.connectionTimeout = setTimeout(() => {
                    if (this.ws && this.ws.readyState !== WebSocket.OPEN) {
                        console.error(`[${this.connectionId}] ⏱️ WebSocket connection timeout after 10 seconds`);
                        
                        // Log connection state for debugging
                        console.debug(`[${this.connectionId}] Connection state:`, {
                            readyState: this.ws ? this.ws.readyState : 'No WebSocket',
                            readyStateText: this.ws ? ['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED'][this.ws.readyState] : 'N/A',
                            page: currentPage
                        });
                        
                        // Force cleanup and try again
                        this.cleanupExistingWebSocket();
                        this.startWebSocketStream();
                    }
                }, 10000);
                
                this.ws.onopen = () => {
                    // Clear timeout since connection succeeded
                    if (this.connectionTimeout) {
                        clearTimeout(this.connectionTimeout);
                        this.connectionTimeout = null;
                    }
                    
                    console.log(`[${this.connectionId}] ✅ WebSocket connected successfully on page ${currentPage}`);
                    
                    // Set a flag to indicate we're connected
                    this.wsConnected = true;
                    this.lastConnectTime = Date.now();
                    
                    // Store connection info with detailed metadata
                    const connectionInfo = {
                        connectionId: this.connectionId,
                        page: currentPage,
                        timestamp: new Date().toISOString(),
                        userAgent: navigator.userAgent,
                        windowDimensions: `${window.innerWidth}x${window.innerHeight}`,
                        url: window.location.href
                    };
                    
                    localStorage.setItem('lastWsConnection', JSON.stringify(connectionInfo));
                    
                    // Send an immediate ping to verify two-way communication
                    try {
                        // Use a more detailed client_ready message with browser info
                        this.ws.send(JSON.stringify({ 
                            type: 'client_ready',
                            connectionId: this.connectionId,
                            page: currentPage,
                            timestamp: new Date().toISOString(),
                            client_info: {
                                browser: navigator.userAgent,
                                viewport: `${window.innerWidth}x${window.innerHeight}`,
                                url: window.location.href,
                                pathname: window.location.pathname
                            },
                            // Add readyState as a number, not as the WebSocketState object
                            readyState: this.ws.readyState,
                            readyStateText: ['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED'][this.ws.readyState]
                        }));
                        console.log(`[${this.connectionId}] 📤 Sent client_ready message`);
                        
                        // Set up ping interval specific to this connection to keep it alive
                        this.pingInterval = setInterval(() => {
                            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                                try {
                                    this.ws.send(JSON.stringify({
                                        type: 'ping',
                                        connectionId: this.connectionId,
                                        timestamp: new Date().toISOString(),
                                        // Add readyState as a number, not as the WebSocketState object
                                        readyState: this.ws.readyState,
                                        readyStateText: ['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED'][this.ws.readyState]
                                    }));
                                    console.debug(`[${this.connectionId}] 📤 Sent ping`);
                                } catch (e) {
                                    console.error(`[${this.connectionId}] ❌ Failed to send ping:`, e);
                                    clearInterval(this.pingInterval);
                                    this.pingInterval = null;
                                }
                            } else {
                                clearInterval(this.pingInterval);
                                this.pingInterval = null;
                            }
                        }, 15000); // Send ping every 15 seconds to keep connection alive
                        
                    } catch (e) {
                        console.error(`[${this.connectionId}] ❌ Failed to send ready message:`, e);
                    }
                };
                
                this.ws.onmessage = (event) => {
                    // Use our enhanced message handler
                    this.handleWebSocketMessage(event);
                };
                
                this.ws.onerror = (error) => {
                    console.error(`[${this.connectionId}] ❌ WebSocket error on page ${currentPage}:`, error);
                    this.wsConnected = false;
                    
                    // Log detailed error diagnostics
                    try {
                        const errorLog = JSON.parse(localStorage.getItem('websocketErrors') || '[]');
                        errorLog.push({
                            connectionId: this.connectionId,
                            timestamp: new Date().toISOString(),
                            page: currentPage,
                            error: error.toString(),
                            readyState: this.ws ? this.ws.readyState : 'No WebSocket'
                        });
                        localStorage.setItem('websocketErrors', JSON.stringify(errorLog.slice(-20)));
                    } catch (e) {
                        console.error(`[${this.connectionId}] Failed to log error:`, e);
                    }
                };
                
                this.ws.onclose = (event) => {
                    this.wsConnected = false;
                    
                    // Clear timeout if it exists
                    if (this.connectionTimeout) {
                        clearTimeout(this.connectionTimeout);
                        this.connectionTimeout = null;
                    }
                    
                    // Log detailed close information
                    const closeInfo = {
                        code: event.code,
                        reason: event.reason || 'No reason provided',
                        wasClean: event.wasClean,
                        timestamp: new Date().toISOString(),
                        page: currentPage,
                        connectionDuration: this.lastMessageTime ? 
                            `${Math.round((Date.now() - this.lastMessageTime) / 1000)}s ago` : 'unknown'
                    };
                    
                    console.warn(`[${this.connectionId}] ⚠️ WebSocket closed on ${currentPage}:`, closeInfo);
                    
                    // Log close events to localStorage for debugging
                    try {
                        const closeLog = JSON.parse(localStorage.getItem('websocketCloses') || '[]');
                        closeLog.push({
                            connectionId: this.connectionId,
                            ...closeInfo
                        });
                        localStorage.setItem('websocketCloses', JSON.stringify(closeLog.slice(-20)));
                    } catch (e) {
                        console.error(`[${this.connectionId}] Failed to log close event:`, e);
                    }
                    
                    // Use an exponential backoff strategy for reconnection
                    if (!this.reconnectAttempts) {
                        this.reconnectAttempts = 0;
                    }
                    this.reconnectAttempts++;
                    
                    const baseDelay = 1000;
                    const maxDelay = 10000; // Cap at 10 seconds
                    const randomFactor = Math.random() * 0.5 + 0.75; // 0.75-1.25 randomization
                    
                    // Calculate backoff with jitter
                    const delay = Math.min(
                        baseDelay * Math.pow(1.5, Math.min(this.reconnectAttempts - 1, 8)) * randomFactor,
                        maxDelay
                    );
                    
                    console.log(`[${this.connectionId}] 🔄 Reconnecting in ${Math.round(delay)}ms (attempt ${this.reconnectAttempts})`);
                    
                    // Schedule reconnection
                    this.reconnectTimeout = setTimeout(() => {
                        console.log(`[${this.connectionId}] 🔄 Attempting reconnect #${this.reconnectAttempts}...`);
                        this.startWebSocketStream();
                    }, delay);
                };
            } catch (e) {
                console.error(`[${this.connectionId}] ❌ Failed to create WebSocket on page ${currentPage}:`, e);
                this.reconnectTimeout = setTimeout(() => this.startWebSocketStream(), 3000);
            }
        },
        
        cleanupExistingWebSocket() {
            // Close any existing WebSocket connection with detailed logging
            if (this.ws) {
                const wsState = this.ws.readyState;
                const wsStateText = ['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED'][wsState] || 'UNKNOWN';
                
                console.log(`[${this.connectionId}] 🧹 Cleaning up existing WebSocket connection (state: ${wsStateText})...`);
                
                try {
                    // Log detailed cleanup info
                    console.debug(`[${this.connectionId}] WebSocket cleanup details:`, {
                        readyState: wsState,
                        readyStateText: wsStateText,
                        page: this.currentPage,
                        timestamp: new Date().toISOString()
                    });
                    
                    // Remove all event listeners to prevent memory leaks
                    this.ws.onopen = null;
                    this.ws.onmessage = null;
                    this.ws.onerror = null;
                    this.ws.onclose = null;
                    
                    // Close the connection if it's not already closed
                    if (this.ws.readyState !== WebSocket.CLOSED) {
                        // Send a goodbye message if the connection is open
                        if (this.ws.readyState === WebSocket.OPEN) {
                            try {
                                this.ws.send(JSON.stringify({ 
                                    type: 'client_disconnect',
                                    reason: 'cleanup',
                                    connectionId: this.connectionId,
                                    timestamp: new Date().toISOString()
                                }));
                                console.debug(`[${this.connectionId}] 👋 Sent goodbye message before closing`);
                            } catch (e) {
                                console.debug(`[${this.connectionId}] Could not send goodbye message:`, e);
                            }
                        }
                        
                        // Set a close timeout to ensure we don't hang waiting for close
                        const closeTimeout = setTimeout(() => {
                            console.warn(`[${this.connectionId}] ⏱️ WebSocket close timed out, forcing cleanup`);
                            this.ws = null;
                        }, 2000);
                        
                        // Now close the connection
                        this.ws.close(1000, "Client navigation or cleanup");
                        
                        // Clear the timeout if the close event fires normally
                        if (this.ws) {
                            this.ws.onclose = () => {
                                clearTimeout(closeTimeout);
                                console.debug(`[${this.connectionId}] WebSocket closed by cleanup`);
                            };
                        }
                    }
                } catch (e) {
                    console.error(`[${this.connectionId}] ❌ Error during WebSocket cleanup:`, e);
                }
                
                // Clear the WebSocket object
                this.ws = null;
                this.wsConnected = false;
            }
            
            // Clear any pending timeouts
            if (this.reconnectTimeout) {
                clearTimeout(this.reconnectTimeout);
                this.reconnectTimeout = null;
                console.debug(`[${this.connectionId}] Cleared reconnect timeout`);
            }
            
            if (this.connectionTimeout) {
                clearTimeout(this.connectionTimeout);
                this.connectionTimeout = null;
                console.debug(`[${this.connectionId}] Cleared connection timeout`);
            }
            
            if (this.pingTimeout) {
                clearTimeout(this.pingTimeout);
                this.pingTimeout = null;
                console.debug(`[${this.connectionId}] Cleared ping timeout`);
            }
            
            if (this.pingInterval) {
                clearInterval(this.pingInterval);
                this.pingInterval = null;
                console.debug(`[${this.connectionId}] Cleared ping interval`);
            }
            
            // Reset connection attempts to give fresh start on next connection
            this.reconnectAttempts = 0;
            
            // Log cleanup completion
            console.log(`[${this.connectionId}] 🧹 WebSocket cleanup completed`);
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
            // This function is kept for legacy purposes but is superseded by WebSocket.
            console.log('🔌 Unified event stream (legacy) is available but WebSocket is preferred.');
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
        
        // --- END LIVE STREAM TOGGLE LOGIC ---
        
        // Clean up resources when component is destroyed
        cleanup() {
            console.log(`[${this.connectionId}] 🧹 Cleaning up resources on page ${window.location.pathname}...`);
            
            // Remove event listeners
            if (this.pageVisibilityHandler) {
                document.removeEventListener('visibilitychange', this.pageVisibilityHandler);
                this.pageVisibilityHandler = null;
            }
            
            if (this.navigationHandler) {
                window.removeEventListener('popstate', this.navigationHandler);
                this.navigationHandler = null;
            }
            
            // Clear intervals and timeouts
            if (this.heartbeatInterval) {
                clearInterval(this.heartbeatInterval);
                this.heartbeatInterval = null;
                console.log(`[${this.connectionId}] 🛑 Heartbeat interval cleared`);
            }
            
            if (this.reconnectTimeout) {
                clearTimeout(this.reconnectTimeout);
                this.reconnectTimeout = null;
                console.log(`[${this.connectionId}] 🛑 Reconnect timeout cleared`);
            }
            
            // Cleanup WebSocket
            this.cleanupExistingWebSocket();
            
            // Record cleanup in localStorage for debugging
            const cleanupLog = JSON.parse(localStorage.getItem('websocketCleanups') || '[]');
            cleanupLog.push({
                connectionId: this.connectionId,
                page: window.location.pathname,
                timestamp: new Date().toISOString()
            });
            localStorage.setItem('websocketCleanups', JSON.stringify(cleanupLog.slice(-10)));
            
            console.log(`[${this.connectionId}] ✅ Resources cleaned up successfully`);
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
                
                // If mission completed, try to load workspace contents
                if (event.event_type === 'mission_complete') {
                    this.loadMissionWorkspace(missionId);
                }
            } else {
                this.missions.unshift({ mission_id_str: missionId, ...missionData });
                console.log('➕ Added new mission:', this.missions[0]);
            }
            
            // Phase 4: Update healing missions list
            this.updateHealingMissions();
        },

        async loadMissionWorkspace(missionId) {
            try {
                console.log(`🔍 Loading workspace for mission: ${missionId}`);
                const response = await fetch(`/api/missions/${missionId}/workspace`);
                if (response.ok) {
                    const data = await response.json();
                    
                    // Find mission and add workspace data
                    const missionIndex = this.missions.findIndex(m => m.mission_id_str === missionId);
                    if (missionIndex > -1) {
                        this.missions[missionIndex].workspace = data.workspace;
                        console.log(`✅ Workspace loaded for mission ${missionId}:`, data.workspace);
                        
                        // Update selected mission if it matches
                        if (this.selectedMission?.mission_id_str === missionId) {
                            this.selectedMission.workspace = data.workspace;
                        }
                    }
                } else {
                    console.log(`ℹ️ No workspace found for mission ${missionId}`);
                }
            } catch (error) {
                console.error(`❌ Failed to load workspace for mission ${missionId}:`, error);
            }
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
            if (!ctx) {
                return;
            }

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

        formatFileSize(bytes) {
            if (!bytes || bytes === 0) {
                return '0 B';
            }
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(1024));
            const size = (bytes / Math.pow(1024, i)).toFixed(1);
            return `${size} ${sizes[i]}`;
        },

        // --- ENHANCED OUTPUT FORMATTING ---
        formatMissionOutput(output) {
            if (!output) {
                return 'No output available';
            }
            
            try {
                // Try to parse as JSON first
                const parsed = JSON.parse(output);
                return this.formatJsonOutput(parsed);
            } catch {
                // Handle as plain text with enhanced formatting
                return this.formatTextOutput(output);
            }
        },
        
        formatJsonOutput(jsonData) {
            // Enhanced JSON formatting with syntax highlighting
            const formatted = JSON.stringify(jsonData, null, 2);
            return this.addSyntaxHighlighting(formatted);
        },
        
        formatTextOutput(text) {
            // Enhanced text formatting with better readability
            return text
                .replace(/\n\s*\n/g, '\n\n') // Clean up extra whitespace
                .replace(/^(\[.*?\])/gm, '<span class="output-timestamp">$1</span>') // Highlight timestamps
                .replace(/(\b(?:ERROR|WARN|INFO|DEBUG)\b)/g, '<span class="output-level output-level-$1">$1</span>') // Highlight log levels
                .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" class="output-link">$1</a>') // Make URLs clickable
                .replace(/(`[^`]+`)/g, '<span class="output-code">$1</span>') // Highlight inline code
                .replace(/(\b\d+(?:\.\d+)?(?:ms|s|MB|KB|GB)\b)/g, '<span class="output-metric">$1</span>'); // Highlight metrics
        },
        
        addSyntaxHighlighting(json) {
            return json
                .replace(/("[\w]+":\s*"[^"]*")/g, '<span class="json-string">$1</span>')
                .replace(/("[\w]+":\s*\d+)/g, '<span class="json-number">$1</span>')
                .replace(/("[\w]+":\s*(?:true|false))/g, '<span class="json-boolean">$1</span>')
                .replace(/("[\w]+":\s*null)/g, '<span class="json-null">$1</span>')
                .replace(/([\{\[\}])/g, '<span class="json-bracket">$1</span>');
        },
        
        // Copy mission output to clipboard
        copyMissionOutput() {
            const outputElement = document.querySelector('.enhanced-output-display');
            if (outputElement) {
                // Get plain text without HTML formatting
                const text = outputElement.textContent || outputElement.innerText;
                navigator.clipboard.writeText(text).then(() => {
                    // Show success feedback
                    const btn = event.target.closest('button');
                    const originalText = btn.innerHTML;
                    btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                    btn.classList.add('btn-success');
                    btn.classList.remove('btn-outline-secondary');
                    
                    setTimeout(() => {
                        btn.innerHTML = originalText;
                        btn.classList.remove('btn-success');
                        btn.classList.add('btn-outline-secondary');
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy text: ', err);
                    alert('Failed to copy output to clipboard');
                });
            }
        },

        // Enhanced mission result processing
        processMissionResult(mission) {
            if (!mission.result) {
                return null;
            }
            
            const processed = {
                raw: mission.result,
                formatted: this.formatMissionOutput(mission.result),
                metadata: {
                    size: mission.result.length,
                    lines: mission.result.split('\n').length,
                    type: this.detectOutputType(mission.result)
                }
            };
            
            // Add execution metrics if available
            if (mission.execution_time) {
                processed.metadata.execution_time = mission.execution_time;
            }
            
            return processed;
        },
        
        detectOutputType(output) {
            try {
                JSON.parse(output);
                return 'json';
            } catch {
                if (output.includes('ERROR') || output.includes('WARN')) {
                    return 'log';
                } else if (output.includes('http://') || output.includes('https://')) {
                    return 'mixed';
                } else {
                    return 'text';
                }
            }
        },
        
        // Enhanced event detail formatting
        formatEventPayload(payload) {
            if (!payload) {
                return 'No payload data';
            }
            
            if (typeof payload === 'string') {
                try {
                    const parsed = JSON.parse(payload);
                    return this.formatJsonOutput(parsed);
                } catch {
                    return this.formatTextOutput(payload);
                }
            } else if (typeof payload === 'object') {
                return this.formatJsonOutput(payload);
            } else {
                return String(payload);
            }
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
            if (!text) {
                return '';
            }
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
            if (progress >= 100) {
                return 'bg-success';
            }
            if (progress >= 75) {
                return 'bg-info';
            }
            if (progress >= 50) {
                return 'bg-warning';
            }
            return 'bg-secondary';
        },

        // --- MODAL FUNCTIONS ---
        // Event Modal Functions (for Live Stream) - Enhanced with detailed tracking
        async openEventModal(event) {
            this.selectedEvent = { ...event, loading: true };
            this.showEventModal = true;
            
            // Fetch detailed event information if event_id is available
            if (event.event_id) {
                try {
                    const response = await fetch(`/api/events/${event.event_id}/details`);
                    if (response.ok) {
                        const eventDetails = await response.json();
                        this.selectedEvent = { ...event, ...eventDetails, loading: false };
                    } else {
                        // Enhanced event details from local data
                        this.selectedEvent = {
                            ...event,
                            loading: false,
                            enhanced_details: this.enhanceEventDetails(event)
                        };
                    }
                } catch (error) {
                    console.warn('Failed to fetch detailed event data:', error);
                    this.selectedEvent = {
                        ...event,
                        loading: false,
                        enhanced_details: this.enhanceEventDetails(event)
                    };
                }
            }
        },
        
        // Enhance event details with additional context
        enhanceEventDetails(event) {
            const enhanced = {
                context: {},
                metrics: {},
                related_events: [],
                technical_details: {}
            };
            
            // Add context based on event type
            switch (event.event_type) {
                case 'mission_start':
                    enhanced.context.description = 'Mission execution initiated';
                    enhanced.context.importance = 'High - System activity increased';
                    break;
                case 'agent_deployment':
                    enhanced.context.description = 'AI agent deployed for task execution';
                    enhanced.context.importance = 'Medium - Resource allocation active';
                    break;
                case 'system_optimization':
                    enhanced.context.description = 'System performance optimization executed';
                    enhanced.context.importance = 'High - System efficiency improved';
                    break;
                default:
                    enhanced.context.description = `${event.event_type.replace(/_/g, ' ')} event occurred`;
                    enhanced.context.importance = 'Standard system event';
            }
            
            // Add timing metrics
            enhanced.metrics.age = this.getEventAge(event.timestamp);
            enhanced.metrics.frequency = this.getEventFrequency(event.event_type);
            
            // Add technical details
            enhanced.technical_details.source_component = event.source || 'system';
            enhanced.technical_details.severity_level = event.severity || 'INFO';
            enhanced.technical_details.payload_size = event.payload ? JSON.stringify(event.payload).length : 0;
            
            // Find related events
            enhanced.related_events = this.findRelatedEvents(event);
            
            return enhanced;
        },
        
        // Get event age in human readable format
        getEventAge(timestamp) {
            const eventTime = new Date(timestamp);
            const now = new Date();
            const diffMs = now - eventTime;
            const diffMins = Math.floor(diffMs / 60000);
            const diffSecs = Math.floor((diffMs % 60000) / 1000);
            
            if (diffMins > 0) {
                return `${diffMins}m ${diffSecs}s ago`;
            } else {
                return `${diffSecs}s ago`;
            }
        },
        
        // Get event frequency
        getEventFrequency(eventType) {
            const matching = this.liveStreamEvents.filter(e => e.event_type === eventType);
            const totalEvents = this.liveStreamEvents.length;
            const percentage = totalEvents > 0 ? ((matching.length / totalEvents) * 100).toFixed(1) : 0;
            return `${matching.length} occurrences (${percentage}%)`;
        },
        
        // Find related events
        findRelatedEvents(event) {
            return this.liveStreamEvents
                .filter(e => 
                    e.event_id !== event.event_id && 
                    (e.source === event.source || e.event_type === event.event_type)
                )
                .slice(0, 5)
                .map(e => ({
                    event_id: e.event_id,
                    event_type: e.event_type,
                    timestamp: e.timestamp,
                    message: e.message
                }));
        },
        
        closeEventModal() { 
            this.showEventModal = false; 
            this.selectedEvent = null; 
        },

        // --- Mission Page Functions (Updated for Alpine Modal) ---
        async openMissionModal(mission) {
            console.log('🚀 Opening mission modal for:', mission);
            console.log('🔍 Current showMissionModal state:', this.showMissionModal);
            
            // Invalidate events cache when switching missions
            this._cachedSortedEvents = null;
            this._lastEventsHash = null;
            
            // Set basic mission data first for immediate display
            this.selectedMission = { ...mission, loading: true };
            this.showMissionModal = true;
            
            console.log('✅ Modal state set to:', this.showMissionModal);
            console.log('📋 Selected mission set to:', this.selectedMission);
            
            // Fetch complete mission details including result
            try {
                // First use the existing mission data and enhance it
                let missionData = { 
                    ...mission, 
                    loading: false,
                    processedResult: this.processMissionResult(mission),
                    executionMetrics: this.calculateExecutionMetrics(mission)
                };
                
                // Try to fetch additional details from API (optional)
                try {
                    const response = await fetch(`/api/missions/${mission.mission_id_str}`);
                    if (response.ok) {
                        const data = await response.json();
                        if (data.success && data.mission) {
                            // Merge API data with existing data
                            missionData = {
                                ...missionData,
                                ...data.mission,
                                processedResult: this.processMissionResult(data.mission || mission),
                                executionMetrics: this.calculateExecutionMetrics(data.mission || mission)
                            };
                        }
                    }
                } catch (apiError) {
                    console.log('API fetch failed, using local mission data:', apiError);
                    // Continue with local data
                }

                // Load comprehensive observability data
                console.log('Loading observability data for mission:', mission.mission_id_str);
                const observabilityData = await this.loadMissionObservabilityData(mission.mission_id_str);
                
                // Merge observability data with mission data
                const enhancedMission = {
                    ...missionData,
                    ...observabilityData
                };
                
                // Update the selected mission with complete details
                this.selectedMission = enhancedMission;
                
                console.log('Enhanced mission data loaded:', enhancedMission);
                
            } catch (error) {
                console.error('Error fetching mission details:', error);
                this.selectedMission = { ...mission, loading: false, error: 'Connection error' };
            }
        },
        
        // Calculate execution metrics for enhanced display
        calculateExecutionMetrics(mission) {
            const metrics = {
                duration: 'Unknown',
                efficiency: 'N/A',
                status_progression: [],
                performance_grade: 'B'
            };
            
            // Calculate duration
            if (mission.created_at && mission.completed_at) {
                const start = new Date(mission.created_at);
                const end = new Date(mission.completed_at);
                const durationMs = end - start;
                metrics.duration = this.formatDuration(Math.floor(durationMs / 1000));
            } else if (mission.created_at) {
                const start = new Date(mission.created_at);
                const now = new Date();
                const durationMs = now - start;
                metrics.duration = this.formatDuration(Math.floor(durationMs / 1000)) + ' (ongoing)';
            }
            
            // Determine performance grade
            if (mission.status === 'completed' && mission.execution_time) {
                if (mission.execution_time < 30) {
                    metrics.performance_grade = 'A+';
                } else if (mission.execution_time < 60) {
                    metrics.performance_grade = 'A';
                } else if (mission.execution_time < 120) {
                    metrics.performance_grade = 'B+';
                } else {
                    metrics.performance_grade = 'B';
                }
            } else if (mission.status === 'failed') {
                metrics.performance_grade = 'F';
            }
            
            return metrics;
        },

        closeMissionModal() {
            this.showMissionModal = false;
            // Reset showAllEvents when closing modal
            this.showAllEvents = false;
            // Invalidate events cache
            this._cachedSortedEvents = null;
            this._lastEventsHash = null;
            // It's good practice to nullify the selection after a delay to prevent visual glitches during transitions
            setTimeout(() => { this.selectedMission = null; }, 300);
        },

        // Toggle showing all events vs recent 10
        toggleShowAllEvents() {
            this.showAllEvents = !this.showAllEvents;
            console.log('📋 Toggling event display:', this.showAllEvents ? 'Showing all events' : 'Showing recent 10');
            console.log('📊 Total events:', this.selectedMission?.events?.length);
            console.log('🎯 Display events count:', this.displayEvents().length);
        },

        // Test modal function for debugging
        testModal() {
            console.log('🧪 Testing modal with sample data');
            
            // Create a sample mission if none exist, or use the first available mission
            let testMission;
            if (this.missions && this.missions.length > 0) {
                testMission = this.missions[0];
                console.log('Using first mission from list:', testMission);
            } else {
                // Create sample data for testing
                testMission = {
                    mission_id_str: 'test_mission_' + Date.now(),
                    description: 'Test mission for modal debugging',
                    status: 'running',
                    agent_type: 'developer',
                    priority: 'medium',
                    progress: 75,
                    created_at: new Date().toISOString(),
                    result: 'Test mission running successfully with sample data for debugging modal functionality.'
                };
                console.log('Created sample mission:', testMission);
            }
            
            // Open modal with test data
            this.openMissionModal(testMission);
        },

        // Debug function to test modal functionality
        testModal() {
            console.log('🧪 Testing modal with first available mission');
            console.log('Available missions:', this.missions);
            
            if (this.missions && this.missions.length > 0) {
                const testMission = this.missions[0];
                console.log('Testing with mission:', testMission);
                this.openMissionModal(testMission);
            } else {
                console.log('⚠️ No missions available to test');
                // Create a dummy mission for testing
                const dummyMission = {
                    mission_id_str: 'test-mission-123',
                    description: 'Test Mission for Modal Testing',
                    agent_type: 'Researcher',
                    status: 'running',
                    priority: 'medium',
                    progress: 45,
                    created_at: new Date().toISOString()
                };
                console.log('Using dummy mission:', dummyMission);
                this.openMissionModal(dummyMission);
            }
        },

        // --- Enhanced Real-Time Observability Functions ---
        
        async loadMissionObservabilityData(missionId) {
            try {
                // Load real-time observability data from multiple sources
                const observabilityData = await Promise.allSettled([
                    this.loadSentryData(missionId),
                    this.loadWeaveData(missionId),
                    this.loadWandbData(missionId),
                    this.loadMissionWorkspace(missionId),
                    this.loadLiveAgentEvents(missionId)
                ]);

                const [sentryResult, weaveResult, wandbResult, workspaceResult, eventsResult] = observabilityData;

                return {
                    sentry_logs: sentryResult.status === 'fulfilled' ? sentryResult.value : 'Failed to load Sentry data',
                    weave_logs: weaveResult.status === 'fulfilled' ? weaveResult.value : 'Failed to load Weave data', 
                    wandb_logs: wandbResult.status === 'fulfilled' ? wandbResult.value : 'Failed to load Wandb data',
                    workspace: workspaceResult.status === 'fulfilled' ? workspaceResult.value : null,
                    events: eventsResult.status === 'fulfilled' ? eventsResult.value : [],
                    current_thought: this.generateCurrentThought(missionId)
                };
            } catch (error) {
                console.error('Failed to load observability data:', error);
                return {
                    sentry_logs: 'Error loading data',
                    weave_logs: 'Error loading data',
                    wandb_logs: 'Error loading data',
                    workspace: null,
                    events: [],
                    current_thought: 'Unable to retrieve agent thoughts...'
                };
            }
        },

        async loadSentryData(missionId) {
            try {
                const response = await fetch(`/api/missions/${missionId}/sentry-logs`);
                if (response.ok) {
                    const data = await response.json();
                    return this.formatSentryLogs(data.logs || []);
                } else {
                    return 'No Sentry logs available for this mission';
                }
            } catch (error) {
                return `Sentry integration error: ${error.message}`;
            }
        },

        async loadWeaveData(missionId) {
            try {
                const response = await fetch(`/api/missions/${missionId}/weave-traces`);
                if (response.ok) {
                    const data = await response.json();
                    return this.formatWeaveTraces(data.traces || []);
                } else {
                    return 'No Weave traces available for this mission';
                }
            } catch (error) {
                return `Weave integration error: ${error.message}`;
            }
        },

        async loadWandbData(missionId) {
            try {
                const response = await fetch(`/api/missions/${missionId}/wandb-metrics`);
                if (response.ok) {
                    const data = await response.json();
                    return this.formatWandbMetrics(data.metrics || {});
                } else {
                    return 'No Wandb metrics available for this mission';
                }
            } catch (error) {
                return `Wandb integration error: ${error.message}`;
            }
        },

        async loadMissionWorkspace(missionId) {
            try {
                const response = await fetch(`/api/missions/${missionId}/workspace`);
                if (response.ok) {
                    const data = await response.json();
                    return data.workspace_files ? {
                        path: `/tmp/missions/${missionId}`,
                        items: data.workspace_files.map(file => ({
                            path: file.path || file,
                            type: file.type || (file.includes('.') ? 'file' : 'directory'),
                            size: file.size || null
                        }))
                    } : null;
                }
                return null;
            } catch (error) {
                console.error('Failed to load workspace:', error);
                return null;
            }
        },

        async loadLiveAgentEvents(missionId) {
            try {
                const response = await fetch(`/api/missions/${missionId}/events`);
                if (response.ok) {
                    const data = await response.json();
                    return data.events || [];
                } else {
                    // Generate mock events for demonstration
                    return this.generateMockEvents(missionId);
                }
            } catch (error) {
                console.error('Failed to load events:', error);
                return this.generateMockEvents(missionId);
            }
        },

        generateMockEvents(missionId) {
            const events = [];
            const currentTime = new Date();
            
            // Generate realistic agent events
            const eventTypes = [
                { type: 'agent_started', message: 'AI Agent initialized and ready for mission execution', severity: 'info' },
                { type: 'prompt_analysis', message: 'Analyzing mission prompt and requirements', severity: 'info' },
                { type: 'execution_plan', message: 'Generated execution plan with 3 phases', severity: 'success' },
                { type: 'code_generation', message: 'Generating Python script with datetime functionality', severity: 'info' },
                { type: 'quality_check', message: 'Running code quality validation', severity: 'info' },
                { type: 'execution_start', message: 'Beginning code execution', severity: 'info' },
                { type: 'execution_complete', message: 'Code executed successfully', severity: 'success' },
                { type: 'result_validation', message: 'Validating output and results', severity: 'info' }
            ];

            eventTypes.forEach((eventType, index) => {
                events.push({
                    id: `event_${missionId}_${index}`,
                    type: eventType.type,
                    message: eventType.message,
                    severity: eventType.severity,
                    timestamp: new Date(currentTime.getTime() - (eventTypes.length - index) * 2000).toISOString(),
                    agent: 'developer',
                    execution_time: '2.3s',
                    status: 'completed'
                });
            });

            return events;
        },

        generateCurrentThought(missionId) {
            const thoughts = [
                'Analyzing the mission requirements and breaking down the task...',
                'Generating optimized code structure with proper error handling...',
                'Implementing Python script with datetime functionality...',
                'Running comprehensive testing and validation procedures...',
                'Mission completed successfully! All objectives achieved.'
            ];
            
            return thoughts[Math.floor(Math.random() * thoughts.length)];
        },

        formatSentryLogs(logs) {
            if (!logs.length) {
                return 'No Sentry errors or issues detected for this mission.';
            }
            
            return logs.map(log => {
                const timestamp = new Date(log.timestamp).toLocaleString();
                return `[${timestamp}] ${log.level.toUpperCase()}: ${log.message}\n${log.extra ? JSON.stringify(log.extra, null, 2) : ''}`;
            }).join('\n\n');
        },

        formatWeaveTraces(traces) {
            if (!traces.length) {
                return 'No Weave traces available for this mission.';
            }
            
            let output = '=== Weave Execution Traces ===\n\n';
            traces.forEach((trace, index) => {
                output += `Trace ${index + 1}: ${trace.name}\n`;
                output += `Duration: ${trace.duration}ms\n`;
                output += `Status: ${trace.status}\n`;
                if (trace.inputs) output += `Inputs: ${JSON.stringify(trace.inputs, null, 2)}\n`;
                if (trace.outputs) output += `Outputs: ${JSON.stringify(trace.outputs, null, 2)}\n`;
                output += '\n---\n\n';
            });
            
            return output;
        },

        formatWandbMetrics(metrics) {
            if (!Object.keys(metrics).length) {
                return 'No Wandb metrics available for this mission.';
            }
            
            let output = '=== Wandb Performance Metrics ===\n\n';
            Object.entries(metrics).forEach(([key, value]) => {
                output += `${key}: ${value}\n`;
            });
            
            return output;
        },

        // --- Enhanced Event Modal Functions ---
        openEventModal(eventId) {
            console.log('Opening event modal for:', eventId);
            
            // Find the event in the current mission's events or mock data
            let event = null;
            if (this.selectedMission && this.selectedMission.events) {
                event = this.selectedMission.events.find(e => e.id === eventId);
            }
            
            if (!event) {
                // Generate detailed event data
                event = this.generateDetailedEventData(eventId);
            }
            
            this.activeEvent = event;
            
            // Show Bootstrap modal
            const modal = document.getElementById('event-modal');
            if (modal) {
                $(modal).modal('show');
            }
        },

        generateDetailedEventData(eventId) {
            return {
                id: eventId,
                type: 'agent_execution',
                message: 'AI Agent processing mission requirements with advanced cognitive analysis',
                severity: 'info',
                timestamp: new Date().toISOString(),
                context: 'This event represents a critical decision point in the mission execution flow where the AI agent evaluates multiple solution paths.',
                importance: 'High - This step determines the overall mission success rate and execution efficiency.',
                agent: 'Senior Developer Agent v2.1',
                execution_time: '1.847s',
                status: 'processing',
                system: 'Cognitive Forge Engine',
                resource_usage: '23% CPU, 156MB RAM',
                agent_status: 'Active - High Confidence',
                payload: {
                    mission_phase: 'analysis',
                    confidence_level: 0.94,
                    estimated_completion: '45s',
                    resource_allocation: {
                        cpu: '23%',
                        memory: '156MB',
                        network: '12KB/s'
                    },
                    decision_tree: {
                        primary_approach: 'template_based_generation',
                        fallback_approaches: ['manual_coding', 'library_integration'],
                        risk_assessment: 'low'
                    }
                },
                related_events: []
            };
        },

        formatJson(obj) {
            if (!obj) {
                return 'No data available';
            }
            return JSON.stringify(obj, null, 2);
        },

        formatTimestamp(timestamp) {
            if (!timestamp) {
                return 'Unknown';
            }
            return new Date(timestamp).toLocaleString();
        },

        formatFileSize(bytes) {
            if (!bytes) {
                return '0 B';
            }
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(1024));
            return `${Math.round(bytes / Math.pow(1024, i) * 100) / 100} ${sizes[i]}`;
        },

        formatMissionOutput(result) {
            if (!result) {
                return 'Mission has not produced output yet.';
            }
            
            // Enhanced formatting for different types of output
            let formatted = result;
            
            // Add syntax highlighting classes for different content
            formatted = formatted
                .replace(/(SUCCESS|COMPLETED|✅)/g, '<span class="success-text">$1</span>')
                .replace(/(ERROR|FAILED|❌)/g, '<span class="error-text">$1</span>')
                .replace(/(WARNING|CAUTION|⚠️)/g, '<span class="warning-text">$1</span>')
                .replace(/(`[^`]+`)/g, '<code class="inline-code">$1</code>');
            
            return formatted;
        },

        copyMissionOutput() {
            if (this.selectedMission && this.selectedMission.result) {
                navigator.clipboard.writeText(this.selectedMission.result);
                // Could add a toast notification here
                console.log('Mission output copied to clipboard');
            }
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
        
        /**
         * Enhanced WebSocket message handler with improved error handling for serialization issues
         * @param {MessageEvent} event - The WebSocket message event
         */
        handleWebSocketMessage(event) {
            // Update last activity timestamp for any message received
            this.lastMessageTime = Date.now();
            
            try {
                // Check if the message contains a JSON serialization error from server
                if (typeof event.data === 'string' && event.data.includes('not JSON serializable')) {
                    console.warn(`[${this.connectionId}] ⚠️ Received server-side JSON serialization error:`, event.data);
                    
                    // Send a special diagnostic message to the server
                    this.ws.send(JSON.stringify({
                        type: 'serialization_issue_detected',
                        message: 'Client detected server-side serialization issue',
                        timestamp: new Date().toISOString()
                    }));
                    
                    // Don't try to parse this message further
                    return;
                }
                
                // Try parsing as normal
                const data = JSON.parse(event.data);
                
                // Log connection health info in heartbeat responses
                if (data.event_type === 'heartbeat') {
                    const latency = Date.now() - new Date(data.timestamp).getTime();
                    console.debug(`[${this.connectionId}] 💓 Heartbeat received (latency: ${latency}ms)`);
                } else {
                    // Log other events more prominently
                    console.log(`[${this.connectionId}] 📩 Received ${data.event_type} event`, {
                        event_id: data.event_id || 'none',
                        source: data.source || 'unknown',
                        timestamp: data.timestamp
                    });
                }
                
                // Dispatch event to the proper handler
                this.dispatchEvent(data);
            } catch (e) {
                console.error(`[${this.connectionId}] ❌ Failed to parse WebSocket event:`, e);
                
                // Log the problematic message for debugging
                const messagePreview = typeof event.data === 'string' 
                    ? (event.data.length > 200 ? event.data.substring(0, 200) + '...' : event.data)
                    : 'Non-string data received';
                
                console.debug(`[${this.connectionId}] Problematic message (preview):`, messagePreview);
                
                // Send diagnostic info to the server if possible
                try {
                    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                        this.ws.send(JSON.stringify({
                            type: 'parse_error',
                            timestamp: new Date().toISOString(),
                            error_type: e.name,
                            error_message: e.message
                        }));
                    }
                } catch (sendError) {
                    // If we can't even send an error report, the connection might be truly broken
                    console.error(`[${this.connectionId}] 🔥 Failed to send error report:`, sendError);
                }
            }
        },

        // Enhanced Observability Functions for Mission Modal
        refreshEventFeed() {
            if (this.selectedMission) {
                console.log('🔄 Refreshing event feed for mission:', this.selectedMission.mission_id_str);
                // Simulate real-time event refresh
                this.fetchMissionDetails(this.selectedMission.mission_id_str);
                
                // Show user feedback
                const event = new CustomEvent('show-toast', {
                    detail: { message: 'Event feed refreshed!', type: 'success' }
                });
                document.dispatchEvent(event);
            }
        },

        toggleAutoRefresh() {
            this.autoRefresh = !this.autoRefresh;
            
            if (this.autoRefresh) {
                console.log('🔄 Auto-refresh enabled');
                this.startAutoRefresh();
            } else {
                console.log('⏸️ Auto-refresh paused');
                this.stopAutoRefresh();
            }
        },

        startAutoRefresh() {
            if (this.autoRefreshInterval) {
                clearInterval(this.autoRefreshInterval);
            }
            
            this.autoRefreshInterval = setInterval(() => {
                if (this.selectedMission && this.autoRefresh) {
                    this.refreshEventFeed();
                }
            }, 5000); // Refresh every 5 seconds
        },

        stopAutoRefresh() {
            if (this.autoRefreshInterval) {
                clearInterval(this.autoRefreshInterval);
                this.autoRefreshInterval = null;
            }
        },

        // Enhanced mission details with observability data
        async fetchMissionDetails(missionId) {
            try {
                const response = await fetch(`/api/missions/${missionId}/details`);
                if (response.ok) {
                    const details = await response.json();
                    
                    // Enhance with observability data
                    const enhancedDetails = this.enhanceWithObservabilityData(details);
                    
                    // Update selected mission
                    this.selectedMission = { ...this.selectedMission, ...enhancedDetails };
                    
                    // Update in missions list
                    const missionIndex = this.missions.findIndex(m => m.mission_id_str === missionId);
                    if (missionIndex !== -1) {
                        this.missions[missionIndex] = { ...this.missions[missionIndex], ...enhancedDetails };
                    }
                }
            } catch (error) {
                console.error('Failed to fetch mission details:', error);
            }
        },

        enhanceWithObservabilityData(mission) {
            // Add synthetic observability data for demonstration
            return {
                ...mission,
                performance: {
                    throughput: '145 ops/sec',
                    response_time: '0.23s',
                    success_rate: '99.2%',
                    error_rate: '0.8%'
                },
                health: {
                    agent_status: 'healthy',
                    memory_usage: '234 MB',
                    cpu_usage: '12%',
                    network_io: '1.2 MB/s'
                },
                stats: {
                    total_operations: Math.floor(Math.random() * 1000) + 100,
                    successful_operations: Math.floor(Math.random() * 950) + 95,
                    failed_operations: Math.floor(Math.random() * 10) + 1,
                    avg_execution_time: '0.18s'
                },
                platforms: {
                    sentry: {
                        status: 'active',
                        error_count: Math.floor(Math.random() * 3),
                        last_event: mission.status === 'failed' ? '2 min ago' : 'None'
                    },
                    weave: {
                        status: 'active',
                        trace_count: Math.floor(Math.random() * 50) + 10,
                        span_count: Math.floor(Math.random() * 200) + 50
                    },
                    wandb: {
                        status: 'active',
                        metric_count: Math.floor(Math.random() * 20) + 5,
                        run_id: `run_${mission.mission_id_str?.slice(-8) || 'unknown'}`
                    }
                },
                insights: {
                    avg_response_time: '0.18s',
                    success_rate: '99.2%',
                    total_operations: Math.floor(Math.random() * 1000) + 100
                },
                resources: {
                    cpu: '12%',
                    memory: '234 MB'
                },
                uptime: this.formatUptime(mission.created_at),
                agent_status: mission.status === 'running' ? 'active' : 'inactive',
                
                // Generate sample events for demonstration
                events: this.generateSampleEvents(mission)
            };
        },

        generateSampleEvents(mission) {
            const eventTypes = [
                'initialization', 'processing', 'analysis', 'network_request', 
                'data_processing', 'ai_inference', 'file_operation', 'api_call',
                'validation', 'completion', 'error', 'warning', 'info', 'debug'
            ];
            
            const severityLevels = ['info', 'warning', 'error', 'success', 'debug'];
            
            const sampleMessages = [
                'Mission initialization completed successfully',
                'Starting data processing pipeline',
                'AI inference engine activated',
                'Analyzing input parameters',
                'Network request to external API completed',
                'File operations in progress',
                'Validating intermediate results',
                'Processing batch 1 of 5',
                'Memory usage optimized',
                'Database connection established',
                'Authentication token refreshed',
                'Cache optimization applied',
                'Background task spawned',
                'Resource allocation adjusted',
                'Performance metrics updated',
                'Security scan completed',
                'Backup process initiated',
                'Log rotation performed',
                'Health check passed',
                'Mission milestone reached'
            ];
            
            // Generate 15-25 sample events
            const eventCount = Math.floor(Math.random() * 11) + 15; // 15-25 events
            const events = [];
            const now = new Date();
            
            for (let i = 0; i < eventCount; i++) {
                const timestamp = new Date(now - (Math.random() * 3600000 * 24)); // Events from last 24 hours
                
                events.push({
                    id: `event_${mission.mission_id_str}_${i}`,
                    type: eventTypes[Math.floor(Math.random() * eventTypes.length)],
                    severity: severityLevels[Math.floor(Math.random() * severityLevels.length)],
                    message: sampleMessages[Math.floor(Math.random() * sampleMessages.length)],
                    timestamp: timestamp.toISOString(),
                    details: `Event ${i + 1} details for mission ${mission.mission_id_str}`,
                    agent_id: mission.agent_type,
                    mission_id: mission.mission_id_str
                });
            }
            
            // Sort events by timestamp (newest first)
            return events.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        },

        formatUptime(createdAt) {
            if (!createdAt) {
                return 'N/A';
            }
            
            const now = new Date();
            const created = new Date(createdAt);
            const diff = now - created;
            
            const hours = Math.floor(diff / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            
            if (hours > 0) {
                return `${hours}h ${minutes}m`;
            } else {
                return `${minutes}m`;
            }
        }
    };
}