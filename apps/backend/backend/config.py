"""
Application configuration management.
Loads environment variables and provides typed configuration.
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Settings
    APP_NAME: str = "AI Career Management Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production-min-32-chars"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-this-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS Settings
    CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # Database Configuration
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/ai_career_platform"

    # LLM Configuration
    LLM_PROVIDER: str = "deepseek"

    # DeepSeek Configuration
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"

    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Anthropic Configuration
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    # File Storage Configuration
    STORAGE_TYPE: str = "local"
    LOCAL_STORAGE_PATH: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_UPLOAD_TYPES: List[str] = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "image/jpeg",
        "image/png",
    ]

    # Azure Blob Storage Settings
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    AZURE_STORAGE_CONTAINER: Optional[str] = None
    AZURE_STORAGE_ACCOUNT_NAME: Optional[str] = None
    AZURE_STORAGE_ACCOUNT_KEY: Optional[str] = None

    # AI Configuration
    AI_MAX_TOKENS: int = 2000
    AI_TEMPERATURE: float = 0.7
    AI_TOP_P: float = 0.9

    # Email Configuration (Optional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: str = "AI Career Platform"

    # Redis Configuration (Optional)
    REDIS_URL: Optional[str] = None

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    @validator("LLM_PROVIDER")
    def validate_llm_provider(cls, v):
        """Validate LLM provider."""
        allowed_providers = ["deepseek", "openai", "anthropic"]
        if v not in allowed_providers:
            raise ValueError(f"LLM_PROVIDER must be one of {allowed_providers}")
        return v

    @validator("STORAGE_TYPE")
    def validate_storage_type(cls, v):
        """Validate storage type."""
        allowed_types = ["local", "azure"]
        if v not in allowed_types:
            raise ValueError(f"STORAGE_TYPE must be one of {allowed_types}")
        return v

    @validator("AI_TEMPERATURE")
    def validate_temperature(cls, v):
        """Validate AI temperature."""
        if not 0 <= v <= 2:
            raise ValueError("AI_TEMPERATURE must be between 0 and 2")
        return v

    @validator("AI_TOP_P")
    def validate_top_p(cls, v):
        """Validate AI top_p."""
        if not 0 <= v <= 1:
            raise ValueError("AI_TOP_P must be between 0 and 1")
        return v

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        validate_assignment = True


# Global settings instance
settings = Settings()
