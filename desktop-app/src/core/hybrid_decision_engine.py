"""
Hybrid Decision Engine - Intelligent Routing System
Advanced AI-powered decision making for optimal execution path selection
"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from collections import defaultdict, deque
import threading
import pickle
import os

from ..config.settings import settings
from loguru import logger

@dataclass
class TaskComplexity:
    """Task complexity analysis result"""
    overall_score: float  # 0.0 = simple, 1.0 = complex
    length_score: float
    keyword_score: float
    context_score: float
    historical_score: float
    confidence: float

@dataclass
class PerformancePrediction:
    """Performance prediction for execution paths"""
    golden_path_time: float
    full_workflow_time: float
    golden_path_success_rate: float
    full_workflow_success_rate: float
    confidence: float

@dataclass
class UserPreferences:
    """User-specific preferences and history"""
    user_id: str
    preferred_path: str  # "golden_path" or "full_workflow"
    speed_preference: float  # 0.0 = quality, 1.0 = speed
    complexity_preference: float  # 0.0 = simple, 1.0 = complex
    satisfaction_history: List[float]
    last_updated: datetime

class PredictiveCache:
    """Intelligent caching system for task results"""
    
    def __init__(self):
        self.cache = {}
        self.access_times = {}
        self.hit_count = defaultdict(int)
        self.miss_count = defaultdict(int)
        self.max_size = settings.CACHE_SIZE_LIMIT
        self.ttl = settings.CACHE_TTL
        
    def _generate_cache_key(self, prompt: str, path: str) -> str:
        """Generate cache key for task"""
        content = f"{prompt.lower().strip()}:{path}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, prompt: str, path: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available"""
        key = self._generate_cache_key(prompt, path)
        
        if key in self.cache:
            result = self.cache[key]
            access_time = self.access_times[key]
            
            # Check TTL
            if time.time() - access_time < self.ttl:
                self.access_times[key] = time.time()
                self.hit_count[path] += 1
                logger.info(f"🔄 Cache HIT for {path}: {key[:8]}...")
                return result
            else:
                # Expired, remove
                del self.cache[key]
                del self.access_times[key]
        
        self.miss_count[path] += 1
        return None
    
    def set(self, prompt: str, path: str, result: Dict[str, Any]):
        """Cache task result"""
        key = self._generate_cache_key(prompt, path)
        
        # Evict if cache is full
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        self.cache[key] = result
        self.access_times[key] = time.time()
        logger.info(f"💾 Cache SET for {path}: {key[:8]}...")
    
    def _evict_oldest(self):
        """Evict oldest cache entries"""
        if not self.access_times:
            return
        
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        del self.cache[oldest_key]
        del self.access_times[oldest_key]
        logger.info(f"🗑️ Cache EVICT: {oldest_key[:8]}...")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_hits = sum(self.hit_count.values())
        total_misses = sum(self.miss_count.values())
        hit_rate = total_hits / (total_hits + total_misses) if (total_hits + total_misses) > 0 else 0
        
        return {
            "cache_size": len(self.cache),
            "hit_rate": hit_rate,
            "hits_by_path": dict(self.hit_count),
            "misses_by_path": dict(self.miss_count),
            "max_size": self.max_size,
            "ttl": self.ttl
        }

