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


@pytest.mark.asyncio
async def test_faster_whisper_stt_returns_tuple(
    dummy_settings, silence_1s_bytes, monkeypatch
):
    import server.providers.stt_faster_whisper as mod

    fake_segment = MagicMock(
        text="Hello world",
        words=[MagicMock(word="Hello", start=0.0, end=0.5)],
    )
    fake_model = MagicMock()
    fake_model.transcribe = MagicMock(return_value=([fake_segment], MagicMock()))
    monkeypatch.setattr(mod, "WhisperModel", lambda *args, **kwargs: fake_model)

    stt = mod.FasterWhisperSTT(dummy_settings)
    text, words = await stt.transcribe(silence_1s_bytes)

    assert "Hello world" in text
    assert words == [{"word": "Hello", "start": 0.0, "end": 0.5}]


@pytest.mark.asyncio
async def test_faster_whisper_passes_condition_on_previous_text_false(
    dummy_settings, silence_1s_bytes, monkeypatch
):
    import server.providers.stt_faster_whisper as mod

    fake_model = MagicMock()
    fake_model.transcribe = MagicMock(return_value=(iter([]), MagicMock()))
    monkeypatch.setattr(mod, "WhisperModel", lambda *args, **kwargs: fake_model)

    stt = mod.FasterWhisperSTT(dummy_settings)
    await stt.transcribe(silence_1s_bytes)

    kwargs = fake_model.transcribe.call_args.kwargs
    assert kwargs["condition_on_previous_text"] is False
    assert kwargs["word_timestamps"] is True


def test_faster_whisper_stt_satisfies_protocol(dummy_settings, monkeypatch):
    import server.providers.stt_faster_whisper as mod
    from server.providers.protocols import STTProvider

    monkeypatch.setattr(mod, "WhisperModel", lambda *args, **kwargs: MagicMock())

    assert isinstance(mod.FasterWhisperSTT(dummy_settings), STTProvider)
