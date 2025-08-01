"""
Configuration Settings for Cognitive Forge v5.0
Advanced configuration management with environment variable support
"""

import os
from typing import Dict, Any, Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    # --- COGNITIVE FORGE v5.0 FEATURE FLAGS ---
    # Hybrid Decision Engine
    ENABLE_HYBRID_MODE: bool = True
    AUTO_SWITCHING: bool = True
    
    # Golden Path Feature Flags
    ENABLE_FULL_WORKFLOW: bool = False
    MINIMAL_MODE: bool = True
    GOLDEN_PATH_LOGGING: bool = True
    
    # Advanced AI Features
    ENABLE_ML_PREDICTION: bool = True
    ENABLE_PREDICTIVE_CACHING: bool = True
    ENABLE_ADVANCED_ANALYTICS: bool = True
    ENABLE_DYNAMIC_THRESHOLDS: bool = True
    
    # --- HYBRID SYSTEM CONFIGURATION ---
    # Complexity analysis thresholds
    SIMPLE_TASK_KEYWORDS: List[str] = [
        "hello", "simple", "basic", "quick", "function", "print", 
        "calculate", "add", "multiply", "convert", "format", "sort",
        "test", "check", "verify", "list", "show", "display"
    ]
    COMPLEX_TASK_KEYWORDS: List[str] = [
        "design", "architecture", "system", "complex", "advanced",
        "algorithm", "optimization", "machine learning", "neural network",
        "database", "api", "framework", "microservice", "distributed",
        "refactor", "implement", "create a script", "build an app"
    ]
    
    # Performance thresholds (seconds)
    GOLDEN_PATH_TIME_LIMIT: float = 5.0
    FULL_WORKFLOW_TIME_LIMIT: float = 60.0
    HYBRID_SWITCH_THRESHOLD: float = 0.6
    
    # Decision weights (0.0 to 1.0)
    USER_PREFERENCE_WEIGHT: float = 0.3
    PERFORMANCE_WEIGHT: float = 0.4
    COMPLEXITY_WEIGHT: float = 0.3
    
    # Machine learning configuration
    ML_MODEL_UPDATE_INTERVAL: int = 3600  # 1 hour
    MIN_TRAINING_SAMPLES: int = 50
    
    # Predictive caching
    CACHE_SIZE_LIMIT: int = 1000
    CACHE_TTL: int = 3600  # 1 hour
    
    # Advanced analytics
    ANALYTICS_SAMPLE_RATE: float = 0.1  # 10% of requests
    PERFORMANCE_METRICS_RETENTION: int = 86400  # 24 hours
    
    # Dynamic threshold adjustment
    THRESHOLD_UPDATE_INTERVAL: int = 1800  # 30 minutes
    THRESHOLD_LEARNING_RATE: float = 0.1
    
    # --- SERVER CONFIGURATION ---
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8001, env="PORT")
    SERVER_8001_PORT: int = 8001
    SERVER_8002_PORT: int = 8002
    SERVER_HOST: str = "0.0.0.0"
    RELOAD: bool = Field(default=True, env="RELOAD")
    
    # --- LLM CONFIGURATION ---
    GOOGLE_API_KEY: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = Field(
        default=None, env="GOOGLE_APPLICATION_CREDENTIALS"
    )
    LLM_MODEL: str = Field(default="gemini-1.5-pro-latest", env="LLM_MODEL")
    LLM_TEMPERATURE: float = Field(default=0.7, env="LLM_TEMPERATURE")
    
    # --- DATABASE CONFIGURATION ---
    DATABASE_URL: str = Field(default="sqlite:///db/sentinel_missions.db", env="DATABASE_URL")
    POSTGRES_URL: Optional[str] = None
    CHROMA_PERSIST_DIRECTORY: str = "db/chroma_memory"
    CHROMA_PATH: str = Field(default="db/chroma_memory", env="CHROMA_PATH")
    
    # --- LOGGING CONFIGURATION ---
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="logs/cognitive_forge.log", env="LOG_FILE")
    LOG_ROTATION: str = Field(default="10 MB", env="LOG_ROTATION")
    LOG_RETENTION: str = Field(default="7 days", env="LOG_RETENTION")
    LOG_BUFFER_SIZE: int = 200
    LOG_FORWARDING_INTERVAL: int = 2
    SSE_KEEPALIVE_INTERVAL: int = 25
    
    # --- MISSION CONFIGURATION ---
    MAX_MISSION_DURATION: int = Field(default=3600, env="MAX_MISSION_DURATION")  # seconds
    MAX_CONCURRENT_MISSIONS: int = Field(default=5, env="MAX_CONCURRENT_MISSIONS")
    MISSION_TIMEOUT: int = Field(default=3600, env="MISSION_TIMEOUT")  # seconds
    STUCK_MISSION_TIMEOUT: int = 300  # 5 minutes
    BACKGROUND_TASK_TIMEOUT: int = 3   # 3 seconds per step
    
    # --- MEMORY CONFIGURATION ---
    MEMORY_SEARCH_LIMIT: int = Field(default=5, env="MEMORY_SEARCH_LIMIT")
    MEMORY_SYNTHESIS_ENABLED: bool = Field(default=True, env="MEMORY_SYNTHESIS_ENABLED")
    MEMORY_RETENTION_DAYS: int = Field(default=30, env="MEMORY_RETENTION_DAYS")
    MAX_MEMORY_ENTRIES: int = Field(default=1000, env="MAX_MEMORY_ENTRIES")
    
    # --- SECURITY SETTINGS ---
    ALLOWED_FILE_EXTENSIONS: List[str] = Field(
        default=[".py", ".js", ".html", ".css", ".json", ".txt", ".md", ".yml", ".yaml"],
        env="ALLOWED_FILE_EXTENSIONS",
    )
    ALLOWED_SHELL_COMMANDS: List[str] = Field(
        default=[
            "ls", "dir", "pwd", "echo", "cat", "head", "tail", "grep", "find",
            "python", "pip", "node", "npm", "git", "mkdir", "touch", "cp", "mv",
            "python -m py_compile", "python -c", "pip list", "pip show",
        ],
        env="ALLOWED_SHELL_COMMANDS",
    )
    
    # --- AGENT SETTINGS ---
    ENABLE_PLAN_VALIDATION: bool = Field(default=True, env="ENABLE_PLAN_VALIDATION")
    ENABLE_MEMORY_SYNTHESIS: bool = Field(default=True, env="ENABLE_MEMORY_SYNTHESIS")
    ENABLE_REAL_TIME_UPDATES: bool = Field(default=True, env="ENABLE_REAL_TIME_UPDATES")
    
    # --- PERFORMANCE SETTINGS ---
    WORKER_TIMEOUT: int = Field(default=60, env="WORKER_TIMEOUT")  # seconds
    PLANNING_TIMEOUT: int = Field(default=120, env="PLANNING_TIMEOUT")  # seconds
    
    # --- ADDITIONAL SETTINGS ---
    WORKSPACE_PATH: str = Field(default=".", env="WORKSPACE_PATH")
    LOGS_DIR: str = Field(default="logs", env="LOGS_DIR")
    DESKTOP_TUNNEL_URL: Optional[str] = Field(default=None, env="DESKTOP_TUNNEL_URL")
    VECTOR_DB_URL: str = Field(default="http://localhost:8000", env="VECTOR_DB_URL")
    VECTOR_DB_TYPE: str = Field(default="chromadb", env="VECTOR_DB_TYPE")
    
    # --- SENTRY CONFIGURATION ---
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    SENTRY_AUTH_TOKEN: Optional[str] = Field(default=None, env="SENTRY_AUTH_TOKEN")
    SENTRY_ORG_SLUG: Optional[str] = Field(default=None, env="SENTRY_ORG_SLUG")
    SENTRY_PROJECT_ID: Optional[str] = Field(default=None, env="SENTRY_PROJECT_ID")
    
    # Application Settings
    app_name: str = "Sentinel Cognitive Forge v5.0"
    app_version: str = "5.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra fields from .env
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration"""
        return {
            "model": self.LLM_MODEL,
            "temperature": self.LLM_TEMPERATURE,
            "api_key": self.GOOGLE_API_KEY,
            "credentials": self.GOOGLE_APPLICATION_CREDENTIALS,
        }
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return {
            "url": self.DATABASE_URL,
            "chroma_path": self.CHROMA_PATH,
            "vector_db_url": self.VECTOR_DB_URL,
            "vector_db_type": self.VECTOR_DB_TYPE,
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            "level": self.LOG_LEVEL,
            "file": self.LOG_FILE,
            "rotation": self.LOG_ROTATION,
            "retention": self.LOG_RETENTION,
            "buffer_size": self.LOG_BUFFER_SIZE,
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return {
            "allowed_extensions": set(self.ALLOWED_FILE_EXTENSIONS),
            "allowed_commands": set(self.ALLOWED_SHELL_COMMANDS),
        }
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration"""
        return {
            "enable_plan_validation": self.ENABLE_PLAN_VALIDATION,
            "enable_memory_synthesis": self.ENABLE_MEMORY_SYNTHESIS,
            "enable_real_time_updates": self.ENABLE_REAL_TIME_UPDATES,
            "worker_timeout": self.WORKER_TIMEOUT,
            "planning_timeout": self.PLANNING_TIMEOUT,
        }