class PerformanceLearningSystem:
    """Machine learning system for performance prediction"""
    
    def __init__(self):
        self.execution_history = deque(maxlen=10000)
        self.user_preferences = {}
        self.performance_models = {
            "golden_path": self._create_simple_model(),
            "full_workflow": self._create_simple_model()
        }
        self.last_model_update = datetime.now()
        self.update_lock = threading.Lock()
    
    def _create_simple_model(self) -> Dict[str, Any]:
        """Create a simple performance prediction model"""
        return {
            "avg_execution_time": 0.0,
            "success_rate": 0.0,
            "complexity_weights": {},
            "keyword_weights": {},
            "sample_count": 0
        }
    
    def record_execution(self, task_id: str, prompt: str, path: str, 
                        execution_time: float, success: bool, 
                        user_satisfaction: float, complexity_score: float):
        """Record execution result for learning"""
        with self.update_lock:
            record = {
                "task_id": task_id,
                "prompt": prompt,
                "path": path,
                "execution_time": execution_time,
                "success": success,
                "user_satisfaction": user_satisfaction,
                "complexity_score": complexity_score,
                "timestamp": datetime.now()
            }
            
            self.execution_history.append(record)
            
            # Update performance model
            self._update_performance_model(path, record)
            
            # Update user preferences
            self._update_user_preferences(task_id, path, user_satisfaction)
    
    def _update_performance_model(self, path: str, record: Dict[str, Any]):
        """Update performance prediction model"""
        model = self.performance_models[path]
        
        # Update average execution time
        if model["sample_count"] == 0:
            model["avg_execution_time"] = record["execution_time"]
        else:
            alpha = 0.1  # Learning rate
            model["avg_execution_time"] = (
                (1 - alpha) * model["avg_execution_time"] + 
                alpha * record["execution_time"]
            )
        
        # Update success rate
        if model["sample_count"] == 0:
            model["success_rate"] = 1.0 if record["success"] else 0.0
        else:
            alpha = 0.1
            current_success = 1.0 if record["success"] else 0.0
            model["success_rate"] = (
                (1 - alpha) * model["success_rate"] + 
                alpha * current_success
            )
        
        model["sample_count"] += 1
    
    def _update_user_preferences(self, task_id: str, path: str, satisfaction: float):
        """Update user preferences based on satisfaction"""
        user_id = task_id.split('_')[0] if '_' in task_id else "default"
        
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = UserPreferences(
                user_id=user_id,
                preferred_path="golden_path",
                speed_preference=0.5,
                complexity_preference=0.5,
                satisfaction_history=[],
                last_updated=datetime.now()
            )
        
        user_pref = self.user_preferences[user_id]
        user_pref.satisfaction_history.append(satisfaction)
        
        # Keep only recent history
        if len(user_pref.satisfaction_history) > 100:
            user_pref.satisfaction_history = user_pref.satisfaction_history[-50:]
        
        # Update preferences based on satisfaction
        if satisfaction > 0.8:
            user_pref.preferred_path = path
        elif satisfaction < 0.3:
            # Switch preference if satisfaction is low
            user_pref.preferred_path = "full_workflow" if path == "golden_path" else "golden_path"
        
        user_pref.last_updated = datetime.now()
    
    def predict_performance(self, prompt: str, complexity_score: float) -> PerformancePrediction:
        """Predict performance for both execution paths"""
        golden_model = self.performance_models["golden_path"]
        full_model = self.performance_models["full_workflow"]
        
        # Adjust predictions based on complexity
        complexity_factor = 1.0 + (complexity_score * 0.5)
        
        golden_time = golden_model["avg_execution_time"] * complexity_factor
        full_time = full_model["avg_execution_time"] * complexity_factor
        
        # Ensure minimum values
        golden_time = max(golden_time, 0.5)
        full_time = max(full_time, 10.0)
        
        return PerformancePrediction(
            golden_path_time=golden_time,
            full_workflow_time=full_time,
            golden_path_success_rate=golden_model["success_rate"],
            full_workflow_success_rate=full_model["success_rate"],
            confidence=min(golden_model["sample_count"], full_model["sample_count"]) / 100.0
        )
    
    def get_user_preferences(self, user_id: str = "default") -> UserPreferences:
        """Get user preferences"""
        return self.user_preferences.get(user_id, UserPreferences(
            user_id=user_id,
            preferred_path="golden_path",
            speed_preference=0.5,
            complexity_preference=0.5,
            satisfaction_history=[],
            last_updated=datetime.now()
        ))

