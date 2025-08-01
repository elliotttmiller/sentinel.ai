"""
Configuration Settings for Cognitive Forge
Centralized configuration management with environment variable support
"""

import os
from typing import Dict, Any, Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    # --- Golden Path Feature Flags ---
    # When True, missions use the full 8-phase AI workflow
    # When False, they use the simple, direct-to-LLM golden path
    ENABLE_FULL_WORKFLOW: bool = False
    
    # When True, enables minimal mode for faster testing
    MINIMAL_MODE: bool = True
    
    # When True, enables detailed logging for golden path operations
    GOLDEN_PATH_LOGGING: bool = True
    
    # --- HYBRID SYSTEM CONFIGURATION ---
    # Enable intelligent hybrid routing
    ENABLE_HYBRID_MODE: bool = True
    AUTO_SWITCHING: bool = True
    
    # Complexity analysis thresholds
    SIMPLE_TASK_KEYWORDS: List[str] = [
        "hello", "simple", "basic", "quick", "function", "print", 
        "calculate", "add", "multiply", "convert", "format", "sort"
    ]
    COMPLEX_TASK_KEYWORDS: List[str] = [
        "design", "architecture", "system", "complex", "advanced",
        "algorithm", "optimization", "machine learning", "neural network",
        "database", "api", "framework", "microservice", "distributed"
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
    ENABLE_ML_PREDICTION: bool = True
    ML_MODEL_UPDATE_INTERVAL: int = 3600  # 1 hour
    MIN_TRAINING_SAMPLES: int = 50
    
    # Predictive caching
    ENABLE_PREDICTIVE_CACHING: bool = True
    CACHE_SIZE_LIMIT: int = 1000
    CACHE_TTL: int = 3600  # 1 hour
    
    # Advanced analytics
    ENABLE_ADVANCED_ANALYTICS: bool = True
    ANALYTICS_SAMPLE_RATE: float = 0.1  # 10% of requests
    PERFORMANCE_METRICS_RETENTION: int = 86400  # 24 hours
    
    # Dynamic threshold adjustment
    ENABLE_DYNAMIC_THRESHOLDS: bool = True
    THRESHOLD_UPDATE_INTERVAL: int = 1800  # 30 minutes
    THRESHOLD_LEARNING_RATE: float = 0.1
    
    # --- Existing Settings ---
    GOOGLE_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gemini-1.5-flash"
    DATABASE_URL: str = "sqlite:///db/sentinel_missions.db"
    LOG_LEVEL: str = "INFO"
    
    # --- Server Configuration ---
    SERVER_8001_PORT: int = 8001
    SERVER_8002_PORT: int = 8002
    SERVER_HOST: str = "0.0.0.0"
    
    # --- Database Configuration ---
    POSTGRES_URL: Optional[str] = None
    CHROMA_PERSIST_DIRECTORY: str = "db/chroma_memory"
    
    # --- Logging Configuration ---
    LOG_BUFFER_SIZE: int = 200
    LOG_FORWARDING_INTERVAL: int = 2
    SSE_KEEPALIVE_INTERVAL: int = 25
    
    # --- Mission Configuration ---
    STUCK_MISSION_TIMEOUT: int = 300  # 5 minutes
    BACKGROUND_TASK_TIMEOUT: int = 3   # 3 seconds per step
    
    # Application Settings
    app_name: str = "Sentinel Cognitive Forge"
    app_version: str = "3.0.0"
    debug: bool = Field(default=False, env="DEBUG")

    # Server Settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8081, env="PORT")
    reload: bool = Field(default=True, env="RELOAD")

    # LLM Configuration
    llm_model: str = Field(default="gemini-1.5-pro-latest", env="LLM_MODEL")
    llm_temperature: float = Field(default=0.7, env="LLM_TEMPERATURE")
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    google_application_credentials: Optional[str] = Field(
        default=None, env="GOOGLE_APPLICATION_CREDENTIALS"
    )

    # Database Settings
    database_url: str = Field(default="sqlite:///db/sentinel_missions.db", env="DATABASE_URL")
    vector_db_url: str = Field(default="http://localhost:8000", env="VECTOR_DB_URL")
    vector_db_type: str = Field(default="chromadb", env="VECTOR_DB_TYPE")
    chroma_path: str = Field(default="db/chroma_memory", env="CHROMA_PATH")

    # Logging Settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/cognitive_forge.log", env="LOG_FILE")
    log_rotation: str = Field(default="10 MB", env="LOG_ROTATION")
    log_retention: str = Field(default="7 days", env="LOG_RETENTION")

    # Mission Settings
    max_mission_duration: int = Field(default=3600, env="MAX_MISSION_DURATION")  # seconds
    max_concurrent_missions: int = Field(default=5, env="MAX_CONCURRENT_MISSIONS")
    mission_timeout: int = Field(default=3600, env="MISSION_TIMEOUT")  # seconds

    # Memory Settings
    memory_search_limit: int = Field(default=5, env="MEMORY_SEARCH_LIMIT")
    memory_synthesis_enabled: bool = Field(default=True, env="MEMORY_SYNTHESIS_ENABLED")
    memory_retention_days: int = Field(default=30, env="MEMORY_RETENTION_DAYS")
    max_memory_entries: int = Field(default=1000, env="MAX_MEMORY_ENTRIES")

    # Security Settings
    allowed_file_extensions: set = Field(
        default={".py", ".js", ".html", ".css", ".json", ".txt", ".md", ".yml", ".yaml"},
        env="ALLOWED_FILE_EXTENSIONS",
    )
    allowed_shell_commands: set = Field(
        default={
            "ls",
            "dir",
            "pwd",
            "echo",
            "cat",
            "head",
            "tail",
            "grep",
            "find",
            "python",
            "pip",
            "node",
            "npm",
            "git",
            "mkdir",
            "touch",
            "cp",
            "mv",
            "python -m py_compile",
            "python -c",
            "pip list",
            "pip show",
        },
        env="ALLOWED_SHELL_COMMANDS",
    )

    # Agent Settings
    enable_plan_validation: bool = Field(default=True, env="ENABLE_PLAN_VALIDATION")
    enable_memory_synthesis: bool = Field(default=True, env="ENABLE_MEMORY_SYNTHESIS")
    enable_real_time_updates: bool = Field(default=True, env="ENABLE_REAL_TIME_UPDATES")

    # Performance Settings
    worker_timeout: int = Field(default=60, env="WORKER_TIMEOUT")  # seconds
    planning_timeout: int = Field(default=120, env="PLANNING_TIMEOUT")  # seconds

    # Additional Settings
    workspace_path: str = Field(default=".", env="WORKSPACE_PATH")
    logs_dir: str = Field(default="logs", env="LOGS_DIR")
    desktop_tunnel_url: Optional[str] = Field(default=None, env="DESKTOP_TUNNEL_URL")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra fields from .env

    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration"""
        return {
            "model": self.llm_model,
            "temperature": self.llm_temperature,
            "api_key": self.google_api_key,
        }

    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return {"url": self.database_url, "chroma_path": self.chroma_path}

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            "level": self.log_level,
            "file": self.log_file,
            "rotation": self.log_rotation,
            "retention": self.log_retention,
        }

    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return {
            "allowed_file_extensions": self.allowed_file_extensions,
            "allowed_shell_commands": self.allowed_shell_commands,
        }

    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration"""
        return {
            "enable_plan_validation": self.enable_plan_validation,
            "enable_memory_synthesis": self.enable_memory_synthesis,
            "enable_real_time_updates": self.enable_real_time_updates,
            "worker_timeout": self.worker_timeout,
            "planning_timeout": self.planning_timeout,
        }


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance"""
    return settings


def validate_environment() -> bool:
    """Validate that all required environment variables are set"""
    required_vars = ["GOOGLE_API_KEY"]
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file")
        return False

    print("✅ Environment validation passed")
    return True


def create_env_template():
    """Create a template .env file"""
    template = """# Cognitive Forge Environment Configuration

# Application Settings
DEBUG=false
HOST=0.0.0.0
PORT=8001
RELOAD=true

# LLM Configuration
LLM_MODEL=gemini-1.5-pro-latest
LLM_TEMPERATURE=0.7
GOOGLE_API_KEY=your_google_api_key_here

# Database Settings
DATABASE_URL=sqlite:///db/sentinel_missions.db
CHROMA_PATH=db/chroma_memory

# Logging Settings
LOG_LEVEL=INFO
LOG_FILE=logs/cognitive_forge.log
LOG_ROTATION=10 MB
LOG_RETENTION=7 days

# Mission Settings
MAX_MISSION_DURATION=300
MAX_CONCURRENT_MISSIONS=5

# Memory Settings
MEMORY_SEARCH_LIMIT=5
MEMORY_SYNTHESIS_ENABLED=true

# Security Settings
ALLOWED_FILE_EXTENSIONS=.py,.js,.html,.css,.json,.txt,.md,.yml,.yaml
ALLOWED_SHELL_COMMANDS=ls,dir,pwd,echo,cat,head,tail,grep,find,python,pip,node,npm,git,mkdir,touch,cp,mv

# Agent Settings
ENABLE_PLAN_VALIDATION=true
ENABLE_MEMORY_SYNTHESIS=true
ENABLE_REAL_TIME_UPDATES=true

# Performance Settings
WORKER_TIMEOUT=60
PLANNING_TIMEOUT=120
"""

    with open(".env.template", "w") as f:
        f.write(template)

    print("📝 Created .env.template file")
    print("Please copy this to .env and configure your settings")
