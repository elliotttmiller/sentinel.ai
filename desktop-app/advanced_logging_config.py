#!/usr/bin/env python3
"""
Advanced Logging Configuration for Sentinel System
Provides comprehensive debugging and monitoring capabilities
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from loguru import logger
import json
import traceback
from typing import Dict, Any, Optional
import threading
import time

class AdvancedLogger:
    """Advanced logging system with intelligent debugging"""
    
    def __init__(self, system_name: str = "Sentinel"):
        self.system_name = system_name
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Configure comprehensive logging
        self.setup_logging()
        
        # Performance tracking
        self.performance_metrics = {}
        self.error_counts = {}
        self.start_time = time.time()
    
    def setup_logging(self):
        """Setup comprehensive logging system"""
        # Remove default logger
        logger.remove()
        
        # Console logger with colors and levels
        logger.add(
            lambda msg: self._console_handler(msg),
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
            colorize=True
        )
        
        # Main system log
        logger.add(
            self.log_dir / "sentinel_system.log",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation="50 MB",
            retention="30 days",
            compression="zip"
        )
        
        # Error log with detailed stack traces
        logger.add(
            self.log_dir / "sentinel_errors.log",
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}\n{traceback}",
            rotation="10 MB",
            retention="90 days",
            compression="zip"
        )
        
        # Performance log
        logger.add(
            self.log_dir / "sentinel_performance.log",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | PERFORMANCE | {message}",
            filter=lambda record: "PERFORMANCE" in record["message"],
            rotation="20 MB",
            retention="60 days"
        )
        
        # API access log
        logger.add(
            self.log_dir / "sentinel_api.log",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | API | {message}",
            filter=lambda record: "API" in record["message"],
            rotation="30 MB",
            retention="45 days"
        )
        
        # AI operations log
        logger.add(
            self.log_dir / "sentinel_ai.log",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | AI | {message}",
            filter=lambda record: "AI" in record["message"],
            rotation="25 MB",
            retention="60 days"
        )
        
        # Database operations log
        logger.add(
            self.log_dir / "sentinel_database.log",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | DATABASE | {message}",
            filter=lambda record: "DATABASE" in record["message"],
            rotation="15 MB",
            retention="90 days"
        )
    
    def _console_handler(self, msg):
        """Custom console handler with intelligent formatting"""
        import colorama
        from colorama import Fore, Style
        
        # Parse the log message
        parts = msg.split(" | ")
        if len(parts) >= 4:
            timestamp, level, location, message = parts[0], parts[1], parts[2], " | ".join(parts[3:])
            
            # Color coding based on level
            level_colors = {
                "DEBUG": Fore.BLUE,
                "INFO": Fore.GREEN,
                "WARNING": Fore.YELLOW,
                "ERROR": Fore.RED,
                "CRITICAL": Fore.RED + Style.BRIGHT
            }
            
            color = level_colors.get(level.strip(), Fore.WHITE)
            print(f"{color}{level}{Style.RESET_ALL} | {location} | {message}")
        else:
            print(msg)
    
    def log_system_startup(self, components: Dict[str, Any]):
        """Log system startup with component status"""
        logger.info(f"[STARTUP] {self.system_name} System Starting Up")
        logger.info(f"Startup timestamp: {datetime.now().isoformat()}")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        
        for component, status in components.items():
            if status:
                logger.info(f"[OK] {component}: Initialized successfully")
            else:
                logger.error(f"[ERROR] {component}: Failed to initialize")
    
    def log_api_request(self, method: str, endpoint: str, status_code: int, 
                       response_time: float, user_agent: str = None, 
                       request_data: Dict[str, Any] = None):
        """Log API request with detailed information"""
        logger.info(f"API | {method} {endpoint} | Status: {status_code} | Time: {response_time:.3f}s")
        
        if user_agent:
            logger.debug(f"API | User-Agent: {user_agent}")
        
        if request_data:
            logger.debug(f"API | Request data: {json.dumps(request_data, default=str)}")
        
        # Track performance
        if endpoint not in self.performance_metrics:
            self.performance_metrics[endpoint] = []
        
        self.performance_metrics[endpoint].append({
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "status_code": status_code,
            "response_time": response_time
        })
    
    def log_ai_operation(self, operation: str, prompt: str, result: Any, 
                        duration: float, model: str = None):
        """Log AI operations with detailed information"""
        logger.info(f"AI | Operation: {operation} | Duration: {duration:.3f}s | Model: {model}")
        logger.debug(f"AI | Prompt: {prompt[:200]}...")
        logger.debug(f"AI | Result: {str(result)[:500]}...")
    
    def log_database_operation(self, operation: str, table: str, 
                              query: str, duration: float, rows_affected: int = None):
        """Log database operations with performance metrics"""
        logger.info(f"DATABASE | {operation} | Table: {table} | Duration: {duration:.3f}s")
        logger.debug(f"DATABASE | Query: {query}")
        
        if rows_affected is not None:
            logger.debug(f"DATABASE | Rows affected: {rows_affected}")
    
    def log_performance_metric(self, metric_name: str, value: float, 
                              threshold: float = None, unit: str = ""):
        """Log performance metrics with threshold checking"""
        logger.info(f"PERFORMANCE | {metric_name}: {value:.2f}{unit}")
        
        if threshold and value > threshold:
            logger.warning(f"PERFORMANCE | {metric_name} exceeds threshold: {value:.2f}{unit} > {threshold:.2f}{unit}")
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any] = None):
        """Log errors with detailed context and stack trace"""
        error_type = type(error).__name__
        error_msg = str(error)
        stack_trace = traceback.format_exc()
        
        logger.error(f"ERROR | Type: {error_type} | Message: {error_msg}")
        logger.error(f"ERROR | Stack trace:\n{stack_trace}")
        
        if context:
            logger.error(f"ERROR | Context: {json.dumps(context, default=str)}")
        
        # Track error counts
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
    
    def log_system_health(self, metrics: Dict[str, Any]):
        """Log system health metrics"""
        logger.info(f"HEALTH | Memory: {metrics.get('memory', 0):.2f}MB | CPU: {metrics.get('cpu', 0):.1f}%")
        
        # Check for health issues
        if metrics.get('memory', 0) > 1000:  # 1GB
            logger.warning("HEALTH | High memory usage detected")
        
        if metrics.get('cpu', 0) > 80:
            logger.warning("HEALTH | High CPU usage detected")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all endpoints"""
        summary = {}
        
        for endpoint, metrics in self.performance_metrics.items():
            if metrics:
                response_times = [m["response_time"] for m in metrics]
                status_codes = [m["status_code"] for m in metrics]
                
                summary[endpoint] = {
                    "total_requests": len(metrics),
                    "avg_response_time": sum(response_times) / len(response_times),
                    "max_response_time": max(response_times),
                    "min_response_time": min(response_times),
                    "success_rate": len([s for s in status_codes if 200 <= s < 300]) / len(status_codes),
                    "last_request": metrics[-1]["timestamp"] if metrics else None
                }
        
        return summary
    
    def get_error_summary(self) -> Dict[str, int]:
        """Get error summary"""
        return self.error_counts.copy()
    
    def log_comprehensive_report(self):
        """Log comprehensive system report"""
        uptime = time.time() - self.start_time
        
        logger.info("[STATS] COMPREHENSIVE SYSTEM REPORT")
        logger.info(f"Uptime: {uptime:.2f} seconds")
        
        # Performance summary
        perf_summary = self.get_performance_summary()
        logger.info("Performance Summary:")
        for endpoint, metrics in perf_summary.items():
            logger.info(f"  {endpoint}: {metrics['total_requests']} requests, "
                       f"avg {metrics['avg_response_time']:.3f}s, "
                       f"success rate {metrics['success_rate']:.1%}")
        
        # Error summary
        error_summary = self.get_error_summary()
        if error_summary:
            logger.info("Error Summary:")
            for error_type, count in error_summary.items():
                logger.info(f"  {error_type}: {count} occurrences")
        else:
            logger.info("[OK] No errors recorded")
    
    def create_debug_snapshot(self) -> Dict[str, Any]:
        """Create a debug snapshot of the current system state"""
        import psutil
        
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "python_version": sys.version,
                "working_directory": os.getcwd(),
                "uptime": time.time() - self.start_time
            },
            "performance_metrics": self.get_performance_summary(),
            "error_counts": self.get_error_summary(),
            "system_resources": {
                "memory_usage": psutil.virtual_memory().percent,
                "cpu_usage": psutil.cpu_percent(),
                "disk_usage": psutil.disk_usage('/').percent
            }
        }
        
        return snapshot

# Global logger instance
advanced_logger = AdvancedLogger("Sentinel")

def get_logger():
    """Get the global advanced logger instance"""
    return advanced_logger

if __name__ == "__main__":
    # Test the advanced logging system
    logger = get_logger()
    
    logger.log_system_startup({
        "Database": True,
        "API Server": True,
        "AI Engine": True,
        "Web Interface": True
    })
    
    logger.log_api_request("GET", "/missions", 200, 0.125)
    logger.log_ai_operation("code_generation", "Create a function", "def test(): pass", 1.5, "gemini-1.5-pro")
    logger.log_database_operation("SELECT", "missions", "SELECT * FROM missions", 0.050, 5)
    logger.log_performance_metric("Memory Usage", 512.5, 1000, "MB")
    logger.log_system_health({"memory": 512.5, "cpu": 25.3})
    
    logger.log_comprehensive_report() 