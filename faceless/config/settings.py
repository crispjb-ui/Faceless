from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration, loaded from environment / .env.

    Secrets are optional at import time so the package can be inspected and the
    offline (`--dry-run`) paths can run without any credentials. Each module that
    needs a key validates its presence when it actually makes a call.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Core
    niche: str = Field(default="self_improvement", alias="FACELESS_NICHE")
    database_url: str = Field(default="sqlite:///data/faceless.sqlite", alias="DATABASE_URL")
    output_dir: str = Field(default="output", alias="OUTPUT_DIR")
    # Render backend: "ffmpeg" (slideshow, no extra deps) or "remotion" (branded).
    render_backend: str = Field(default="ffmpeg", alias="RENDER_BACKEND")
    # Root folder of pre-licensed music; subfolders are selected per niche.
    music_library_dir: str = Field(default="music", alias="MUSIC_LIBRARY_DIR")

    # LLM
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-sonnet-4-6", alias="ANTHROPIC_MODEL")
    anthropic_model_heavy: str = Field(default="claude-opus-4-7", alias="ANTHROPIC_MODEL_HEAVY")

    # YouTube
    youtube_api_key: str | None = Field(default=None, alias="YOUTUBE_API_KEY")
    youtube_client_secret_file: str = Field(
        default="client_secret.json", alias="YOUTUBE_CLIENT_SECRET_FILE"
    )
    youtube_token_file: str = Field(default="youtube_token.json", alias="YOUTUBE_TOKEN_FILE")

    # TTS
    elevenlabs_api_key: str | None = Field(default=None, alias="ELEVENLABS_API_KEY")
    elevenlabs_voice_id: str | None = Field(default=None, alias="ELEVENLABS_VOICE_ID")

    # Visuals / music / distribution
    image_api_key: str | None = Field(default=None, alias="IMAGE_API_KEY")
    video_api_key: str | None = Field(default=None, alias="VIDEO_API_KEY")
    music_api_key: str | None = Field(default=None, alias="MUSIC_API_KEY")
    distribution_api_key: str | None = Field(default=None, alias="DISTRIBUTION_API_KEY")

    def require(self, attr: str) -> str:
        """Return a required secret or raise a clear, actionable error."""
        value = getattr(self, attr, None)
        if not value:
            env_name = self.model_fields[attr].alias or attr.upper()
            raise RuntimeError(
                f"Missing required setting '{attr}'. Set {env_name} in your .env "
                f"(see .env.example)."
            )
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
