"""REQ-02 - OpenAI and edge-tts TTS provider tests."""
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.mark.asyncio
async def test_openai_tts_synthesize_returns_bytes(dummy_settings):
    from server.providers.tts_openai import OpenAITTS

    tts = OpenAITTS(dummy_settings)
    fake_resp = MagicMock(content=b"\xff\xfb\x00MP3DATA")
    tts._client.audio.speech.create = AsyncMock(return_value=fake_resp)

    out = await tts.synthesize_sentence("Hello world")

    assert out == b"\xff\xfb\x00MP3DATA"
    kwargs = tts._client.audio.speech.create.call_args.kwargs
    assert kwargs["model"] == "tts-1"
    assert kwargs["voice"] == "nova"
    assert kwargs["input"] == "Hello world"
    assert kwargs["response_format"] == "mp3"


def test_openai_tts_satisfies_protocol(dummy_settings):
    from server.providers.protocols import TTSProvider
    from server.providers.tts_openai import OpenAITTS

    assert isinstance(OpenAITTS(dummy_settings), TTSProvider)


def test_edge_tts_hardcoded_voice(dummy_settings):
    from server.providers.tts_edge import EdgeTTS

    dummy_settings.tts_voice = "nova"
    tts = EdgeTTS(dummy_settings)

    assert tts._voice == "en-US-JennyNeural"


@pytest.mark.asyncio
async def test_edge_tts_synthesize_returns_bytes(dummy_settings, monkeypatch):
    import server.providers.tts_edge as mod

    async def fake_stream():
        yield {"type": "audio", "data": b"AUDIO1"}
        yield {"type": "WordBoundary", "offset": 0, "duration": 1}
        yield {"type": "audio", "data": b"AUDIO2"}

    instance = MagicMock()
    instance.stream = fake_stream
    fake_communicate_cls = MagicMock(return_value=instance)
    monkeypatch.setattr(mod.edge_tts, "Communicate", fake_communicate_cls)

    tts = mod.EdgeTTS(dummy_settings)
    out = await tts.synthesize_sentence("Hello")

    assert out == b"AUDIO1AUDIO2"
    fake_communicate_cls.assert_called_once_with("Hello", "en-US-JennyNeural")


def test_edge_tts_satisfies_protocol(dummy_settings):
    from server.providers.protocols import TTSProvider
    from server.providers.tts_edge import EdgeTTS

    assert isinstance(EdgeTTS(dummy_settings), TTSProvider)
