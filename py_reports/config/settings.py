"""Application settings and configuration."""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # MongoDB settings
    mongodb_url: str = Field(
        default="mongodb://wro4.ppo.enigma.com.pl:27017",
        env="MONGODB_URL",
        description="MongoDB connection URL"
    )
    mongodb_database: str = Field(
        default="Person",
        env="MONGODB_DATABASE",
        description="MongoDB database name"
    )
    mongodb_username: Optional[str] = Field(
        default=None,
        env="MONGODB_USERNAME",
        description="MongoDB username"
    )
    mongodb_password: Optional[str] = Field(
        default=None,
        env="MONGODB_PASSWORD",
        description="MongoDB password"
    )
    
    # Report settings
    reports_dir: str = Field(
        default="reports",
        env="REPORTS_DIR",
        description="Directory containing report definitions"
    )
    templates_dir: str = Field(
        default="py_reports/templates",
        env="TEMPLATES_DIR",
        description="Directory containing Jinja2 templates"
    )
    translations_dir: str = Field(
        default="py_reports/translations",
        env="TRANSLATIONS_DIR",
        description="Directory containing translation files"
    )
    output_dir: str = Field(
        default="output",
        env="OUTPUT_DIR",
        description="Directory for generated reports"
    )
    
    # Performance settings
    max_rows_per_table: int = Field(
        default=100000,
        env="MAX_ROWS_PER_TABLE",
        description="Maximum rows per table"
    )
    max_columns_per_pivot: int = Field(
        default=200,
        env="MAX_COLUMNS_PER_PIVOT",
        description="Maximum columns per pivot table"
    )
    max_generation_time: int = Field(
        default=60,
        env="MAX_GENERATION_TIME",
        description="Maximum report generation time in seconds"
    )
    
    # API settings
    api_host: str = Field(
        default="0.0.0.0",
        env="API_HOST",
        description="API server host"
    )
    api_port: int = Field(
        default=8000,
        env="API_PORT",
        description="API server port"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        env="LOG_LEVEL",
        description="Logging level"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings (singleton pattern)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings