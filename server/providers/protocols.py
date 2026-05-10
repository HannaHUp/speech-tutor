"""Provider Protocols - narrow interfaces per D-20.

Plans 03/04/05 implement concrete providers against these Protocols.
Runtime-checkable so isinstance() works for test assertions.
"""
from typing import AsyncIterator, Protocol, runtime_checkable


@runtime_checkable
class STTProvider(Protocol):
    async def transcribe(
        self, audio_bytes: bytes, *, mime: str = "audio/webm"
    ) -> tuple[str, list[dict]]:
        """Transcribe audio to (text, word_timestamps)."""
        ...


@runtime_checkable
class TTSProvider(Protocol):
    async def synthesize_sentence(self, text: str) -> bytes:
        """Synthesize one sentence to mp3 bytes."""
        ...


@runtime_checkable
class LLMProvider(Protocol):
    async def stream(
        self, session_prompt: str, messages: list[dict]
    ) -> AsyncIterator[str]:
        """Yield text deltas from the LLM stream."""
        ...


@runtime_checkable
class PronunciationProvider(Protocol):
    def analyze(self, audio_bytes: bytes) -> dict:
        """Pronunciation analysis. Null impl returns {'enabled': False}."""
        ...
