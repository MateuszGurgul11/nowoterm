from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    environment: Literal["development", "test", "production"] = "development"
    database_url: str = "sqlite+aiosqlite:///./novoterm.db"
    session_secret: str = "development-only-change-me"
    export_token: str = ""
    vercel_deploy_hook: str = ""
    supabase_url: str = ""
    supabase_publishable_key: str = ""
    supabase_service_role_key: str = ""
    supabase_media_bucket: str = "media"

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.environment != "production":
            return self

        missing = [
            name
            for name, value in {
                "DATABASE_URL": self.database_url,
                "SESSION_SECRET": self.session_secret,
                "EXPORT_TOKEN": self.export_token,
                "SUPABASE_URL": self.supabase_url,
                "SUPABASE_PUBLISHABLE_KEY": self.supabase_publishable_key,
            }.items()
            if not value
        ]
        if self.database_url.startswith("sqlite"):
            missing.append("DATABASE_URL (PostgreSQL required)")
        if len(self.session_secret) < 32:
            missing.append("SESSION_SECRET (minimum 32 characters)")
        if missing:
            raise ValueError(f"Brak bezpiecznej konfiguracji produkcyjnej: {', '.join(missing)}")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
