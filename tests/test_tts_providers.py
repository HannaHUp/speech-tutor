"""REQ-02 - OpenAI and edge-tts TTS provider tests."""
import pytest


@pytest.mark.skip(reason="W0 stub - implemented in Plan 04 (TTS impls)")
def test_openai_tts_synthesize_returns_bytes(dummy_settings):
    from server.providers.tts_openai import OpenAITTS

    ...


@pytest.mark.skip(reason="W0 stub - implemented in Plan 04")
def test_edge_tts_hardcoded_voice(dummy_settings):
    ...