def get_settings() -> Settings:
    """Get application settings"""
    return Settings()


def validate_environment() -> bool:
    """Validate environment configuration"""
    settings = get_settings()
    
    # Check required settings
    if not settings.GOOGLE_API_KEY:
        print("❌ GOOGLE_API_KEY is required")
        return False
    
    if not settings.DATABASE_URL:
        print("❌ DATABASE_URL is required")
        return False
    
    # Check optional but recommended settings
    if not settings.SENTRY_DSN:
        print("⚠️  SENTRY_DSN not set - error tracking disabled")
    
    print("✅ Environment validation passed")
    return True


def create_env_template():
    """Create environment template"""
    template = """
# Cognitive Forge v5.0 Environment Configuration

# --- HYBRID SYSTEM CONFIGURATION ---
ENABLE_HYBRID_MODE=true
AUTO_SWITCHING=true

# --- GOLDEN PATH FEATURE FLAGS ---
ENABLE_FULL_WORKFLOW=false
MINIMAL_MODE=true
GOLDEN_PATH_LOGGING=true

# --- SERVER CONFIGURATION ---
HOST=0.0.0.0
PORT=8001
SERVER_8001_PORT=8001
SERVER_8002_PORT=8002
SERVER_HOST=0.0.0.0

# --- GOOGLE AI CONFIGURATION ---
GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
GOOGLE_API_KEY=your_google_api_key_here
LLM_MODEL=gemini-1.5-pro-latest
LLM_TEMPERATURE=0.7

# --- DATABASE CONFIGURATION ---
DATABASE_URL=sqlite:///db/sentinel_missions.db

# --- LOGGING CONFIGURATION ---
LOG_LEVEL=INFO
LOGS_DIR=logs
LOG_BUFFER_SIZE=200
LOG_FORWARDING_INTERVAL=2
SSE_KEEPALIVE_INTERVAL=25

# --- MISSION CONFIGURATION ---
MAX_CONCURRENT_MISSIONS=5
MISSION_TIMEOUT=3600
STUCK_MISSION_TIMEOUT=300
BACKGROUND_TASK_TIMEOUT=3

# --- MEMORY CONFIGURATION ---
MEMORY_RETENTION_DAYS=30
MAX_MEMORY_ENTRIES=1000

# --- HYBRID SYSTEM ADVANCED CONFIGURATION ---
HYBRID_SWITCH_THRESHOLD=0.6
USER_PREFERENCE_WEIGHT=0.3
PERFORMANCE_WEIGHT=0.4
COMPLEXITY_WEIGHT=0.3

# --- MACHINE LEARNING CONFIGURATION ---
ENABLE_ML_PREDICTION=true
ML_MODEL_UPDATE_INTERVAL=3600
MIN_TRAINING_SAMPLES=50

# --- PREDICTIVE CACHING ---
ENABLE_PREDICTIVE_CACHING=true
CACHE_SIZE_LIMIT=1000
CACHE_TTL=3600

# --- ADVANCED ANALYTICS ---
ENABLE_ADVANCED_ANALYTICS=true
ANALYTICS_SAMPLE_RATE=0.1
PERFORMANCE_METRICS_RETENTION=86400

# --- DYNAMIC THRESHOLD ADJUSTMENT ---
ENABLE_DYNAMIC_THRESHOLDS=true
THRESHOLD_UPDATE_INTERVAL=1800
THRESHOLD_LEARNING_RATE=0.1

# --- PERFORMANCE THRESHOLDS ---
GOLDEN_PATH_TIME_LIMIT=5.0
FULL_WORKFLOW_TIME_LIMIT=60.0
"""
    return template


# Global settings instance
settings = get_settings()
