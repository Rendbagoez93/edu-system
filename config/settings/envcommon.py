from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CommonEnvSettings(BaseSettings):
    """Common environment settings for all deployment environments."""

    # Security
    SECRET_KEY: str = Field(
        default="django-insecure-change-this-in-production",
        description="Django secret key for cryptographic signing",
    )

    # Debug and Environment
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    ENVIRONMENT: str = Field(default="local", description="Current environment (local, dev, staging, prod)")

    # Allowed Hosts
    ALLOWED_HOSTS: list[str] = Field(
        default=["localhost", "127.0.0.1"],
        description="List of allowed host/domain names",
    )

    # CORS (for mobile apps)
    CORS_ALLOWED_ORIGINS: list[str] = Field(
        default=["http://localhost:8000", "http://127.0.0.1:8000", "http://10.0.2.2:8000"],
        description="List of allowed CORS origins for mobile apps",
    )

    # Internationalization
    LANGUAGE_CODE: str = Field(default="en-us", description="Language code for the application")
    TIME_ZONE: str = Field(default="Asia/Jakarta", description="Time zone for the application")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # -------------------------------------------------------------------------
    # Convenience accessors used by local.py and production.py
    # -------------------------------------------------------------------------

    @property
    def is_local(self) -> bool:
        return self.ENVIRONMENT == "local"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "prod"

    @property
    def secret_key(self) -> str:
        """Alias for SECRET_KEY."""
        return self.SECRET_KEY

    @property
    def allowed_hosts(self) -> list[str]:
        """Alias for ALLOWED_HOSTS."""
        return self.ALLOWED_HOSTS

    @property
    def base_dir(self) -> Path:
        """Project root — two levels up from this settings directory."""
        return Path(__file__).resolve().parent.parent.parent

    @property
    def app_name(self) -> str:
        return "School Management System"

    @property
    def app_timezone(self) -> str:
        """Alias for TIME_ZONE."""
        return self.TIME_ZONE


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

env_common = CommonEnvSettings()
