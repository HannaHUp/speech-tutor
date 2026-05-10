"""Edge TTS provider via edge-tts.

RESEARCH Pitfall 4: edge-tts voice names are locale-specific. Phase 1
hardcodes en-US-JennyNeural and ignores the OpenAI voice setting.
"""
import edge_tts

from server.config import Settings


_EDGE_VOICE_PHASE_1 = "en-US-JennyNeural"


class EdgeTTS:
    """TTSProvider implementation using edge-tts 7.x async streaming."""

    def __init__(self, settings: Settings) -> None:
        _ = settings
        self._voice = _EDGE_VOICE_PHASE_1

    async def synthesize_sentence(self, text: str) -> bytes:
        communicate = edge_tts.Communicate(text, self._voice)
        chunks: list[bytes] = []
        async for chunk in communicate.stream():
            if chunk.get("type") == "audio":
                chunks.append(chunk["data"])
        return b"".join(chunks)
