"""Bot configuration using pydantic-settings."""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Bot configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Discord settings
    discord_token: str = Field(description="Discord bot token")
    discord_owner_ids: list[int] = Field(
        default_factory=list,
        description="List of Discord user IDs that are bot owners",
    )
    discord_prefix: str = Field(
        default="!",
        description="Command prefix for text commands",
    )

    # External API keys
    gemini_api_key: str | None = Field(
        default=None,
        description="Google Gemini API key",
    )
    w2g_api_key: str | None = Field(
        default=None,
        description="Watch2Gether API key (optional, increases rate limits)",
    )

    # Environment
    environment: Literal["development", "production"] = Field(
        default="development",
        description="Current environment",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )

    # Database
    database_path: Path = Field(
        default=Path("data/bot.db"),
        description="Path to SQLite database file",
    )

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"


_settings: Settings | None = None


def get_settings() -> Settings:
    """Get the settings instance (lazy initialization).

    Returns:
        Settings instance.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
