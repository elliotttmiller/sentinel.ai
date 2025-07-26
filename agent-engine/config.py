"""
Configuration for Project Sentinel Agent Engine.

Centralized configuration management for all agent engine settings.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseSettings, Field


class AgentEngineConfig(BaseSettings):
    """Configuration settings for the Agent Engine."""
    
    # API Settings
    host: str = Field(default="0.0.0.0", description="Host to bind the API server to")
    port: int = Field(default=8001, description="Port to bind the API server to")
    
    # LLM Settings
    google_api_key: Optional[str] = Field(default=None, description="Google API key for Gemini")
    default_model: str = Field(default="gemini-1.5-pro", description="Default LLM model to use")
    
    # Vector Database Settings
    vector_db_url: Optional[str] = Field(default=None, description="Vector database URL")
    vector_db_type: str = Field(default="chromadb", description="Vector database type")
    
    # Cloudflare Tunnel Settings
    cloudflare_tunnel_token: Optional[str] = Field(default=None, description="Cloudflare tunnel token")
    tunnel_url: Optional[str] = Field(default=None, description="Cloudflare tunnel URL")
    
    # Logging Settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="logs/agent_engine.log", description="Log file path")
    
    # Workspace Settings
    workspace_path: Path = Field(default=Path.cwd(), description="Workspace path")
    logs_dir: Path = Field(default=Path("logs"), description="Logs directory")
    
    # Agent Settings
    max_concurrent_missions: int = Field(default=5, description="Maximum concurrent missions")
    mission_timeout: int = Field(default=3600, description="Mission timeout in seconds")
    
    # Memory Settings
    memory_retention_days: int = Field(default=30, description="Memory retention in days")
    max_memory_entries: int = Field(default=1000, description="Maximum memory entries")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def load_config() -> AgentEngineConfig:
    """Load configuration from environment variables and .env file."""
    return AgentEngineConfig()


def get_config() -> AgentEngineConfig:
    """Get the global configuration instance."""
    if not hasattr(get_config, '_instance'):
        get_config._instance = load_config()
    return get_config._instance


# Global configuration instance
config = get_config() 