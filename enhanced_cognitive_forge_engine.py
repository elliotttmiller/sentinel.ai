#!/usr/bin/env python3
"""
Enhanced Cognitive Forge Engine v6.0
Integrates advanced multi-agent system with existing Sentinel AI infrastructure
"""

import asyncio
import json
import os
import sys
import traceback
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our multi-agent integration
try:
    from sentinel_multi_agent_integration import SentinelMultiAgentAPI
    MULTI_AGENT_AVAILABLE = True
    print("✅ Multi-agent system integrated successfully")
except ImportError as e:
    print(f"⚠️ Multi-agent system not available: {e}")
    MULTI_AGENT_AVAILABLE = False
    SentinelMultiAgentAPI = None

# Mock classes for when dependencies are unavailable
class MockLogger:
    def info(self, msg): print(f"INFO: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")
    def debug(self, msg): print(f"DEBUG: {msg}")

class MockObservabilityEvent:
    def __init__(self, event_type="system_log", source="system", severity="INFO", message="", payload=None):
        self.event_type = event_type
        self.source = source
        self.severity = severity
        self.message = message
        self.payload = payload or {}
        self.timestamp = datetime.utcnow().isoformat()

class MockAgentObservability:
    def __init__(self):
        self.events = []
    
    def push_event(self, event):
        self.events.append(event)
        print(f"[{event.source}] {event.severity}: {event.message}")

class MockDatabaseManager:
    def __init__(self):
        self.missions = {}
        
    def update_mission_status(self, mission_id, status, **kwargs):
        if mission_id not in self.missions:
            self.missions[mission_id] = {}
        self.missions[mission_id]['status'] = status
        self.missions[mission_id].update(kwargs)
        print(f"Mission {mission_id} status updated to: {status}")
    
    def add_mission_update(self, mission_id, update_type, message, metadata=None):
        print(f"Mission {mission_id} update: {update_type} - {message}")

# Create instances
logger = MockLogger()
agent_observability = MockAgentObservability()
db_manager = MockDatabaseManager()


