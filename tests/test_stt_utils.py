"""REQ-02 - Whisper hallucination filter tests.

Hermes borrow: tools/voice_mode.py::WHISPER_HALLUCINATIONS.
Implementation lands in Plan 03.
"""
import pytest


@pytest.mark.skip(reason="W0 stub - implemented in Plan 03 (STT wrapper)")
def test_hallucination_filter_blocks_thank_you_for_watching():
    from server.providers.stt_utils import is_whisper_hallucination

    assert is_whisper_hallucination("thank you for watching") is True


@pytest.mark.skip(reason="W0 stub - implemented in Plan 03")
def test_hallucination_filter_passes_real_utterance():
    from server.providers.stt_utils import is_whisper_hallucination

    assert is_whisper_hallucination("yesterday I went to the park") is False


@pytest.mark.skip(reason="W0 stub - implemented in Plan 03")
def test_hallucination_repeat_regex_blocks_repeated_you():
    from server.providers.stt_utils import _HALLUCINATION_REPEAT_RE

    assert _HALLUCINATION_REPEAT_RE.match("you you you you") is not None
