"""Provider factories - Hermes-style if/elif dispatch per D-16.

# Adapted from Hermes: tools/transcription_tools.py::_get_provider
# Hermes returns string keys and auto-detects. We return concrete provider
# objects and raise ValueError on unknown (no auto-detect, per D-16).
# Verified deepwiki 2026-05-10.
"""
from server.config import Settings

from .pronunciation_null import NullPronunciationProvider
from .protocols import (
    LLMProvider,
    PronunciationProvider,
    STTProvider,
    TTSProvider,
)


def get_stt_provider(settings: Settings) -> STTProvider:
    # Adapted from Hermes: tools/transcription_tools.py::_get_provider if/elif shape
    if settings.stt_impl == "openai":
        from .stt_openai import OpenAIWhisperSTT

        return OpenAIWhisperSTT(settings)
    elif settings.stt_impl == "faster_whisper":
        from .stt_faster_whisper import FasterWhisperSTT

        return FasterWhisperSTT(settings)
    else:
        raise ValueError(
            f"Unknown STT_IMPL={settings.stt_impl!r}. "
            f"Valid values: openai, faster_whisper"
        )


def get_tts_provider(settings: Settings) -> TTSProvider:
    # Adapted from Hermes: tools/transcription_tools.py::_get_provider
    if settings.tts_impl == "openai":
        from .tts_openai import OpenAITTS

        return OpenAITTS(settings)
    elif settings.tts_impl == "edge":
        from .tts_edge import EdgeTTS

        return EdgeTTS(settings)
    else:
        raise ValueError(
            f"Unknown TTS_IMPL={settings.tts_impl!r}. " f"Valid values: openai, edge"
        )


def get_llm_provider(settings: Settings) -> LLMProvider:
    from .llm_anthropic import AnthropicLLM

    return AnthropicLLM(settings)


def get_pronunciation_provider(settings: Settings) -> PronunciationProvider:
    return NullPronunciationProvider()


__all__ = [
    "get_stt_provider",
    "get_tts_provider",
    "get_llm_provider",
    "get_pronunciation_provider",
    "NullPronunciationProvider",
    "STTProvider",
    "TTSProvider",
    "LLMProvider",
    "PronunciationProvider",
]
