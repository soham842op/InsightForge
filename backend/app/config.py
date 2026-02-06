"""
Application Configuration

Uses pydantic-settings for type-safe environment variable loading.
This pattern is standard in production FastAPI applications.

Interview Insight:
- Environment-based configuration follows the "12-Factor App" methodology
- Secrets should NEVER be hardcoded or committed to version control
- Different environments (dev, staging, prod) use different .env files
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Pydantic Settings automatically:
    - Reads from .env file
    - Validates types
    - Provides defaults
    - Handles case-insensitivity
    """
    
    # Application
    app_name: str = "InsightForge"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"
    
    # Database
    database_url: str
    
    # Security
    secret_key: str
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Algorithm for JWT tokens
    algorithm: str = "HS256"
    
    # OAuth Providers (optional)
    google_client_id: str | None = None
    google_client_secret: str | None = None
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # OpenAI
    openai_api_key: str | None = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance.
    
    Best Practice: Using lru_cache ensures we only parse
    environment variables once, not on every request.
    
    This is a common pattern you'll see in FastAPI applications
    and is often asked about in interviews.
    """
    return Settings()
