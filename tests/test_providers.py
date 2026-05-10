"""REQ-02/08 - provider factory tests. Implementation lands in Plan 02."""
import pytest


@pytest.mark.skip(reason="W0 stub - implemented in Plan 02 (config + factories)")
def test_factory_raises_on_unknown_stt_impl(dummy_settings):
    from server.providers import get_stt_provider

    dummy_settings.stt_impl = "nonsense"
    with pytest.raises(ValueError, match="Unknown STT_IMPL"):
        get_stt_provider(dummy_settings)


@pytest.mark.skip(reason="W0 stub - implemented in Plan 02")
def test_null_pronunciation_returns_disabled(dummy_settings):
    from server.providers import get_pronunciation_provider

    p = get_pronunciation_provider(dummy_settings)
    result = p.analyze(b"\x00" * 100)
    assert result == {"enabled": False}


@pytest.mark.skip(reason="W0 stub - implemented in Plan 03 (STT impls)")
def test_openai_stt_returns_str(dummy_settings, silence_1s_bytes):
    from server.providers import get_stt_provider

    ...
