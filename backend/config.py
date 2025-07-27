from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Manages application settings and secrets for the Sentinel BACKEND service.
    """
    # --- Critical Infrastructure Settings ---
    DATABASE_URL: str
    DESKTOP_TUNNEL_URL: str

    # --- Authentication (Multiple options for flexibility) ---
    GOOGLE_APPLICATION_CREDENTIALS_JSON: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None

    # --- LLM Settings ---
    DEFAULT_MODEL: str = "gemini-1.5-pro"
    
    # --- General Settings ---
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings() 