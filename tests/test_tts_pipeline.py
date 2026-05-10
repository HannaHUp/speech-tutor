"""REQ-02 - TTS sentence-flush pipeline tests.

Hermes borrows: tools/tts_tool.py::_SENTENCE_BOUNDARY_RE,
_strip_markdown_for_tts, _think_block_re. Implementation lands in Plan 04.
"""
import pytest


@pytest.mark.skip(reason="W0 stub - implemented in Plan 04 (TTS pipeline)")
def test_sentence_boundary_splits_on_period_space():
    from server.tts_pipeline import _SENTENCE_BOUNDARY_RE

    parts = _SENTENCE_BOUNDARY_RE.split("Hello world. How are you?", maxsplit=1)
    assert parts[0] == "Hello world."


@pytest.mark.skip(reason="W0 stub - implemented in Plan 04")
def test_strip_markdown_removes_bold_and_italic():
    from server.tts_pipeline import _strip_markdown_for_tts

    assert "went" in _strip_markdown_for_tts("Yesterday I *went* to the **park**.")
    assert "*" not in _strip_markdown_for_tts("Yesterday I *went* to the **park**.")


@pytest.mark.skip(reason="W0 stub - implemented in Plan 04")
def test_think_block_stripped():
    from server.tts_pipeline import _think_block_re

    cleaned = _think_block_re.sub("", "Before <think>secret</think> after")
    assert "secret" not in cleaned
    assert "Before" in cleaned and "after" in cleaned
