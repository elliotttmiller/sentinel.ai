#!/usr/bin/env python3
"""
WebSocket Fix Script for Sentinel

This script applies fixes to the unified-realtime.js file to properly handle
WebSocketState serialization issues. It makes specific, targeted changes to:

1. Add lastMessageTime tracking in startWebSocketStream
2. Replace the WebSocket onmessage handler with a call to a new method
3. Add the new handleWebSocketMessage method to the application object
"""

import os
import re
import sys
import shutil
from datetime import datetime

# Set file paths
JS_FILE = os.path.join('static', 'js', 'unified-realtime.js')
BACKUP_FILE = os.path.join('static', 'js', f'unified-realtime.js.bak-{datetime.now().strftime("%Y%m%d-%H%M%S")}')

# Enhanced message handler implementation
HANDLER_CODE = """
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
"""

def apply_fixes():
    """Apply WebSocket fixes to the JavaScript file."""
    
    # First, back up the file
    if not os.path.exists(JS_FILE):
        print(f"ERROR: Could not find {JS_FILE}")
        return False

    try:
        shutil.copy(JS_FILE, BACKUP_FILE)
        print(f"Created backup at {BACKUP_FILE}")
    except Exception as e:
        print(f"ERROR: Failed to create backup: {e}")
        return False
    
    # Read the file
    try:
        with open(JS_FILE, 'r', encoding='utf-8') as f:
            js_content = f.read()
    except Exception as e:
        print(f"ERROR: Failed to read {JS_FILE}: {e}")
        return False
    
    # Apply Fix 1: Add lastMessageTime initialization
    start_ws_pattern = r'(startWebSocketStream\(\)\s*\{\s*[^\n]*\n\s*// Generate a unique connection ID for logging)'
    init_timestamp = r'\1\n            \n            // Initialize or reset the last message time\n            this.lastMessageTime = null;'
    js_content = re.sub(start_ws_pattern, init_timestamp, js_content)
    
    # Apply Fix 2: Replace onmessage handler
    onmessage_pattern = r'(this\.ws\.onmessage = \(event\) => \{)[\s\S]*?(this\.ws\.onerror = \(error\) => \{)'
    new_handler = r'\1\n                    // Use our enhanced message handler\n                    this.handleWebSocketMessage(event);\n                };\n                \n                \2'
    js_content = re.sub(onmessage_pattern, new_handler, js_content)
    
    # Apply Fix 3: Add the enhanced message handler
    end_pattern = r'(preflightCheckPrompt[\s\S]*?\n        \}\n    \};)'
    handler_addition = r'\1\n\n' + HANDLER_CODE + r'\n    };'
    js_content = re.sub(end_pattern, handler_addition, js_content)
    
    # Write the modified content back
    try:
        with open(JS_FILE, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print(f"Successfully applied WebSocket fixes to {JS_FILE}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to write to {JS_FILE}: {e}")
        # Restore the backup
        try:
            shutil.copy(BACKUP_FILE, JS_FILE)
            print(f"Restored original file from backup")
        except Exception as restore_error:
            print(f"ERROR: Failed to restore backup: {restore_error}")
        return False

if __name__ == "__main__":
    print("=== Sentinel WebSocket Fix Script ===")
    if apply_fixes():
        print("✅ All fixes applied successfully!")
        sys.exit(0)
    else:
        print("❌ Failed to apply fixes. See errors above.")
        sys.exit(1)
