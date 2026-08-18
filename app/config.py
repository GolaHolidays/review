"""
Centralized configuration — single source of truth for all env vars.
Uses Pydantic Settings to validate and type-check environment variables.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Brand ──
    brand_name: str = "Gola Holidays"
    brand_tagline: str = "Your Gateway to Unforgettable Journeys"

    # ── Google Review ──
    google_review_url: str = "https://g.page/r/YOUR_GOOGLE_REVIEW_LINK/review"

    # ── LLM ──
    llm_provider: str = "gemini"
    gemini_api_key_1: str = ""
    gemini_api_key_2: str = ""
    gemini_api_key_3: str = ""
    llm_model: str = "gemini-3.6-flash"

    @property
    def gemini_api_keys(self) -> list[str]:
        """Return all non-empty, non-placeholder keys in order."""
        return [
            k for k in [
                self.gemini_api_key_1,
                self.gemini_api_key_2,
                self.gemini_api_key_3,
            ]
            if k and not k.startswith("your-")
        ]

    # ── App ──
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = True


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton — loaded once, reused everywhere."""
    return Settings()
