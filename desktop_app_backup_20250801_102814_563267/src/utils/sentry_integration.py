#!/usr/bin/env python3
"""
Sentry Integration for Enhanced Self-Healing and Self-Learning
Provides advanced error tracking, performance monitoring, and release tracking
"""

import os
import sys
import json
import time
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from loguru import logger

try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.asyncio import AsyncioIntegration
    from sentry_sdk.integrations.threading import ThreadingIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    logger.warning("Sentry SDK not installed. Install with: pip install sentry-sdk")

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SentryIntegration:
    """
    Advanced Sentry integration for enhanced self-healing and self-learning capabilities
    """
    
    def __init__(self, dsn: Optional[str] = None, environment: str = "development"):
        self.dsn = dsn or os.getenv("SENTRY_DSN")
        self.environment = environment
        self.initialized = False
        self.performance_data = {}
        self.error_patterns = {}
        self.learning_insights = []
        
        if SENTRY_AVAILABLE and self.dsn:
            self._initialize_sentry()
        else:
            logger.warning("Sentry not available. Enhanced monitoring will be limited.")
    
    def _initialize_sentry(self):
        """Initialize Sentry SDK with comprehensive configuration"""
        try:
            # Configure Sentry with multiple integrations
            sentry_sdk.init(
                dsn=self.dsn,
                environment=self.environment,
                release=self._get_release_version(),
                traces_sample_rate=1.0,  # Capture 100% of transactions
                profiles_sample_rate=1.0,  # Capture 100% of profiles
                integrations=[
                    LoggingIntegration(
                        level=20,  # INFO
                        event_level=40,  # ERROR
                    ),
                    AsyncioIntegration(),
                    ThreadingIntegration(),
                ],
                # Custom context
                before_send=self._before_send,
                before_breadcrumb=self._before_breadcrumb,
            )
            
            # Set user context
            self._set_user_context()
            
            self.initialized = True
            logger.success("Sentry integration initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Sentry: {e}")
            self.initialized = False
    
    def _get_release_version(self) -> str:
        """Get current release version"""
        try:
            # Try to get version from various sources
            version_file = Path("version.txt")
            if version_file.exists():
                return version_file.read_text().strip()
            
            # Fallback to timestamp-based version
            return f"sentinel-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        except Exception:
            return "sentinel-unknown"
    
    def _set_user_context(self):
        """Set user context for Sentry"""
        try:
            sentry_sdk.set_user({
                "id": "sentinel-system",
                "username": "sentinel-ai",
                "email": "system@sentinel.ai",
            })
        except Exception as e:
            logger.warning(f"Failed to set Sentry user context: {e}")
    
    def _before_send(self, event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Custom event processing before sending to Sentry"""
        try:
            # Add custom context
            event.setdefault("contexts", {})
            event["contexts"]["system"] = {
                "component": "sentinel-ai",
                "subsystem": "cognitive-forge",
                "version": self._get_release_version(),
            }
            
            # Add performance data if available
            if self.performance_data:
                event["contexts"]["performance"] = self.performance_data
            
            # Add learning insights
            if self.learning_insights:
                event["contexts"]["learning"] = {
                    "insights": self.learning_insights[-10:],  # Last 10 insights
                    "total_insights": len(self.learning_insights),
                }
            
            # Filter out sensitive information
            if "password" in str(event).lower() or "api_key" in str(event).lower():
                return None
            
            return event
            
        except Exception as e:
            logger.error(f"Error in before_send: {e}")
            return event
    
    def _before_breadcrumb(self, breadcrumb: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Custom breadcrumb processing"""
        try:
            # Add timestamp if not present
            if "timestamp" not in breadcrumb:
                breadcrumb["timestamp"] = datetime.now().isoformat()
            
            # Add system context
            breadcrumb["data"] = breadcrumb.get("data", {})
            breadcrumb["data"]["system"] = "sentinel-ai"
            
            return breadcrumb
            
        except Exception as e:
            logger.error(f"Error in before_breadcrumb: {e}")
            return breadcrumb
    
    def capture_error(self, error: Exception, context: Dict[str, Any] = None, level: str = "error"):
        """Capture an error with enhanced context"""
        if not self.initialized:
            logger.error(f"Error (Sentry not available): {error}")
            return
        
        try:
            # Add custom context
            if context:
                sentry_sdk.set_context("custom", context)
            
            # Add performance context
            if self.performance_data:
                sentry_sdk.set_context("performance", self.performance_data)
            
            # Capture the error
            sentry_sdk.capture_exception(error)
            
            # Update error patterns for learning
            self._update_error_patterns(error, context)
            
        except Exception as e:
            logger.error(f"Failed to capture error in Sentry: {e}")
    
    def capture_message(self, message: str, level: str = "info", context: Dict[str, Any] = None):
        """Capture a custom message"""
        if not self.initialized:
            logger.info(f"Message (Sentry not available): {message}")
            return
        
        try:
            if context:
                sentry_sdk.set_context("custom", context)
            
            sentry_sdk.capture_message(message, level=level)
            
        except Exception as e:
            logger.error(f"Failed to capture message in Sentry: {e}")
    
    def start_transaction(self, name: str, operation: str = "default") -> Any:
        """Start a performance transaction"""
        if not self.initialized:
            return None
        
        try:
            return sentry_sdk.start_transaction(
                name=name,
                op=operation,
                description=f"Sentinel AI operation: {name}"
            )
        except Exception as e:
            logger.error(f"Failed to start Sentry transaction: {e}")
            return None
    
    def set_performance_data(self, data: Dict[str, Any]):
        """Set performance data for context"""
        self.performance_data.update(data)
        
        if self.initialized:
            try:
                sentry_sdk.set_context("performance", self.performance_data)
            except Exception as e:
                logger.error(f"Failed to set performance context: {e}")
    
    def add_learning_insight(self, insight: Dict[str, Any]):
        """Add a learning insight for pattern recognition"""
        insight["timestamp"] = datetime.now().isoformat()
        self.learning_insights.append(insight)
        
        # Keep only last 100 insights
        if len(self.learning_insights) > 100:
            self.learning_insights = self.learning_insights[-100:]
    
    def _update_error_patterns(self, error: Exception, context: Dict[str, Any] = None):
        """Update error patterns for learning"""
        error_type = type(error).__name__
        error_msg = str(error)
        
        if error_type not in self.error_patterns:
            self.error_patterns[error_type] = {
                "count": 0,
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "contexts": [],
                "suggested_fixes": []
            }
        
        pattern = self.error_patterns[error_type]
        pattern["count"] += 1
        pattern["last_seen"] = datetime.now().isoformat()
        
        if context:
            pattern["contexts"].append(context)
        
        # Keep only last 10 contexts
        if len(pattern["contexts"]) > 10:
            pattern["contexts"] = pattern["contexts"][-10:]
    
    def get_error_insights(self) -> Dict[str, Any]:
        """Get insights from error patterns"""
        insights = {
            "total_errors": sum(p["count"] for p in self.error_patterns.values()),
            "error_types": len(self.error_patterns),
            "most_common_errors": sorted(
                self.error_patterns.items(),
                key=lambda x: x[1]["count"],
                reverse=True
            )[:5],
            "learning_insights": self.learning_insights[-10:],
        }
        
        return insights
    
    def create_release(self, version: str, ref: str = None):
        """Create a new release in Sentry"""
        if not self.initialized:
            logger.warning("Cannot create release: Sentry not available")
            return
        
        try:
            sentry_sdk.set_tag("release", version)
            sentry_sdk.set_context("release", {
                "version": version,
                "ref": ref,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Created Sentry release: {version}")
            
        except Exception as e:
            logger.error(f"Failed to create Sentry release: {e}")
    
    def set_environment(self, environment: str):
        """Set the environment for Sentry"""
        if not self.initialized:
            return
        
        try:
            sentry_sdk.set_tag("environment", environment)
            self.environment = environment
            
        except Exception as e:
            logger.error(f"Failed to set Sentry environment: {e}")
    
    def flush(self, timeout: float = 2.0):
        """Flush Sentry events"""
        if not self.initialized:
            return
        
        try:
            sentry_sdk.flush(timeout=timeout)
        except Exception as e:
            logger.error(f"Failed to flush Sentry events: {e}")


# Global Sentry instance
sentry_integration = None


def initialize_sentry(dsn: Optional[str] = None, environment: str = "development") -> SentryIntegration:
    """Initialize global Sentry integration"""
    global sentry_integration
    sentry_integration = SentryIntegration(dsn, environment)
    return sentry_integration


def get_sentry() -> Optional[SentryIntegration]:
    """Get the global Sentry integration instance"""
    return sentry_integration


def capture_error(error: Exception, context: Dict[str, Any] = None, level: str = "error"):
    """Global error capture function"""
    if sentry_integration:
        sentry_integration.capture_error(error, context, level)


def capture_message(message: str, level: str = "info", context: Dict[str, Any] = None):
    """Global message capture function"""
    if sentry_integration:
        sentry_integration.capture_message(message, level, context)


def start_transaction(name: str, operation: str = "default") -> Any:
    """Global transaction start function"""
    if sentry_integration:
        return sentry_integration.start_transaction(name, operation)
    return None


# Decorator for automatic error tracking
def track_errors(func):
    """Decorator to automatically track errors in functions"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            capture_error(e, {
                "function": func.__name__,
                "module": func.__module__,
                "args": str(args),
                "kwargs": str(kwargs)
            })
            raise
    return wrapper


# Async decorator for automatic error tracking
def track_async_errors(func):
    """Decorator to automatically track errors in async functions"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            capture_error(e, {
                "function": func.__name__,
                "module": func.__module__,
                "args": str(args),
                "kwargs": str(kwargs)
            })
            raise
    return wrapper 