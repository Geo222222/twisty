"""
TwistyVoice Configuration Settings

This module handles all application configuration using Pydantic Settings.
"""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Settings
    APP_NAME: str = Field(default="TwistyVoice", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    DEBUG: bool = Field(default=False, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite:///./twistyvoice.db",
        description="Database connection URL"
    )
    
    # Square API Configuration
    SQUARE_APPLICATION_ID: str = Field(description="Square Application ID")
    SQUARE_ACCESS_TOKEN: str = Field(description="Square Access Token")
    SQUARE_ENVIRONMENT: str = Field(
        default="sandbox",
        description="Square environment (sandbox or production)"
    )
    SQUARE_WEBHOOK_SIGNATURE_KEY: Optional[str] = Field(
        default=None,
        description="Square webhook signature key"
    )
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID: str = Field(description="Twilio Account SID")
    TWILIO_AUTH_TOKEN: str = Field(description="Twilio Auth Token")
    TWILIO_PHONE_NUMBER: str = Field(description="Twilio phone number")
    TWILIO_WEBHOOK_URL: Optional[str] = Field(
        default=None,
        description="Twilio webhook URL"
    )
    
    # Voice & TTS Configuration
    TTS_PROVIDER: str = Field(
        default="elevenlabs",
        description="TTS provider (elevenlabs, google, openai)"
    )
    ELEVENLABS_API_KEY: Optional[str] = Field(
        default=None,
        description="ElevenLabs API key"
    )
    ELEVENLABS_VOICE_ID: Optional[str] = Field(
        default=None,
        description="ElevenLabs voice ID"
    )
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    
    # Email Configuration
    SMTP_HOST: str = Field(default="smtp.gmail.com", description="SMTP host")
    SMTP_PORT: int = Field(default=587, description="SMTP port")
    SMTP_USERNAME: str = Field(description="SMTP username")
    SMTP_PASSWORD: str = Field(description="SMTP password")
    MANAGER_EMAIL: str = Field(description="Manager email for reports")
    
    # Business Configuration
    SALON_NAME: str = Field(
        default="GetTwisted Hair Studios",
        description="Salon name"
    )
    SALON_PHONE: str = Field(description="Salon phone number")
    SALON_ADDRESS: str = Field(description="Salon address")
    BUSINESS_HOURS_START: str = Field(
        default="09:00",
        description="Business hours start time"
    )
    BUSINESS_HOURS_END: str = Field(
        default="18:00",
        description="Business hours end time"
    )
    TIMEZONE: str = Field(
        default="America/New_York",
        description="Business timezone"
    )
    
    # Call Campaign Settings
    MAX_CALLS_PER_DAY: int = Field(
        default=50,
        description="Maximum calls per day"
    )
    CALL_RETRY_ATTEMPTS: int = Field(
        default=2,
        description="Number of call retry attempts"
    )
    CALL_RETRY_DELAY_HOURS: int = Field(
        default=4,
        description="Hours between call retries"
    )
    RESPECT_DND_HOURS: bool = Field(
        default=True,
        description="Respect do not disturb hours"
    )
    DND_START_HOUR: int = Field(
        default=20,
        description="Do not disturb start hour (24h format)"
    )
    DND_END_HOUR: int = Field(
        default=9,
        description="Do not disturb end hour (24h format)"
    )
    
    # Security Settings
    SECRET_KEY: str = Field(description="Secret key for JWT tokens")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token expiration in minutes"
    )
    ENCRYPTION_KEY: str = Field(description="32-character encryption key")
    
    # Compliance Settings
    TCPA_COMPLIANCE: bool = Field(
        default=True,
        description="Enable TCPA compliance"
    )
    AUTO_OPT_OUT_KEYWORDS: str = Field(
        default="STOP,UNSUBSCRIBE,REMOVE,QUIT",
        description="Comma-separated opt-out keywords"
    )
    DATA_RETENTION_DAYS: int = Field(
        default=365,
        description="Data retention period in days"
    )
    
    # Optional: Web Dashboard
    DASHBOARD_ENABLED: bool = Field(
        default=False,
        description="Enable web dashboard"
    )
    DASHBOARD_USERNAME: str = Field(
        default="admin",
        description="Dashboard username"
    )
    DASHBOARD_PASSWORD: str = Field(
        default="admin",
        description="Dashboard password"
    )
    
    # Development Settings
    MOCK_CALLS: bool = Field(
        default=True,
        description="Mock calls in development"
    )
    MOCK_SMS: bool = Field(
        default=True,
        description="Mock SMS in development"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