class HybridDecisionEngine:
    """Intelligent hybrid decision engine for optimal path selection"""
    
    def __init__(self):
        self.cache = PredictiveCache()
        self.learning_system = PerformanceLearningSystem()
        self.complexity_analyzer = TaskComplexityAnalyzer()
        self.analytics = AdvancedAnalytics()
        
        # Performance tracking
        self.decision_history = deque(maxlen=1000)
        self.last_threshold_update = datetime.now()
        
        logger.info("🚀 Hybrid Decision Engine initialized")
    
    def analyze_task_complexity(self, prompt: str) -> TaskComplexity:
        """Analyze task complexity using multiple factors"""
        return self.complexity_analyzer.analyze(prompt)
    
    def predict_performance(self, prompt: str, complexity_score: float) -> PerformancePrediction:
        """Predict performance for both execution paths"""
        return self.learning_system.predict_performance(prompt, complexity_score)
    
    def make_hybrid_decision(self, prompt: str, user_id: str = "default", 
                           force_path: Optional[str] = None) -> Dict[str, Any]:
        """Make intelligent routing decision"""
        
        # Check cache first
        cache_key = f"{prompt}:{user_id}"
        cached_decision = self.cache.get(prompt, "decision")
        if cached_decision:
            return cached_decision
        
        # Force path if specified
        if force_path:
            decision = {
                "path": force_path,
                "reason": "forced",
                "confidence": 1.0,
                "complexity_score": 0.5,
                "predicted_time": 0.0
            }
            self.cache.set(prompt, "decision", decision)
            return decision
        
        # Analyze task complexity
        complexity = self.analyze_task_complexity(prompt)
        
        # Predict performance
        performance = self.predict_performance(prompt, complexity.overall_score)
        
        # Get user preferences
        user_prefs = self.learning_system.get_user_preferences(user_id)
        
        # Calculate decision weights
        decision_score = self._calculate_decision_score(
            complexity, performance, user_prefs
        )
        
        # Make decision
        if decision_score > settings.HYBRID_SWITCH_THRESHOLD:
            chosen_path = "full_workflow"
            reason = "complex_task"
        else:
            chosen_path = "golden_path"
            reason = "simple_task"
        
        # Consider user preferences
        if user_prefs.preferred_path != chosen_path:
            # Adjust based on user preference weight
            if user_prefs.preferred_path == "golden_path" and decision_score < 0.8:
                chosen_path = "golden_path"
                reason = "user_preference"
            elif user_prefs.preferred_path == "full_workflow" and decision_score > 0.4:
                chosen_path = "full_workflow"
                reason = "user_preference"
        
        # Record decision
        decision = {
            "path": chosen_path,
            "reason": reason,
            "confidence": complexity.confidence,
            "complexity_score": complexity.overall_score,
            "predicted_time": performance.golden_path_time if chosen_path == "golden_path" else performance.full_workflow_time,
            "user_preference": user_prefs.preferred_path,
            "performance_prediction": {
                "golden_path_time": performance.golden_path_time,
                "full_workflow_time": performance.full_workflow_time,
                "golden_path_success_rate": performance.golden_path_success_rate,
                "full_workflow_success_rate": performance.full_workflow_success_rate
            }
        }
        
        # Cache decision
        self.cache.set(prompt, "decision", decision)
        
        # Record analytics
        self.analytics.record_decision(prompt, decision, complexity, performance)
        
        # Log decision
        logger.info(f"🎯 Hybrid Decision: {chosen_path} ({reason}) - Confidence: {complexity.confidence:.2f}")
        
        return decision
    
    def _calculate_decision_score(self, complexity: TaskComplexity, 
                                performance: PerformancePrediction,
                                user_prefs: UserPreferences) -> float:
        """Calculate weighted decision score"""
        
        # Complexity score (0.0 = simple, 1.0 = complex)
        complexity_score = complexity.overall_score
        
        # Performance score (0.0 = golden path better, 1.0 = full workflow better)
        golden_advantage = performance.full_workflow_time / max(performance.golden_path_time, 0.1)
        performance_score = min(golden_advantage / 10.0, 1.0)  # Normalize
        
        # User preference score
        user_score = 0.5  # Neutral default
        if user_prefs.preferred_path == "full_workflow":
            user_score = 0.8
        elif user_prefs.preferred_path == "golden_path":
            user_score = 0.2
        
        # Weighted combination
        final_score = (
            settings.COMPLEXITY_WEIGHT * complexity_score +
            settings.PERFORMANCE_WEIGHT * performance_score +
            settings.USER_PREFERENCE_WEIGHT * user_score
        )
        
        return min(max(final_score, 0.0), 1.0)
    
    def record_execution_result(self, task_id: str, prompt: str, path: str,
                              execution_time: float, success: bool,
                              user_satisfaction: float):
        """Record execution result for learning"""
        complexity = self.analyze_task_complexity(prompt)
        
        self.learning_system.record_execution(
            task_id, prompt, path, execution_time, success,
            user_satisfaction, complexity.overall_score
        )
        
        # Update analytics
        self.analytics.record_execution_result(
            task_id, prompt, path, execution_time, success, user_satisfaction
        )
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        return {
            "cache_stats": self.cache.get_stats(),
            "analytics": self.analytics.get_stats(),
            "performance_models": self.learning_system.performance_models,
            "user_preferences_count": len(self.learning_system.user_preferences),
            "total_decisions": len(self.decision_history),
            "last_threshold_update": self.last_threshold_update.isoformat()
        }

