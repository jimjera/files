"""
Configuration management for Wesza API.

This module uses Pydantic settings to manage environment variables
with type validation and default values.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        ENV: Environment name (development, production).
        PORT: Server port number.
        DATABASE_URL: PostgreSQL connection string.
        SUPABASE_URL: Supabase project URL.
        SUPABASE_KEY: Supabase anon key.
        SECRET_KEY: Secret key for JWT token signing.
        ALGORITHM: JWT algorithm (default: HS256).
        ACCESS_TOKEN_EXPIRE_MINUTES: JWT token expiration time.
        GROQ_API_KEY: Groq API key for AI inference.
        SPACES_KEY: DigitalOcean Spaces access key.
        SPACES_SECRET: DigitalOcean Spaces secret key.
        SPACES_REGION: DigitalOcean Spaces region.
        SPACES_BUCKET_NAME: DigitalOcean Spaces bucket name.
        SPACES_ENDPOINT: DigitalOcean Spaces endpoint URL.
        REDIS_URL: Redis connection URL for Celery.
        LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR).
        ALLOWED_ORIGINS: List of allowed CORS origins.
        VERSION: API version.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # FastAPI
    ENV: str = "development"
    PORT: int = 8000
    VERSION: str = "2.0"
    
    # Database (Supabase)
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI (Groq)
    GROQ_API_KEY: str
    
    # Storage (DigitalOcean Spaces)
    SPACES_KEY: str
    SPACES_SECRET: str
    SPACES_REGION: str = "nyc3"
    SPACES_BUCKET_NAME: str = "wesza-apps"
    SPACES_ENDPOINT: str = "https://nyc3.digitaloceanspaces.com"
    
    # Queue (Redis)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://wesza.online",
    ]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENV == "production"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings: Cached application settings.
    """
    return Settings()


# Export settings instance
settings = get_settings()
