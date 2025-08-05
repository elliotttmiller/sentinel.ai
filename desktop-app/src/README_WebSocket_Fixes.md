# WebSocket Handling Improvements

This document provides guidance on fixing the WebSocket serialization issues in the Sentinel application.

## The Issue

We've identified a bug where WebSocket messages containing WebSocketState objects cannot be properly serialized to JSON by the server. This is because WebSocketState is a special enum-like object that Python's default JSON serializer doesn't know how to handle.

## Server-Side Fix

We've already implemented the server-side fix in `websocket_helpers.py` which provides a custom JSON encoder for WebSocketState objects. This ensures that all WebSocket messages sent from the server are properly serialized.

## Client-Side Fix

To improve client-side handling and make the application more resilient against serialization errors, we recommend the following changes to `unified-realtime.js`:

1. Initialize `lastMessageTime` tracking in the `startWebSocketStream()` function
2. Replace the WebSocket `onmessage` handler with a call to a new `handleWebSocketMessage()` method
3. Add the new `handleWebSocketMessage()` method to the application object

### Implementation Details

#### 1. Track Last Message Time

In `startWebSocketStream()`, add:

```javascript
// Initialize or reset the last message time
this.lastMessageTime = null;
```

#### 2. Use WebSocket ReadyState Text

When sending connection info, use text representation of WebSocket state:

```javascript
// Send readable state as well as numeric state
readyState: this.ws.readyState,
readyStateText: ['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED'][this.ws.readyState]
```

#### 3. Replace onmessage Handler

Replace the existing WebSocket onmessage handler with:

```javascript
this.ws.onmessage = (event) => {
    // Use our enhanced message handler
    this.handleWebSocketMessage(event);
};
```

#### 4. Add Enhanced Message Handler

Add a new method to the application object:

```javascript
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
}
```

## Testing the Fix

To test the fix:

1. Start the Sentinel server
2. Open the application in a browser
3. Open the browser's developer console
4. Verify that WebSocket connections are established successfully
5. Check for any serialization errors in the console output

## Troubleshooting

If you still see issues after implementing these fixes, consider:

1. Restarting the Sentinel server
2. Clearing your browser cache
3. Checking the server logs for additional error information
