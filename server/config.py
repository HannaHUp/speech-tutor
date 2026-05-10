"""Phase 1 config. Six env keys + two API keys per D-14/D-15.

No YAML, no auto-detect - pydantic-settings validates at startup and fails
fast on missing required keys (D-16 Hermes-style explicit config).
"""
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    stt_impl: str = "openai"
    stt_faster_whisper_model: str = "small"
    tts_impl: str = "openai"
    tts_voice: str = "nova"
    llm_model: str = "claude-haiku-4-5-20251001"
    pronunciation_enabled: bool = False
    openai_api_key: SecretStr
    anthropic_api_key: SecretStr