class TaskComplexityAnalyzer:
    """Advanced task complexity analysis"""
    
    def analyze(self, prompt: str) -> TaskComplexity:
        """Analyze task complexity using multiple factors"""
        
        # Length analysis
        length_score = min(len(prompt) / 1000.0, 1.0)
        
        # Keyword analysis
        prompt_lower = prompt.lower()
        simple_matches = sum(1 for keyword in settings.SIMPLE_TASK_KEYWORDS 
                           if keyword in prompt_lower)
        complex_matches = sum(1 for keyword in settings.COMPLEX_TASK_KEYWORDS 
                            if keyword in prompt_lower)
        
        keyword_score = complex_matches / max(simple_matches + complex_matches, 1)
        
        # Context analysis
        context_score = self._analyze_context(prompt)
        
        # Historical analysis (placeholder for now)
        historical_score = 0.5
        
        # Weighted combination
        overall_score = (
            0.3 * length_score +
            0.4 * keyword_score +
            0.2 * context_score +
            0.1 * historical_score
        )
        
        # Calculate confidence based on analysis quality
        confidence = min(
            (simple_matches + complex_matches) / 10.0 + 
            (length_score * 0.5),
            1.0
        )
        
        return TaskComplexity(
            overall_score=overall_score,
            length_score=length_score,
            keyword_score=keyword_score,
            context_score=context_score,
            historical_score=historical_score,
            confidence=confidence
        )
    
    def _analyze_context(self, prompt: str) -> float:
        """Analyze context complexity"""
        # Simple heuristics for context analysis
        context_indicators = [
            "system", "architecture", "design", "framework",
            "database", "api", "integration", "deployment",
            "scalability", "performance", "security", "testing"
        ]
        
        prompt_lower = prompt.lower()
        matches = sum(1 for indicator in context_indicators 
                     if indicator in prompt_lower)
        
        return min(matches / len(context_indicators), 1.0)

class AdvancedAnalytics:
    """Advanced analytics and performance tracking"""
    
    def __init__(self):
        self.decision_metrics = defaultdict(list)
        self.execution_metrics = defaultdict(list)
        self.performance_trends = defaultdict(list)
        self.user_satisfaction = defaultdict(list)
    
    def record_decision(self, prompt: str, decision: Dict[str, Any],
                       complexity: TaskComplexity, performance: PerformancePrediction):
        """Record decision metrics"""
        timestamp = datetime.now()
        
        self.decision_metrics["total_decisions"].append({
            "timestamp": timestamp,
            "path": decision["path"],
            "reason": decision["reason"],
            "confidence": decision["confidence"],
            "complexity_score": complexity.overall_score
        })
    
    def record_execution_result(self, task_id: str, prompt: str, path: str,
                              execution_time: float, success: bool,
                              user_satisfaction: float):
        """Record execution result metrics"""
        timestamp = datetime.now()
        
        self.execution_metrics[path].append({
            "timestamp": timestamp,
            "execution_time": execution_time,
            "success": success,
            "user_satisfaction": user_satisfaction
        })
        
        # Update performance trends
        self.performance_trends[path].append({
            "timestamp": timestamp,
            "execution_time": execution_time,
            "success_rate": 1.0 if success else 0.0
        })
        
        # Update user satisfaction
        self.user_satisfaction[path].append({
            "timestamp": timestamp,
            "satisfaction": user_satisfaction
        })
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive analytics statistics"""
        stats = {
            "decision_metrics": {
                "total_decisions": len(self.decision_metrics["total_decisions"]),
                "path_distribution": defaultdict(int),
                "avg_confidence": 0.0,
                "avg_complexity": 0.0
            },
            "execution_metrics": {},
            "performance_trends": {},
            "user_satisfaction": {}
        }
        
        # Calculate decision metrics
        if self.decision_metrics["total_decisions"]:
            decisions = self.decision_metrics["total_decisions"]
            stats["decision_metrics"]["path_distribution"] = {
                path: sum(1 for d in decisions if d["path"] == path)
                for path in ["golden_path", "full_workflow"]
            }
            stats["decision_metrics"]["avg_confidence"] = np.mean([d["confidence"] for d in decisions])
            stats["decision_metrics"]["avg_complexity"] = np.mean([d["complexity_score"] for d in decisions])
        
        # Calculate execution metrics for each path
        for path in ["golden_path", "full_workflow"]:
            if path in self.execution_metrics:
                executions = self.execution_metrics[path]
                if executions:
                    stats["execution_metrics"][path] = {
                        "total_executions": len(executions),
                        "avg_execution_time": np.mean([e["execution_time"] for e in executions]),
                        "success_rate": np.mean([1.0 if e["success"] else 0.0 for e in executions]),
                        "avg_satisfaction": np.mean([e["user_satisfaction"] for e in executions])
                    }
        
        return stats

# Global instance
hybrid_decision_engine = HybridDecisionEngine() 