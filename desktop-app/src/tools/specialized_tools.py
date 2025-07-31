"""
Specialized Tools for Autonomous AI Crew System
Implements tools required by the specialized agents
"""

import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger


class TaskMonitorTool:
    """Tool for monitoring task execution and agent performance"""
    
    def __init__(self):
        self.task_history = []
        self.agent_metrics = {}
        logger.info("TaskMonitorTool initialized")
    
    def monitor_task(self, task_id: str, agent_id: str, start_time: float, 
                    status: str = "running") -> Dict[str, Any]:
        """Monitor a specific task"""
        task_data = {
            "task_id": task_id,
            "agent_id": agent_id,
            "start_time": start_time,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        self.task_history.append(task_data)
        
        # Update agent metrics
        if agent_id not in self.agent_metrics:
            self.agent_metrics[agent_id] = {"tasks": 0, "success_rate": 0.0}
        self.agent_metrics[agent_id]["tasks"] += 1
        
        logger.info(f"TaskMonitorTool: Monitoring task {task_id} by agent {agent_id}")
        return task_data
    
    def get_agent_utilization(self, agent_id: str) -> float:
        """Get agent utilization percentage"""
        if agent_id not in self.agent_metrics:
            return 0.0
        
        # Calculate utilization based on recent activity
        recent_tasks = [t for t in self.task_history 
                       if t["agent_id"] == agent_id 
                       and time.time() - t["start_time"] < 3600]  # Last hour
        
        return min(len(recent_tasks) * 10, 100.0)  # Simplified calculation
    
    def detect_failures(self) -> List[Dict[str, Any]]:
        """Detect potential task failures"""
        failures = []
        for task in self.task_history:
            if task["status"] == "failed" or (
                task["status"] == "running" and 
                time.time() - task["start_time"] > 300  # 5 minutes timeout
            ):
                failures.append(task)
        
        return failures


class PromptABTestTool:
    """Tool for conducting A/B tests on agent prompts"""
    
    def __init__(self):
        self.test_results = []
        self.prompt_variants = {}
        logger.info("PromptABTestTool initialized")
    
    def create_prompt_variant(self, original_prompt: str, 
                            variation_type: str = "semantic_augmentation") -> str:
        """Create a variant of the original prompt"""
        if variation_type == "semantic_augmentation":
            # Add more context and examples
            variant = f"{original_prompt}\n\nAdditional Context:\n- Provide detailed explanations\n- Include code examples where applicable\n- Consider edge cases"
        elif variation_type == "constraint_relaxation":
            # Relax some constraints
            variant = f"{original_prompt}\n\nNote: Focus on core functionality first, optimize later"
        elif variation_type == "few_shot_rotation":
            # Add few-shot examples
            variant = f"{original_prompt}\n\nExample:\n```python\n# Example implementation\ndef example_function():\n    return 'example output'\n```"
        else:
            variant = original_prompt
        
        return variant
    
    def run_ab_test(self, prompt_a: str, prompt_b: str, 
                   test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run A/B test between two prompt variants"""
        results_a = {"prompt": prompt_a, "score": 0.0, "responses": []}
        results_b = {"prompt": prompt_b, "score": 0.0, "responses": []}
        
        for test_case in test_cases:
            # Simulate testing both prompts
            score_a = self._evaluate_response(prompt_a, test_case)
            score_b = self._evaluate_response(prompt_b, test_case)
            
            results_a["responses"].append({"test_case": test_case, "score": score_a})
            results_b["responses"].append({"test_case": test_case, "score": score_b})
            
            results_a["score"] += score_a
            results_b["score"] += score_b
        
        # Calculate average scores
        if test_cases:
            results_a["score"] /= len(test_cases)
            results_b["score"] /= len(test_cases)
        
        test_result = {
            "timestamp": datetime.now().isoformat(),
            "variant_a": results_a,
            "variant_b": results_b,
            "winner": "A" if results_a["score"] > results_b["score"] else "B",
            "improvement": abs(results_a["score"] - results_b["score"])
        }
        
        self.test_results.append(test_result)
        logger.info(f"PromptABTestTool: A/B test completed, winner: {test_result['winner']}")
        
        return test_result
    
    def _evaluate_response(self, prompt: str, test_case: Dict[str, Any]) -> float:
        """Evaluate a prompt response (simplified scoring)"""
        # Simplified evaluation - in practice this would use actual LLM evaluation
        base_score = 7.0  # Base score
        
        # Adjust based on prompt characteristics
        if "example" in prompt.lower():
            base_score += 0.5
        if "detailed" in prompt.lower():
            base_score += 0.3
        if "constraint" in prompt.lower():
            base_score += 0.2
        
        return min(base_score, 10.0)


class KnowledgeGraphBuilder:
    """Tool for building and maintaining knowledge graphs"""
    
    def __init__(self):
        self.knowledge_graph = {
            "nodes": {},
            "edges": [],
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        }
        logger.info("KnowledgeGraphBuilder initialized")
    
    def add_knowledge_node(self, node_id: str, node_type: str, 
                          properties: Dict[str, Any]) -> Dict[str, Any]:
        """Add a node to the knowledge graph"""
        node = {
            "id": node_id,
            "type": node_type,
            "properties": properties,
            "created": datetime.now().isoformat(),
            "confidence": properties.get("confidence", 0.8)
        }
        
        self.knowledge_graph["nodes"][node_id] = node
        self.knowledge_graph["metadata"]["last_updated"] = datetime.now().isoformat()
        
        logger.info(f"KnowledgeGraphBuilder: Added node {node_id} of type {node_type}")
        return node
    
    def add_knowledge_edge(self, source_id: str, target_id: str, 
                          relationship_type: str, properties: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add an edge to the knowledge graph"""
        edge = {
            "source": source_id,
            "target": target_id,
            "type": relationship_type,
            "properties": properties or {},
            "created": datetime.now().isoformat()
        }
        
        self.knowledge_graph["edges"].append(edge)
        self.knowledge_graph["metadata"]["last_updated"] = datetime.now().isoformat()
        
        logger.info(f"KnowledgeGraphBuilder: Added edge {source_id} -> {target_id}")
        return edge
    
    def query_knowledge_graph(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query the knowledge graph"""
        results = []
        
        if "node_type" in query:
            # Filter by node type
            for node_id, node in self.knowledge_graph["nodes"].items():
                if node["type"] == query["node_type"]:
                    results.append(node)
        
        elif "relationship" in query:
            # Filter by relationship type
            for edge in self.knowledge_graph["edges"]:
                if edge["type"] == query["relationship"]:
                    results.append(edge)
        
        elif "keyword" in query:
            # Search by keyword in properties
            keyword = query["keyword"].lower()
            for node_id, node in self.knowledge_graph["nodes"].items():
                for key, value in node["properties"].items():
                    if isinstance(value, str) and keyword in value.lower():
                        results.append(node)
                        break
        
        logger.info(f"KnowledgeGraphBuilder: Query returned {len(results)} results")
        return results
    
    def resolve_contradictions(self) -> List[Dict[str, Any]]:
        """Resolve contradictions in the knowledge graph"""
        contradictions = []
        
        # Simple contradiction detection based on confidence scores
        for node_id, node in self.knowledge_graph["nodes"].items():
            if node["confidence"] < 0.5:
                contradictions.append({
                    "node_id": node_id,
                    "issue": "Low confidence",
                    "confidence": node["confidence"]
                })
        
        logger.info(f"KnowledgeGraphBuilder: Found {len(contradictions)} contradictions")
        return contradictions


class ResourceBalancer:
    """Tool for balancing resources across agents"""
    
    def __init__(self):
        self.agent_resources = {}
        self.resource_history = []
        logger.info("ResourceBalancer initialized")
    
    def allocate_resources(self, agent_id: str, resource_type: str, 
                          amount: float) -> Dict[str, Any]:
        """Allocate resources to an agent"""
        if agent_id not in self.agent_resources:
            self.agent_resources[agent_id] = {}
        
        if resource_type not in self.agent_resources[agent_id]:
            self.agent_resources[agent_id][resource_type] = 0.0
        
        self.agent_resources[agent_id][resource_type] += amount
        
        allocation = {
            "agent_id": agent_id,
            "resource_type": resource_type,
            "amount": amount,
            "total": self.agent_resources[agent_id][resource_type],
            "timestamp": datetime.now().isoformat()
        }
        
        self.resource_history.append(allocation)
        logger.info(f"ResourceBalancer: Allocated {amount} {resource_type} to {agent_id}")
        
        return allocation
    
    def get_resource_utilization(self) -> Dict[str, Any]:
        """Get current resource utilization across all agents"""
        utilization = {}
        
        for agent_id, resources in self.agent_resources.items():
            utilization[agent_id] = {
                "resources": resources,
                "total_utilization": sum(resources.values())
            }
        
        return utilization
    
    def optimize_allocation(self, task_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize resource allocation based on task requirements"""
        # Simple optimization - in practice this would use more sophisticated algorithms
        optimization_plan = {
            "reallocations": [],
            "efficiency_gain": 0.0
        }
        
        # Calculate optimal distribution
        total_resources = sum(req.get("resources", 0) for req in task_requirements.values())
        num_agents = len(task_requirements)
        
        if num_agents > 0:
            optimal_per_agent = total_resources / num_agents
            
            for agent_id, requirements in task_requirements.items():
                current = sum(self.agent_resources.get(agent_id, {}).values())
                if current > optimal_per_agent * 1.2:  # Over-allocated
                    reduction = current - optimal_per_agent
                    optimization_plan["reallocations"].append({
                        "agent_id": agent_id,
                        "action": "reduce",
                        "amount": reduction
                    })
                    optimization_plan["efficiency_gain"] += reduction
        
        logger.info(f"ResourceBalancer: Optimization plan created with {len(optimization_plan['reallocations'])} reallocations")
        return optimization_plan


class MetricAnalyzer:
    """Tool for analyzing performance metrics"""
    
    def __init__(self):
        self.metrics_history = []
        logger.info("MetricAnalyzer initialized")
    
    def analyze_performance(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance metrics and provide insights"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "overall_score": 0.0,
            "trends": {},
            "recommendations": []
        }
        
        # Calculate overall score
        if "accuracy" in metrics:
            analysis["overall_score"] += metrics["accuracy"] * 0.4
        if "efficiency" in metrics:
            analysis["overall_score"] += metrics["efficiency"] * 0.3
        if "autonomy" in metrics:
            analysis["overall_score"] += metrics["autonomy"] * 0.3
        
        # Identify trends
        if len(self.metrics_history) > 0:
            last_metrics = self.metrics_history[-1]
            for key in metrics:
                if key in last_metrics:
                    change = metrics[key] - last_metrics[key]
                    analysis["trends"][key] = {
                        "change": change,
                        "direction": "improving" if change > 0 else "declining"
                    }
        
        # Generate recommendations
        if analysis["overall_score"] < 7.0:
            analysis["recommendations"].append("Consider prompt optimization")
        if metrics.get("autonomy", 0) < 0.8:
            analysis["recommendations"].append("Increase autonomous decision making")
        if metrics.get("efficiency", 0) < 0.7:
            analysis["recommendations"].append("Optimize resource allocation")
        
        self.metrics_history.append(metrics)
        logger.info(f"MetricAnalyzer: Performance analysis completed, score: {analysis['overall_score']:.2f}")
        
        return analysis


class ContextValidator:
    """Tool for validating context consistency"""
    
    def __init__(self):
        self.validation_history = []
        logger.info("ContextValidator initialized")
    
    def validate_context(self, context: Dict[str, Any], 
                        historical_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Validate context for consistency and completeness"""
        validation_result = {
            "timestamp": datetime.now().isoformat(),
            "is_valid": True,
            "issues": [],
            "confidence": 0.8
        }
        
        # Check for required fields
        required_fields = ["mission_id", "agents", "tasks"]
        for field in required_fields:
            if field not in context:
                validation_result["issues"].append(f"Missing required field: {field}")
                validation_result["is_valid"] = False
        
        # Check for contradictions with historical context
        if historical_context:
            contradictions = self._find_contradictions(context, historical_context)
            if contradictions:
                validation_result["issues"].extend(contradictions)
                validation_result["confidence"] -= 0.2
        
        # Check for logical consistency
        if "tasks" in context and "agents" in context:
            if len(context["tasks"]) > len(context["agents"]) * 3:
                validation_result["issues"].append("Too many tasks for available agents")
                validation_result["is_valid"] = False
        
        self.validation_history.append(validation_result)
        logger.info(f"ContextValidator: Validation completed, valid: {validation_result['is_valid']}")
        
        return validation_result
    
    def _find_contradictions(self, current: Dict[str, Any], 
                            historical: Dict[str, Any]) -> List[str]:
        """Find contradictions between current and historical context"""
        contradictions = []
        
        # Simple contradiction detection
        for key in current:
            if key in historical:
                if current[key] != historical[key]:
                    contradictions.append(f"Contradiction in {key}: {historical[key]} vs {current[key]}")
        
        return contradictions


# Factory for creating specialized tools
class SpecializedToolFactory:
    """Factory for creating specialized tools"""
    
    @staticmethod
    def create_task_monitor() -> TaskMonitorTool:
        """Create a TaskMonitorTool"""
        return TaskMonitorTool()
    
    @staticmethod
    def create_prompt_ab_test() -> PromptABTestTool:
        """Create a PromptABTestTool"""
        return PromptABTestTool()
    
    @staticmethod
    def create_knowledge_graph_builder() -> KnowledgeGraphBuilder:
        """Create a KnowledgeGraphBuilder"""
        return KnowledgeGraphBuilder()
    
    @staticmethod
    def create_resource_balancer() -> ResourceBalancer:
        """Create a ResourceBalancer"""
        return ResourceBalancer()
    
    @staticmethod
    def create_metric_analyzer() -> MetricAnalyzer:
        """Create a MetricAnalyzer"""
        return MetricAnalyzer()
    
    @staticmethod
    def create_context_validator() -> ContextValidator:
        """Create a ContextValidator"""
        return ContextValidator()
    
    @staticmethod
    def create_all_tools() -> Dict[str, Any]:
        """Create all specialized tools"""
        return {
            "task_monitor": SpecializedToolFactory.create_task_monitor(),
            "prompt_ab_test": SpecializedToolFactory.create_prompt_ab_test(),
            "knowledge_graph_builder": SpecializedToolFactory.create_knowledge_graph_builder(),
            "resource_balancer": SpecializedToolFactory.create_resource_balancer(),
            "metric_analyzer": SpecializedToolFactory.create_metric_analyzer(),
            "context_validator": SpecializedToolFactory.create_context_validator()
        } 