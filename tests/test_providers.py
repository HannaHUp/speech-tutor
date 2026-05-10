"""REQ-02/08 - provider factory tests."""
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import SecretStr


def test_factory_raises_on_unknown_stt_impl(dummy_settings):
    from server.providers import get_stt_provider

    dummy_settings.stt_impl = "nonsense"
    with pytest.raises(ValueError, match="Unknown STT_IMPL"):
        get_stt_provider(dummy_settings)


def test_factory_raises_on_unknown_tts_impl(dummy_settings):
    from server.providers import get_tts_provider

    dummy_settings.tts_impl = "nonsense"
    with pytest.raises(ValueError, match="Unknown TTS_IMPL"):
        get_tts_provider(dummy_settings)


def test_null_pronunciation_returns_disabled(dummy_settings):
    from server.providers import NullPronunciationProvider, get_pronunciation_provider
    from server.providers.protocols import PronunciationProvider

    p = get_pronunciation_provider(dummy_settings)
    assert isinstance(p, NullPronunciationProvider)
    assert isinstance(p, PronunciationProvider)
    assert p.analyze(b"\x00" * 100) == {"enabled": False}


def test_null_pronunciation_returns_disabled_on_empty_bytes():
    from server.providers import NullPronunciationProvider

    p = NullPronunciationProvider()
    assert p.analyze(b"") == {"enabled": False}


@pytest.mark.asyncio
async def test_openai_stt_returns_tuple(dummy_settings, silence_1s_bytes):
    from server.providers.stt_openai import OpenAIWhisperSTT

    dummy_settings.openai_api_key = SecretStr("sk-test")
    stt = OpenAIWhisperSTT(dummy_settings)
    fake_resp = MagicMock()
    fake_resp.text = "Hello world"
    fake_resp.words = [MagicMock(word="Hello", start=0.0, end=0.5)]
    stt._client.audio.transcriptions.create = AsyncMock(return_value=fake_resp)

    text, words = await stt.transcribe(silence_1s_bytes)

    assert text == "Hello world"
    assert words == [{"word": "Hello", "start": 0.0, "end": 0.5}]
    kwargs = stt._client.audio.transcriptions.create.call_args.kwargs
    assert kwargs["model"] == "whisper-1"
    assert kwargs["response_format"] == "verbose_json"
    assert kwargs["timestamp_granularities"] == ["word"]


@pytest.mark.asyncio
async def test_openai_stt_filters_hallucination(dummy_settings, silence_1s_bytes):
    from server.providers.stt_openai import OpenAIWhisperSTT

    dummy_settings.openai_api_key = SecretStr("sk-test")
    stt = OpenAIWhisperSTT(dummy_settings)
    fake_resp = MagicMock(text="thank you for watching", words=[])
    stt._client.audio.transcriptions.create = AsyncMock(return_value=fake_resp)

    text, words = await stt.transcribe(silence_1s_bytes)

    assert text == ""
    assert words == []


def test_openai_stt_satisfies_protocol(dummy_settings):
    from server.providers.protocols import STTProvider
    from server.providers.stt_openai import OpenAIWhisperSTT

    dummy_settings.openai_api_key = SecretStr("sk-test")
    assert isinstance(OpenAIWhisperSTT(dummy_settings), STTProvider)
