"""Phase 1 config. Six env keys + two API keys per D-14/D-15.

No YAML, no auto-detect - pydantic-settings validates at startup and fails
fast on missing required keys (D-16 Hermes-style explicit config).
"""
from pathlib import Path

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE), env_file_encoding="utf-8", case_sensitive=False
    )

    stt_impl: str = "openai"
    stt_faster_whisper_model: str = "small"
    tts_impl: str = "openai"
    tts_voice: str = "nova"
    llm_impl: str = "openai"
    llm_model: str = "gpt-4o-mini"
    pronunciation_enabled: bool = False
    ffmpeg_path: str | None = None
    openai_api_key: SecretStr
    anthropic_api_key: SecretStr | None = None

    @model_validator(mode="after")
    def validate_selected_llm_provider(self) -> "Settings":
        if self.llm_impl == "anthropic" and self.anthropic_api_key is None:
            raise ValueError(
                "ANTHROPIC_API_KEY is required when LLM_IMPL=anthropic."
            )
        if self.llm_impl not in {"openai", "anthropic"}:
            raise ValueError(
                f"Unknown LLM_IMPL={self.llm_impl!r}. Valid values: openai, anthropic"
            )
        return self
