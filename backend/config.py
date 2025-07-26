from pydantic import BaseSettings, Field
from typing import Optional

class BackendConfig(BaseSettings):
    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8080, description="API port")
    database_url: Optional[str] = Field(default=None, description="Database URL")
    log_level: str = Field(default="INFO", description="Logging level")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

config = BackendConfig() 