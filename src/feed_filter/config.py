"""
Configuration management using pydantic-settings.

This module demonstrates how to use pydantic for type-safe configuration
with automatic validation and environment variable loading.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application settings
    app_name: str = Field(default="feed-filter", description="Application name")
    app_env: str = Field(
        default="development", description="Environment (development, staging, production)"
    )
    debug: bool = Field(default=True, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # Example: API configuration
    # api_key: str = Field(..., description="API key for external service")
    # api_timeout: int = Field(default=30, description="API timeout in seconds")

    # Example: Database configuration
    # db_host: str = Field(default="localhost", description="Database host")
    # db_port: int = Field(default=5432, description="Database port")
    # db_name: str = Field(..., description="Database name")
    # db_user: str = Field(..., description="Database user")
    # db_password: str = Field(..., description="Database password")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env.lower() == "development"


# Global settings instance
settings = Settings()
