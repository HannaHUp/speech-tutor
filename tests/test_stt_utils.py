"""REQ-02 - Whisper hallucination filter tests.

Hermes borrow: tools/voice_mode.py::WHISPER_HALLUCINATIONS.
"""
import pytest


@pytest.mark.parametrize(
    "phrase",
    [
        "thank you for watching",
        "Thank you for watching.",
        "THANKS FOR WATCHING",
        "subscribe to my channel",
        "you",
        "bye",
        "amara.org",
        "ご視聴ありがとうございました",
    ],
)
def test_hallucination_filter_blocks_known_phrases(phrase):
    from server.providers.stt_utils import is_whisper_hallucination

    assert is_whisper_hallucination(phrase) is True


@pytest.mark.parametrize(
    "phrase",
    [
        "yesterday I went to the park",
        "Hello, what should we talk about today?",
        "I am learning English with you",
        "Thank you so much for your help today",
    ],
)
def test_hallucination_filter_passes_real_utterances(phrase):
    from server.providers.stt_utils import is_whisper_hallucination

    assert is_whisper_hallucination(phrase) is False


def test_hallucination_repeat_regex_blocks_repeated_you():
    from server.providers.stt_utils import _HALLUCINATION_REPEAT_RE

    assert _HALLUCINATION_REPEAT_RE.match("you you you you") is not None


@pytest.mark.parametrize("phrase", ["ok ok ok", "bye bye bye", ". . .", "!!!"])
def test_repeat_regex_blocks_filler(phrase):
    from server.providers.stt_utils import _HALLUCINATION_REPEAT_RE

    assert _HALLUCINATION_REPEAT_RE.match(phrase) is not None


def test_empty_is_hallucination():
    from server.providers.stt_utils import is_whisper_hallucination

    assert is_whisper_hallucination("") is True
    assert is_whisper_hallucination("   ") is True


def test_deny_list_has_expected_size():
    from server.providers.stt_utils import WHISPER_HALLUCINATIONS

    assert len(WHISPER_HALLUCINATIONS) >= 20
