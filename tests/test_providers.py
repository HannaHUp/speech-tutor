"""REQ-02/08 - provider factory tests."""
import pytest


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


@pytest.mark.skip(reason="W0 stub - implemented in Plan 03 (STT impls)")
def test_openai_stt_returns_str(dummy_settings, silence_1s_bytes):
    from server.providers import get_stt_provider

    ...
