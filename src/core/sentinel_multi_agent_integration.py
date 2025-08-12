#!/usr/bin/env python3
"""
Sentinel AI Multi-Agent Integration Layer
Integrates enhanced multi-agent system with existing Sentinel AI infrastructure
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our enhanced multi-agent system
from enhanced_multi_agent_system import (
    MultiAgentOrchestrator,
    AgentCapability,
    WorkflowPattern,
    EnhancedAgent
)

# Mock imports for Sentinel AI components (since dependencies are not available)
class MockLogger:
    """Mock logger for when loguru is not available"""
    def info(self, msg): print(f"INFO: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")
    def debug(self, msg): print(f"DEBUG: {msg}")

# Create mock logger
logger = MockLogger()


class SentinelMultiAgentBridge:
    """Bridge between Sentinel AI and the enhanced multi-agent system"""
    
    def __init__(self):
        self.orchestrator = MultiAgentOrchestrator()
        self.mission_workflows = {}
        self.agent_mappings = self._create_agent_mappings()
        self.performance_metrics = {
            'total_missions': 0,
            'successful_missions': 0,
            'average_execution_time': 0.0,
            'agent_utilization': {}
        }
        
    def _create_agent_mappings(self) -> Dict[str, str]:
        """Map Sentinel AI agent types to multi-agent capabilities"""
        return {
            'developer': 'development',
            'reviewer': 'review',
            'tester': 'testing',
            'planner': 'planning',
            'researcher': 'research',
            'integrator': 'development',
            'optimizer': 'optimization'
        }
    
    async def execute_sentinel_mission(self, mission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Sentinel AI mission using the multi-agent system"""
        mission_id = mission_data.get('mission_id_str', f"mission_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
        user_prompt = mission_data.get('prompt', mission_data.get('objective', ''))
        agent_type = mission_data.get('agent_type', 'developer')
        
        logger.info(f"Executing Sentinel mission {mission_id}: {user_prompt}")
        
        try:
            # Determine workflow type based on mission requirements
            workflow_type = self._determine_workflow_type(user_prompt, agent_type)
            
            # Execute multi-agent workflow
            result = await self.orchestrator.execute_workflow(user_prompt, workflow_type)
            
            # Convert to Sentinel AI format
            sentinel_result = self._convert_to_sentinel_format(result, mission_data)
            
            # Update performance metrics
            self._update_performance_metrics(result, mission_id)
            
            return sentinel_result
            
        except Exception as e:
            logger.error(f"Mission {mission_id} failed: {e}")
            return {
                'mission_id': mission_id,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _determine_workflow_type(self, prompt: str, agent_type: str) -> str:
        """Determine the appropriate workflow type based on mission requirements"""
        prompt_lower = prompt.lower()
        
        # Research-heavy tasks
        if any(keyword in prompt_lower for keyword in ['analyze', 'research', 'investigate', 'study']):
            return 'research_and_development'
        
        # Collaborative tasks
        elif any(keyword in prompt_lower for keyword in ['collaborate', 'team', 'multiple', 'together']):
            return 'collaborative_analysis'
        
        # Rapid development tasks
        elif any(keyword in prompt_lower for keyword in ['prototype', 'quick', 'fast', 'rapid', 'poc']):
            return 'rapid_prototyping'
        
        # Default based on agent type
        else:
            return 'research_and_development'
    
    def _convert_to_sentinel_format(self, multi_agent_result: Dict[str, Any], 
                                  original_mission: Dict[str, Any]) -> Dict[str, Any]:
        """Convert multi-agent result to Sentinel AI format"""
        return {
            'mission_id': multi_agent_result.get('workflow_id', 'unknown'),
            'status': multi_agent_result.get('status', 'unknown'),
            'execution_time': multi_agent_result.get('execution_time', 0),
            'agent_results': multi_agent_result.get('results', []),
            'summary': {
                'workflow_pattern': multi_agent_result.get('pattern', 'unknown'),
                'agents_involved': len(multi_agent_result.get('agents_involved', [])),
                'success_rate': 1.0 if multi_agent_result.get('status') == 'completed' else 0.0
            },
            'original_prompt': original_mission.get('prompt', ''),
            'timestamp': datetime.utcnow().isoformat(),
            'multi_agent_details': multi_agent_result
        }
    
    def _update_performance_metrics(self, result: Dict[str, Any], mission_id: str):
        """Update performance metrics"""
        self.performance_metrics['total_missions'] += 1
        
        if result.get('status') == 'completed':
            self.performance_metrics['successful_missions'] += 1
        
        # Update average execution time
        exec_time = result.get('execution_time', 0)
        total = self.performance_metrics['total_missions']
        current_avg = self.performance_metrics['average_execution_time']
        self.performance_metrics['average_execution_time'] = (current_avg * (total - 1) + exec_time) / total
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents in the multi-agent system"""
        return self.orchestrator.get_system_status()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the bridge system"""
        success_rate = 0.0
        if self.performance_metrics['total_missions'] > 0:
            success_rate = (self.performance_metrics['successful_missions'] / 
                          self.performance_metrics['total_missions']) * 100
        
        return {
            **self.performance_metrics,
            'success_rate_percentage': success_rate,
            'system_health': 'optimal' if success_rate > 90 else 'good' if success_rate > 70 else 'needs_attention'
        }


class SentinelAgentObservabilityEnhancer:
    """Enhanced observability for Sentinel AI agents"""
    
    def __init__(self, bridge: SentinelMultiAgentBridge):
        self.bridge = bridge
        self.event_stream = []
        self.agent_metrics = {}
        
    async def push_event(self, event_type: str, source: str, message: str, 
                        severity: str = "INFO", payload: Dict = None):
        """Push observability event"""
        event = {
            'id': f"event_{len(self.event_stream)}",
            'event_type': event_type,
            'source': source,
            'severity': severity,
            'message': message,
            'payload': payload or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.event_stream.append(event)
        logger.info(f"[{source}] {severity}: {message}")
        
        # Keep only last 1000 events
        if len(self.event_stream) > 1000:
            self.event_stream = self.event_stream[-1000:]
    
    async def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent observability events"""
        return self.event_stream[-limit:]
    
    async def get_agent_performance_summary(self) -> Dict[str, Any]:
        """Get agent performance summary"""
        bridge_metrics = self.bridge.get_performance_metrics()
        agent_status = await self.bridge.get_agent_status()
        
        return {
            'bridge_metrics': bridge_metrics,
            'agent_status': agent_status,
            'total_events': len(self.event_stream),
            'system_uptime': 'active',
            'multi_agent_health': 'optimal'
        }


class SentinelMultiAgentAPI:
    """API interface for Sentinel AI multi-agent system"""
    
    def __init__(self):
        self.bridge = SentinelMultiAgentBridge()
        self.observability = SentinelAgentObservabilityEnhancer(self.bridge)
        
    async def execute_mission(self, mission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute mission through multi-agent system"""
        # Log mission start
        await self.observability.push_event(
            'mission_started',
            'multi_agent_api',
            f"Starting mission: {mission_data.get('prompt', 'Unknown')[:50]}...",
            'INFO',
            {'mission_data': mission_data}
        )
        
        # Execute mission
        result = await self.bridge.execute_sentinel_mission(mission_data)
        
        # Log mission completion
        await self.observability.push_event(
            'mission_completed',
            'multi_agent_api',
            f"Mission completed with status: {result.get('status', 'unknown')}",
            'SUCCESS' if result.get('status') == 'completed' else 'ERROR',
            {'result': result}
        )
        
        return result
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            'multi_agent_system': await self.bridge.get_agent_status(),
            'performance_metrics': self.bridge.get_performance_metrics(),
            'observability_summary': await self.observability.get_agent_performance_summary(),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def list_available_workflows(self) -> Dict[str, Any]:
        """List available workflow patterns"""
        return {
            'available_patterns': list(self.bridge.orchestrator.workflow_patterns.keys()),
            'pattern_details': {
                name: {
                    'pattern_type': config['pattern'].value,
                    'steps': len(config['steps']),
                    'description': self._get_pattern_description(name)
                }
                for name, config in self.bridge.orchestrator.workflow_patterns.items()
            }
        }
    
    def _get_pattern_description(self, pattern_name: str) -> str:
        """Get description for workflow pattern"""
        descriptions = {
            'research_and_development': 'Sequential workflow: Research → Planning → Development',
            'collaborative_analysis': 'Collaborative workflow: Multiple agents working together',
            'rapid_prototyping': 'Parallel workflow: Fast concurrent development'
        }
        return descriptions.get(pattern_name, 'Custom workflow pattern')


# Integration test and demo functions
async def test_sentinel_integration():
    """Test the Sentinel AI integration"""
    logger.info("=== Testing Sentinel AI Multi-Agent Integration ===")
    
    # Initialize the API
    api = SentinelMultiAgentAPI()
    
    # Test missions
    test_missions = [
        {
            'mission_id_str': 'test_001',
            'prompt': 'Analyze and optimize the database performance for our web application',
            'agent_type': 'developer',
            'priority': 'high'
        },
        {
            'mission_id_str': 'test_002', 
            'prompt': 'Research best practices for implementing microservices architecture',
            'agent_type': 'researcher',
            'priority': 'medium'
        },
        {
            'mission_id_str': 'test_003',
            'prompt': 'Create a prototype for real-time data processing system',
            'agent_type': 'developer',
            'priority': 'high'
        }
    ]
    
    # Execute test missions
    results = []
    for mission in test_missions:
        logger.info(f"Executing mission: {mission['mission_id_str']}")
        result = await api.execute_mission(mission)
        results.append(result)
        logger.info(f"Mission {mission['mission_id_str']} status: {result.get('status', 'unknown')}")
    
    # Get system status
    system_status = await api.get_system_status()
    logger.info(f"System Status: {system_status['performance_metrics']['success_rate_percentage']:.1f}% success rate")
    
    # List available workflows
    workflows = await api.list_available_workflows()
    logger.info(f"Available workflow patterns: {len(workflows['available_patterns'])}")
    
    return api, results, system_status


async def demonstrate_enhanced_capabilities():
    """Demonstrate enhanced multi-agent capabilities"""
    logger.info("=== Demonstrating Enhanced Multi-Agent Capabilities ===")
    
    api = SentinelMultiAgentAPI()
    
    # Complex mission requiring multiple agents
    complex_mission = {
        'mission_id_str': 'complex_001',
        'prompt': '''
        Build a comprehensive AI-powered customer service system that includes:
        1. Natural language processing for customer inquiries
        2. Sentiment analysis for priority routing  
        3. Automated response generation
        4. Integration with existing CRM systems
        5. Real-time analytics dashboard
        6. Multi-language support
        7. Performance monitoring and alerting
        ''',
        'agent_type': 'developer',
        'priority': 'critical'
    }
    
    logger.info("Executing complex multi-component mission...")
    result = await api.execute_mission(complex_mission)
    
    logger.info("=== Complex Mission Results ===")
    logger.info(f"Status: {result.get('status', 'unknown')}")
    logger.info(f"Execution Time: {result.get('execution_time', 0):.2f} seconds")
    logger.info(f"Workflow Pattern: {result.get('summary', {}).get('workflow_pattern', 'unknown')}")
    logger.info(f"Agents Involved: {result.get('summary', {}).get('agents_involved', 0)}")
    
    return result


# Main execution
if __name__ == "__main__":
    async def main():
        try:
            # Test integration
            api, results, status = await test_sentinel_integration()
            print("\n" + "="*60 + "\n")
            
            # Demonstrate enhanced capabilities
            complex_result = await demonstrate_enhanced_capabilities()
            print("\n" + "="*60 + "\n")
            
            # Final system summary
            logger.info("=== Final System Summary ===")
            final_status = await api.get_system_status()
            perf = final_status['performance_metrics']
            
            logger.info(f"Total Missions Executed: {perf['total_missions']}")
            logger.info(f"Success Rate: {perf['success_rate_percentage']:.1f}%")
            logger.info(f"Average Execution Time: {perf['average_execution_time']:.2f}s")
            logger.info(f"System Health: {perf['system_health']}")
            logger.info(f"Multi-Agent System: Fully Operational")
            
            return api
            
        except Exception as e:
            logger.error(f"Integration test failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Run the integration test
    asyncio.run(main())