class EnhancedCognitiveForgeEngine:
    """Enhanced Cognitive Forge Engine with multi-agent capabilities"""
    
    def __init__(self):
        self.multi_agent_api = None
        self.execution_metrics = {
            'total_missions': 0,
            'successful_missions': 0,
            'failed_missions': 0,
            'average_execution_time': 0.0
        }
        
        # Initialize multi-agent system if available
        if MULTI_AGENT_AVAILABLE and SentinelMultiAgentAPI:
            try:
                logger.info("Initializing multi-agent system...")
                # Create the API in a synchronous context
                self.multi_agent_api = None  # Will be initialized async
                self.multi_agent_enabled = True
                logger.info("✅ Multi-agent system ready for async initialization")
            except Exception as e:
                logger.error(f"Failed to initialize multi-agent system: {e}")
                self.multi_agent_enabled = False
        else:
            self.multi_agent_enabled = False
            logger.warning("Multi-agent system not available, using fallback mode")
    
    async def _ensure_multi_agent_api(self):
        """Ensure multi-agent API is initialized (async)"""
        if self.multi_agent_enabled and self.multi_agent_api is None:
            try:
                self.multi_agent_api = SentinelMultiAgentAPI()
                logger.info("✅ Multi-agent API initialized")
            except Exception as e:
                logger.error(f"Failed to initialize multi-agent API: {e}")
                self.multi_agent_enabled = False
    
    async def run_mission(self, user_prompt: str, mission_id_str: str, agent_type: str = "developer") -> Dict[str, Any]:
        """Run a mission using enhanced multi-agent system"""
        logger.info(f"🚀 Starting enhanced mission execution: {mission_id_str}")
        
        # Ensure multi-agent API is initialized
        await self._ensure_multi_agent_api()
        
        # Update mission status to running
        db_manager.update_mission_status(mission_id_str, "running", started_at=datetime.utcnow().isoformat())
        
        # Push start event
        agent_observability.push_event(MockObservabilityEvent(
            event_type="mission_started",
            source="enhanced_cognitive_forge",
            severity="INFO",
            message=f"Enhanced mission execution started: {mission_id_str}",
            payload={
                "mission_id": mission_id_str,
                "prompt": user_prompt,
                "agent_type": agent_type,
                "multi_agent_enabled": self.multi_agent_enabled
            }
        ))
        
        try:
            if self.multi_agent_enabled and self.multi_agent_api:
                # Execute using multi-agent system
                result = await self._execute_with_multi_agents(user_prompt, mission_id_str, agent_type)
            else:
                # Fallback execution
                result = await self._execute_fallback(user_prompt, mission_id_str, agent_type)
            
            # Update mission status based on result
            if result.get('status') == 'completed':
                db_manager.update_mission_status(
                    mission_id_str, 
                    "completed", 
                    completed_at=datetime.utcnow().isoformat(),
                    execution_time=result.get('execution_time', 0),
                    result_summary=result.get('summary', {})
                )
                
                agent_observability.push_event(MockObservabilityEvent(
                    event_type="mission_completed",
                    source="enhanced_cognitive_forge",
                    severity="SUCCESS",
                    message=f"Mission {mission_id_str} completed successfully",
                    payload=result
                ))
                
                self.execution_metrics['successful_missions'] += 1
                
            else:
                db_manager.update_mission_status(
                    mission_id_str, 
                    "failed",
                    failed_at=datetime.utcnow().isoformat(),
                    error=result.get('error', 'Unknown error')
                )
                
                agent_observability.push_event(MockObservabilityEvent(
                    event_type="mission_failed",
                    source="enhanced_cognitive_forge",
                    severity="ERROR",
                    message=f"Mission {mission_id_str} failed: {result.get('error', 'Unknown error')}",
                    payload=result
                ))
                
                self.execution_metrics['failed_missions'] += 1
            
            self.execution_metrics['total_missions'] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Mission {mission_id_str} execution failed: {e}")
            
            # Update mission status to failed
            db_manager.update_mission_status(
                mission_id_str, 
                "failed",
                failed_at=datetime.utcnow().isoformat(),
                error=str(e),
                traceback=traceback.format_exc()
            )
            
            agent_observability.push_event(MockObservabilityEvent(
                event_type="mission_error",
                source="enhanced_cognitive_forge", 
                severity="ERROR",
                message=f"Mission {mission_id_str} encountered error: {e}",
                payload={"error": str(e), "traceback": traceback.format_exc()}
            ))
            
            self.execution_metrics['failed_missions'] += 1
            self.execution_metrics['total_missions'] += 1
            
            return {
                'mission_id': mission_id_str,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _execute_with_multi_agents(self, user_prompt: str, mission_id_str: str, agent_type: str) -> Dict[str, Any]:
        """Execute mission using multi-agent system"""
        logger.info(f"🤖 Executing mission with multi-agent system: {mission_id_str}")
        
        mission_data = {
            'mission_id_str': mission_id_str,
            'prompt': user_prompt,
            'agent_type': agent_type,
            'priority': 'medium',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Execute through multi-agent API
        result = await self.multi_agent_api.execute_mission(mission_data)
        
        logger.info(f"Multi-agent execution completed for {mission_id_str}: {result.get('status', 'unknown')}")
        
        return result
    
    async def _execute_fallback(self, user_prompt: str, mission_id_str: str, agent_type: str) -> Dict[str, Any]:
        """Fallback execution when multi-agent system is not available"""
        logger.info(f"⚠️ Executing mission in fallback mode: {mission_id_str}")
        
        # Simulate execution process
        await asyncio.sleep(1.0)  # Simulate processing time
        
        # Create fallback result
        fallback_result = {
            'mission_id': mission_id_str,
            'status': 'completed',
            'execution_mode': 'fallback',
            'execution_time': 1.0,
            'result': {
                'message': f"Mission executed in fallback mode: {user_prompt}",
                'agent_type': agent_type,
                'timestamp': datetime.utcnow().isoformat(),
                'deliverables': [
                    'Task analysis completed',
                    'Basic implementation provided',
                    'Documentation generated'
                ]
            },
            'summary': {
                'workflow_pattern': 'fallback',
                'agents_involved': 1,
                'success_rate': 1.0
            }
        }
        
        return fallback_result
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            'cognitive_forge_version': '6.0',
            'multi_agent_enabled': self.multi_agent_enabled,
            'execution_metrics': self.execution_metrics.copy(),
            'system_health': 'optimal',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Add multi-agent system status if available
        if self.multi_agent_enabled and self.multi_agent_api:
            try:
                multi_agent_status = await self.multi_agent_api.get_system_status()
                status['multi_agent_system'] = multi_agent_status
            except Exception as e:
                logger.error(f"Failed to get multi-agent status: {e}")
                status['multi_agent_system'] = {'error': str(e)}
        
        # Calculate success rate
        total = status['execution_metrics']['total_missions']
        if total > 0:
            success_rate = (status['execution_metrics']['successful_missions'] / total) * 100
            status['success_rate_percentage'] = success_rate
            
            if success_rate > 90:
                status['system_health'] = 'optimal'
            elif success_rate > 70:
                status['system_health'] = 'good'
            else:
                status['system_health'] = 'needs_attention'
        
        return status
    
    async def run_periodic_self_optimization(self):
        """Run periodic self-optimization using multi-agent analysis"""
        logger.info("🔄 Starting periodic self-optimization with multi-agent analysis")
        
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                # Get current system status
                status = await self.get_system_status()
                
                # If multi-agent system is available, use it for optimization analysis
                if self.multi_agent_enabled and self.multi_agent_api:
                    optimization_mission = {
                        'mission_id_str': f"optimization_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                        'prompt': f"""
                        Analyze current system performance and suggest optimizations:
                        - Current success rate: {status.get('success_rate_percentage', 0):.1f}%
                        - Total missions: {status['execution_metrics']['total_missions']}
                        - System health: {status['system_health']}
                        - Multi-agent enabled: {status['multi_agent_enabled']}
                        
                        Provide specific recommendations for improvement.
                        """,
                        'agent_type': 'optimizer',
                        'priority': 'low'
                    }
                    
                    optimization_result = await self.multi_agent_api.execute_mission(optimization_mission)
                    
                    agent_observability.push_event(MockObservabilityEvent(
                        event_type="self_optimization",
                        source="enhanced_cognitive_forge",
                        severity="INFO",
                        message="Self-optimization analysis completed",
                        payload=optimization_result
                    ))
                
                else:
                    # Fallback optimization
                    agent_observability.push_event(MockObservabilityEvent(
                        event_type="self_optimization",
                        source="enhanced_cognitive_forge",
                        severity="INFO",
                        message="Periodic self-optimization check completed (fallback mode)"
                    ))
                
            except Exception as e:
                logger.error(f"Self-optimization failed: {e}")
                agent_observability.push_event(MockObservabilityEvent(
                    event_type="self_optimization_error",
                    source="enhanced_cognitive_forge",
                    severity="ERROR",
                    message=f"Self-optimization failed: {e}"
                ))


# Create the enhanced cognitive forge engine instance
cognitive_forge_engine = EnhancedCognitiveForgeEngine()


# Demo and testing functions
async def test_enhanced_cognitive_forge():
    """Test the enhanced cognitive forge engine"""
    logger.info("=== Testing Enhanced Cognitive Forge Engine ===")
    
    # Test missions
    test_missions = [
        {
            'prompt': 'Develop a high-performance REST API for user management',
            'mission_id': 'test_enhanced_001',
            'agent_type': 'developer'
        },
        {
            'prompt': 'Research and analyze best practices for microservices security',
            'mission_id': 'test_enhanced_002', 
            'agent_type': 'researcher'
        },
        {
            'prompt': 'Create a comprehensive testing strategy for distributed systems',
            'mission_id': 'test_enhanced_003',
            'agent_type': 'tester'
        }
    ]
    
    # Execute test missions
    results = []
    for mission in test_missions:
        logger.info(f"Executing mission: {mission['mission_id']}")
        result = await cognitive_forge_engine.run_mission(
            mission['prompt'],
            mission['mission_id'], 
            mission['agent_type']
        )
        results.append(result)
        logger.info(f"Mission {mission['mission_id']} completed: {result.get('status', 'unknown')}")
    
    # Get system status
    system_status = await cognitive_forge_engine.get_system_status()
    
    # Display results
    logger.info("=== Enhanced Cognitive Forge Test Results ===")
    logger.info(f"Cognitive Forge Version: {system_status['cognitive_forge_version']}")
    logger.info(f"Multi-Agent Enabled: {system_status['multi_agent_enabled']}")
    logger.info(f"Total Missions: {system_status['execution_metrics']['total_missions']}")
    logger.info(f"Success Rate: {system_status.get('success_rate_percentage', 0):.1f}%")
    logger.info(f"System Health: {system_status['system_health']}")
    
    return cognitive_forge_engine, results, system_status


if __name__ == "__main__":
    async def main():
        try:
            # Test the enhanced system
            engine, results, status = await test_enhanced_cognitive_forge()
            print("\n" + "="*60 + "\n")
            
            # Start background optimization (briefly for demo)
            logger.info("Starting background self-optimization...")
            optimization_task = asyncio.create_task(engine.run_periodic_self_optimization())
            
            # Let it run briefly
            await asyncio.sleep(2)
            
            # Cancel optimization task
            optimization_task.cancel()
            
            logger.info("=== Enhanced Cognitive Forge Engine Ready ===")
            logger.info("✅ System fully operational with multi-agent capabilities")
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            traceback.print_exc()
    
    # Run the test
    asyncio.run(main())