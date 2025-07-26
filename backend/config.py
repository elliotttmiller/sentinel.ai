from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings for the Sentinel Backend."""
    
    # Database Configuration
    DATABASE_URL: str
    
    # API Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    LOG_LEVEL: str = "INFO"
    
    # Desktop Engine Configuration
    DESKTOP_TUNNEL_URL: Optional[str] = None
    
    # Google GenAI Configuration
    GOOGLE_APPLICATION_CREDENTIALS_JSON: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings() 