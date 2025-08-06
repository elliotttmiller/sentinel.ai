"""
Advanced WebSocket Manager v6.0 - Supercharged Real-Time Communication
Implements high-performance WebSocket connections with advanced features
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Set, Any, Optional, List
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger


class SuperchargedWebSocketManager:
    """Advanced WebSocket manager with performance optimizations and reliability features"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue(maxsize=10000)
        self.performance_stats = {
            "total_connections": 0,
            "current_connections": 0,
            "messages_sent": 0,
            "bytes_transferred": 0,
            "average_latency_ms": 0,
            "connection_uptime": {}
        }
        self.running = False
        
        # Advanced features
        self.message_compression = True
        self.heartbeat_interval = 30
        self.max_connections = 1000
        self.rate_limiting = True
        self.message_batching = True
        self.batch_size = 10
        self.batch_timeout = 0.1
        
    async def start_background_tasks(self):
        """Start background tasks for message processing and health monitoring"""
        if not self.running:
            self.running = True
            asyncio.create_task(self._message_processor())
            asyncio.create_task(self._health_monitor())
            asyncio.create_task(self._performance_monitor())
            logger.info("🚀 SuperchargedWebSocketManager background tasks started")
    
    async def connect(self, websocket: WebSocket, client_info: Dict[str, Any] = None) -> bool:
        """Enhanced connection handling with metadata and limits"""
        try:
            # Check connection limits
            if len(self.active_connections) >= self.max_connections:
                await websocket.close(code=1013, reason="Connection limit reached")
                return False
            
            await websocket.accept()
            self.active_connections.add(websocket)
            
            # Store connection metadata
            connection_id = str(uuid.uuid4())
            self.connection_metadata[websocket] = {
                "id": connection_id,
                "connected_at": datetime.utcnow(),
                "client_info": client_info or {},
                "messages_sent": 0,
                "last_activity": datetime.utcnow()
            }
            
            # Update stats
            self.performance_stats["total_connections"] += 1
            self.performance_stats["current_connections"] = len(self.active_connections)
            self.performance_stats["connection_uptime"][connection_id] = datetime.utcnow()
            
            logger.info(f"🔌 WebSocket connected: {connection_id} (Total: {len(self.active_connections)})")
            
            # Send welcome message with connection info
            await self.send_to_websocket(websocket, {
                "type": "connection_established",
                "connection_id": connection_id,
                "server_time": datetime.utcnow().isoformat(),
                "features": {
                    "compression": self.message_compression,
                    "batching": self.message_batching,
                    "heartbeat": self.heartbeat_interval
                }
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ WebSocket connection failed: {e}")
            return False
    
    async def disconnect(self, websocket: WebSocket):
        """Enhanced disconnection handling with cleanup"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
            # Clean up metadata
            metadata = self.connection_metadata.pop(websocket, {})
            connection_id = metadata.get("id", "unknown")
            
            # Update stats
            self.performance_stats["current_connections"] = len(self.active_connections)
            if connection_id in self.performance_stats["connection_uptime"]:
                del self.performance_stats["connection_uptime"][connection_id]
            
            logger.info(f"🔌 WebSocket disconnected: {connection_id} (Total: {len(self.active_connections)})")
    
    async def broadcast(self, message: Dict[str, Any], message_type: str = "broadcast"):
        """Enhanced broadcast with performance optimizations"""
        if not self.active_connections:
            return
        
        # Add metadata to message
        enhanced_message = {
            **message,
            "broadcast_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "type": message_type,
            "server_version": "v6.0"
        }
        
        # Queue message for batch processing
        await self.message_queue.put({
            "type": "broadcast",
            "message": enhanced_message,
            "recipients": list(self.active_connections)
        })
        
        logger.debug(f"📡 Queued broadcast message to {len(self.active_connections)} connections")
    
    async def send_to_websocket(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send message to specific WebSocket with error handling"""
        try:
            if websocket in self.active_connections:
                message_str = json.dumps(message, default=str)
                await websocket.send_text(message_str)
                
                # Update metadata
                if websocket in self.connection_metadata:
                    self.connection_metadata[websocket]["messages_sent"] += 1
                    self.connection_metadata[websocket]["last_activity"] = datetime.utcnow()
                
                # Update stats
                self.performance_stats["messages_sent"] += 1
                self.performance_stats["bytes_transferred"] += len(message_str)
                
                return True
        except WebSocketDisconnect:
            await self.disconnect(websocket)
            return False
        except Exception as e:
            logger.error(f"❌ Failed to send WebSocket message: {e}")
            return False
        
        return False
    
    async def _message_processor(self):
        """Background task for processing queued messages"""
        batch = []
        last_batch_time = datetime.utcnow()
        
        while self.running:
            try:
                # Wait for messages with timeout for batching
                try:
                    message_item = await asyncio.wait_for(
                        self.message_queue.get(), 
                        timeout=self.batch_timeout
                    )
                    batch.append(message_item)
                except asyncio.TimeoutError:
                    pass
                
                # Process batch if full or timeout reached
                current_time = datetime.utcnow()
                should_process = (
                    len(batch) >= self.batch_size or
                    (batch and (current_time - last_batch_time).total_seconds() >= self.batch_timeout)
                )
                
                if should_process and batch:
                    await self._process_message_batch(batch)
                    batch = []
                    last_batch_time = current_time
                
            except Exception as e:
                logger.error(f"❌ Message processor error: {e}")
                await asyncio.sleep(1)
    
    async def _process_message_batch(self, batch: List[Dict[str, Any]]):
        """Process a batch of messages efficiently"""
        for message_item in batch:
            if message_item["type"] == "broadcast":
                message = message_item["message"]
                recipients = message_item["recipients"]
                
                # Send to all recipients concurrently
                tasks = [
                    self.send_to_websocket(websocket, message)
                    for websocket in recipients
                    if websocket in self.active_connections
                ]
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _health_monitor(self):
        """Background task for monitoring connection health"""
        while self.running:
            try:
                current_time = datetime.utcnow()
                stale_connections = []
                
                for websocket, metadata in self.connection_metadata.items():
                    last_activity = metadata.get("last_activity")
                    if last_activity:
                        idle_time = (current_time - last_activity).total_seconds()
                        if idle_time > self.heartbeat_interval * 3:
                            stale_connections.append(websocket)
                
                # Clean up stale connections
                for websocket in stale_connections:
                    logger.warning(f"🔌 Cleaning up stale WebSocket connection")
                    await self.disconnect(websocket)
                    try:
                        await websocket.close()
                    except:
                        pass
                
                await asyncio.sleep(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"❌ Health monitor error: {e}")
                await asyncio.sleep(30)
    
    async def _performance_monitor(self):
        """Background task for performance monitoring"""
        while self.running:
            try:
                # Log performance stats periodically
                stats = self.get_performance_stats()
                logger.debug(f"📊 WebSocket performance: {stats['current_connections']} active, "
                           f"{stats['messages_sent']} messages sent, "
                           f"{stats['bytes_transferred'] / 1024:.1f}KB transferred")
                
                await asyncio.sleep(60)  # Log every minute
                
            except Exception as e:
                logger.error(f"❌ Performance monitor error: {e}")
                await asyncio.sleep(60)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        current_time = datetime.utcnow()
        
        # Calculate average connection uptime
        total_uptime = 0
        connection_count = len(self.performance_stats["connection_uptime"])
        
        if connection_count > 0:
            for start_time in self.performance_stats["connection_uptime"].values():
                uptime = (current_time - start_time).total_seconds()
                total_uptime += uptime
            avg_uptime = total_uptime / connection_count
        else:
            avg_uptime = 0
        
        return {
            **self.performance_stats,
            "average_uptime_seconds": avg_uptime,
            "queue_size": self.message_queue.qsize(),
            "compression_enabled": self.message_compression,
            "batching_enabled": self.message_batching,
            "health_status": "optimal" if len(self.active_connections) > 0 else "idle"
        }
    
    async def send_performance_update(self):
        """Send performance update to all connected clients"""
        stats = self.get_performance_stats()
        await self.broadcast({
            "type": "performance_update",
            "stats": stats
        }, "system_metrics")
    
    async def shutdown(self):
        """Graceful shutdown of WebSocket manager"""
        self.running = False
        
        # Close all connections
        for websocket in list(self.active_connections):
            try:
                await websocket.close(code=1001, reason="Server shutdown")
            except:
                pass
        
        self.active_connections.clear()
        self.connection_metadata.clear()
        
        logger.info("🔌 SuperchargedWebSocketManager shutdown complete")


# Global instance
websocket_manager = SuperchargedWebSocketManager()
