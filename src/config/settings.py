"""
Configuration Settings for Cognitive Forge v6.0 - Enhanced Multi-Agent System
Advanced configuration management with environment variable support
"""

import os
import json
from typing import Dict, Any, Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    # --- COGNITIVE FORGE v6.0 ENHANCED MULTI-AGENT FEATURES ---
    # Multi-Agent System Configuration
    MULTI_AGENT_ENABLED: bool = True
    MAX_CONCURRENT_WORKFLOWS: int = 10
    AGENT_TIMEOUT: int = 300
    LEARNING_ENABLED: bool = True
    LEARNING_RATE: float = 0.1
    
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
    HYBRID_SWITCH_THRESHOLD: float = 0.4
    
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
    
    # --- AGENT CONFIGURATION ---
    AGENT_POOL_SIZE: int = 5
    AGENT_INITIALIZATION_TIMEOUT: int = 30
    
    # Agent specializations
    RESEARCH_AGENT_ENABLED: bool = True
    PLANNING_AGENT_ENABLED: bool = True
    DEVELOPMENT_AGENT_ENABLED: bool = True
    REVIEW_AGENT_ENABLED: bool = True
    TESTING_AGENT_ENABLED: bool = True
    
    # --- WORKFLOW CONFIGURATION ---
    SEQUENTIAL_WORKFLOW_ENABLED: bool = True
    COLLABORATIVE_WORKFLOW_ENABLED: bool = True
    PARALLEL_WORKFLOW_ENABLED: bool = True
    ADAPTIVE_WORKFLOW_ENABLED: bool = True
    
    # Workflow timeouts
    SEQUENTIAL_TIMEOUT: int = 1800
    COLLABORATIVE_TIMEOUT: int = 1200
    PARALLEL_TIMEOUT: int = 900
    ADAPTIVE_TIMEOUT: int = 2400
    
    # --- OBSERVABILITY CONFIGURATION ---
    OBSERVABILITY_ENABLED: bool = True
    REAL_TIME_MONITORING: bool = True
    PERFORMANCE_TRACKING: bool = True
    AGENT_METRICS_COLLECTION: bool = True
    WORKFLOW_ANALYTICS: bool = True
    
    # --- SECURITY CONFIGURATION ---
    AGENT_ISOLATION: bool = True
    SECURE_COMMUNICATION: bool = True
    AUDIT_LOGGING: bool = True
    VULNERABILITY_SCANNING: bool = True
    
    # --- ADDITIONAL CONFIGURATION FROM ENV ---
    # Vector DB Configuration
    VECTOR_DB_URL: str = Field(default="http://localhost:8001", env="VECTOR_DB_URL")
    VECTOR_DB_TYPE: str = Field(default="chromadb", env="VECTOR_DB_TYPE")
    
    # Logging and workspace
    LOGS_DIR: str = Field(default="logs", env="LOGS_DIR")
    WORKSPACE_PATH: str = Field(default=".", env="WORKSPACE_PATH")
    
    # Mission configuration
    MAX_CONCURRENT_MISSIONS: int = Field(default=5, env="MAX_CONCURRENT_MISSIONS")
    MISSION_TIMEOUT: int = Field(default=3600, env="MISSION_TIMEOUT")
    MEMORY_RETENTION_DAYS: int = Field(default=30, env="MEMORY_RETENTION_DAYS")
    
    # Observability services
    WEAVE_PROJECT_NAME: str = Field(default="cognitive-forge-v6", env="WEAVE_PROJECT_NAME")
    WANDB_PROJECT_NAME: str = Field(default="cognitive-forge-v6", env="WANDB_PROJECT_NAME")
    
    # Sentry configuration
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    SENTRY_AUTH_TOKEN: Optional[str] = Field(default=None, env="SENTRY_AUTH_TOKEN")
    SENTRY_ORG_SLUG: Optional[str] = Field(default=None, env="SENTRY_ORG_SLUG")
    SENTRY_PROJECT_ID: Optional[str] = Field(default=None, env="SENTRY_PROJECT_ID")
    
    # Networking
    DESKTOP_TUNNEL_URL: Optional[str] = Field(default=None, env="DESKTOP_TUNNEL_URL")
    
    # Security - File and command restrictions
    ALLOWED_FILE_EXTENSIONS: List[str] = Field(default=[".py", ".js", ".html", ".css", ".json", ".txt", ".md"], env="ALLOWED_FILE_EXTENSIONS")
    ALLOWED_SHELL_COMMANDS: List[str] = Field(default=["ls", "dir", "pwd", "echo", "cat", "head", "tail", "grep", "find"], env="ALLOWED_SHELL_COMMANDS")
    
    # OpenAI API Key (for compatibility)
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    
    @field_validator('ALLOWED_FILE_EXTENSIONS', mode='before')
    @classmethod
    def parse_allowed_extensions(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return v.split(',')
        return v
    
    @field_validator('ALLOWED_SHELL_COMMANDS', mode='before')
    @classmethod
    def parse_allowed_commands(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return v.split(',')
        return v
    
    # --- WEBSOCKET CONFIGURATION ---
    WEBSOCKET_ENABLED: bool = True
    WEBSOCKET_PING_INTERVAL: int = 30
    WEBSOCKET_PING_TIMEOUT: int = 10
    MAX_WEBSOCKET_CONNECTIONS: int = 100
    WEBSOCKET_BUFFER_SIZE: int = 1024 * 64  # 64KB
    
    # --- CORS CONFIGURATION ---
    ALLOW_ORIGINS: List[str] = ["*"]
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: List[str] = ["*"]
    ALLOW_HEADERS: List[str] = ["*"]
    
    # --- AUTHENTICATION (Optional) ---
    ENABLE_AUTHENTICATION: bool = False
    JWT_SECRET_KEY: str = Field(default="dev-secret-key-change-in-production", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # --- FILE SYSTEM ---
    WORKSPACE_ROOT: str = "workspace"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [".py", ".txt", ".md", ".json", ".yaml", ".yml", ".toml"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields from environment


# Create settings instance
settings = Settings()
