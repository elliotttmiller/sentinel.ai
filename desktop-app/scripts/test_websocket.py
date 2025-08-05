#!/usr/bin/env python3
"""
WebSocket Diagnostic Tool for Sentinel
Provides a standalone test client for WebSocket connections

Usage:
    python test_websocket.py [--host localhost] [--port 8001]
"""

import asyncio
import json
import logging
import sys
import time
import websockets
import argparse
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("websocket-test")

# Parse command line arguments
parser = argparse.ArgumentParser(description='Test WebSocket connections to Sentinel server')
parser.add_argument('--host', default='localhost', help='Host to connect to')
parser.add_argument('--port', default='8001', help='Port to connect to')
parser.add_argument('--path', default='ws/mission-updates', help='WebSocket path')
parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
args = parser.parse_args()

if args.verbose:
    logger.setLevel(logging.DEBUG)

async def test_websocket_connection():
    """Test WebSocket connection to the server"""
    host = args.host
    port = args.port
    path = args.path
    
    uri = f"ws://{host}:{port}/{path}"
    logger.info(f"Connecting to {uri}...")
    
    try:
        connection_start = time.time()
        async with websockets.connect(uri, ping_interval=20, ping_timeout=30) as websocket:
            connection_time = time.time() - connection_start
            logger.info(f"✅ Connected to {uri} in {connection_time:.2f}s")
            
            # Start a task to receive messages
            receiver_task = asyncio.create_task(receive_messages(websocket))
            
            # Keep track of messages
            messages_received = 0
            connection_start_time = time.time()
            
            try:
                # Send a hello message
                await websocket.send(json.dumps({
                    "type": "client_hello",
                    "client": "diagnostic-tool",
                    "timestamp": datetime.utcnow().isoformat()
                }))
                logger.info("👋 Sent hello message")
                
                # Keep the connection open and send heartbeats
                while True:
                    # Send a heartbeat every 30 seconds
                    await asyncio.sleep(30)
                    
                    # Send a heartbeat
                    await websocket.send(json.dumps({
                        "type": "heartbeat",
                        "client": "diagnostic-tool",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                    
                    # Log connection status
                    uptime = time.time() - connection_start_time
                    logger.info(f"💓 Heartbeat sent. Connection uptime: {uptime:.1f}s, Messages received: {messages_received}")
                    
            except asyncio.CancelledError:
                logger.info("Connection closed by user")
            except Exception as e:
                logger.error(f"❌ Error during connection: {e}")
            finally:
                if not receiver_task.done():
                    receiver_task.cancel()
                    try:
                        await receiver_task
                    except asyncio.CancelledError:
                        pass
                    
    except Exception as e:
        logger.error(f"❌ Failed to connect: {e}")
        return False
        
    return True

async def receive_messages(websocket):
    """Receive and log messages from the WebSocket"""
    messages_received = 0
    try:
        async for message in websocket:
            messages_received += 1
            try:
                data = json.loads(message)
                event_type = data.get("event_type", "unknown")
                
                # Only show non-heartbeat messages in detail
                if event_type == "heartbeat":
                    if args.verbose:
                        logger.debug(f"📥 Received heartbeat")
                else:
                    logger.info(f"📥 Received {event_type} event: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                logger.warning(f"📥 Received non-JSON message: {message[:100]}...")
    except asyncio.CancelledError:
        logger.debug("Message receiver cancelled")
    except Exception as e:
        logger.error(f"❌ Error receiving message: {e}")
    finally:
        logger.info(f"Total messages received: {messages_received}")

async def main():
    """Run the WebSocket test"""
    logger.info("=== Sentinel WebSocket Diagnostic Tool ===")
    
    # Show configuration
    logger.info(f"Host:      {args.host}")
    logger.info(f"Port:      {args.port}")
    logger.info(f"Path:      {args.path}")
    logger.info(f"Verbose:   {'Yes' if args.verbose else 'No'}")
    logger.info("======================================")
    
    try:
        # Test the WebSocket connection
        success = await test_websocket_connection()
        
        if success:
            logger.info("✅ WebSocket test completed successfully")
        else:
            logger.error("❌ WebSocket test failed")
            
    except KeyboardInterrupt:
        logger.info("👋 Test interrupted by user")
    except Exception as e:
        logger.error(f"❌ Unhandled error: {e}")

if __name__ == "__main__":
    # Set the event loop policy for Windows if needed
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run the main function
    asyncio.run(main())
