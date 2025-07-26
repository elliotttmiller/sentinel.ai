from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Manages application settings and secrets for the Sentinel Backend and Engine.
    This class defines ALL possible configuration variables for the entire project.
    """

    # --- Backend (Railway) Specific Settings ---
    DATABASE_URL: str
    DESKTOP_TUNNEL_URL: str

    # --- Engine (Desktop) Specific Settings ---
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    VECTOR_DB_URL: Optional[str] = "http://localhost:8000"
    VECTOR_DB_TYPE: Optional[str] = "chromadb"
    CLOUDFLARE_TUNNEL_TOKEN: Optional[str] = None
    WORKSPACE_PATH: Optional[str] = "."
    LOGS_DIR: Optional[str] = "logs"

    # --- Shared LLM and Mission Settings ---
    DEFAULT_MODEL: str = "gemini-1.5-pro"
    MAX_CONCURRENT_MISSIONS: int = 5
    MISSION_TIMEOUT: int = 3600
    
    # --- Shared Memory Settings ---
    MEMORY_RETENTION_DAYS: int = 30
    MAX_MEMORY_ENTRIES: int = 1000

    # --- Authentication (Handled carefully) ---
    GOOGLE_APPLICATION_CREDENTIALS_JSON: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    
    # --- General Settings ---
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = 'ignore'

settings = Settings() 