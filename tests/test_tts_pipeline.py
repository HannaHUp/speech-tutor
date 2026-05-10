"""REQ-02 - TTS sentence-flush pipeline tests.

Hermes borrows from tools/tts_tool.py.
"""
import asyncio
import json
from unittest.mock import AsyncMock

import pytest


def test_sentence_boundary_splits_on_period_space():
    from server.tts_pipeline import _SENTENCE_BOUNDARY_RE

    parts = _SENTENCE_BOUNDARY_RE.split("Hello world. How are you?", maxsplit=1)
    assert parts[0] == "Hello world."
    assert parts[1] == "How are you?"


def test_sentence_boundary_splits_on_double_newline():
    from server.tts_pipeline import _SENTENCE_BOUNDARY_RE

    parts = _SENTENCE_BOUNDARY_RE.split("First paragraph.\n\nSecond one.", maxsplit=1)
    assert "First paragraph." in parts[0]


def test_sentence_boundary_no_split_inside_sentence():
    from server.tts_pipeline import _SENTENCE_BOUNDARY_RE

    parts = _SENTENCE_BOUNDARY_RE.split("Yesterday I went to the park", maxsplit=1)
    assert len(parts) == 1


@pytest.mark.parametrize(
    ("md", "expected_missing", "expected_present"),
    [
        ("Yesterday I *went* to the **park**.", ["*"], ["went", "park"]),
        ("# Heading\nBody", ["#"], ["Heading", "Body"]),
        ("- item one\n- item two", ["- "], ["item one", "item two"]),
        ("Check `this` code", ["`"], ["this"]),
        ("Visit https://example.com now", ["https://"], ["Visit", "now"]),
        ("---\nSeparator", ["---"], ["Separator"]),
        ("```py\nprint('x')\n```after", ["```"], ["after"]),
        ("[click](https://example.com)", ["](", "["], ["click"]),
    ],
)
def test_strip_markdown_all_patterns(md, expected_missing, expected_present):
    from server.tts_pipeline import _strip_markdown_for_tts

    out = _strip_markdown_for_tts(md)
    for token in expected_missing:
        assert token not in out
    for token in expected_present:
        assert token in out


def test_think_block_single_line():
    from server.tts_pipeline import _think_block_re

    out = _think_block_re.sub("", "Before <think>secret</think> after")
    assert "secret" not in out
    assert "Before" in out and "after" in out


def test_think_block_multiline():
    from server.tts_pipeline import _think_block_re

    out = _think_block_re.sub("", "A <think>\nmulti\nline\n</think> B")
    assert "multi" not in out
    assert "A" in out and "B" in out


@pytest.mark.asyncio
async def test_flush_loop_emits_per_sentence():
    from server.tts_pipeline import sentence_flush_loop

    tts = AsyncMock()
    tts.synthesize_sentence = AsyncMock(return_value=b"\x00\x01\x02")
    ws = AsyncMock()
    ws.send_text = AsyncMock()
    ws.send_bytes = AsyncMock()

    q = asyncio.Queue()
    for token in ["Hello world. ", "How are you today? ", "I am fine."]:
        await q.put(token)
    await q.put(None)

    total = await sentence_flush_loop(q, ws, turn_id=1, tts=tts)

    assert total >= 2
    assert tts.synthesize_sentence.call_count >= 2
    assert ws.send_text.call_count == tts.synthesize_sentence.call_count
    assert ws.send_bytes.call_count == tts.synthesize_sentence.call_count


@pytest.mark.asyncio
async def test_flush_loop_strips_markdown_before_tts():
    from server.tts_pipeline import sentence_flush_loop

    tts = AsyncMock()
    tts.synthesize_sentence = AsyncMock(return_value=b"\x00")
    ws = AsyncMock()
    ws.send_text = AsyncMock()
    ws.send_bytes = AsyncMock()

    q = asyncio.Queue()
    await q.put("Yesterday I *went* to the **park**.\n\n")
    await q.put(None)

    await sentence_flush_loop(q, ws, turn_id=1, tts=tts)

    for call in tts.synthesize_sentence.call_args_list:
        assert "*" not in call.args[0]


@pytest.mark.asyncio
async def test_flush_loop_strips_think_blocks_before_tts():
    from server.tts_pipeline import sentence_flush_loop

    tts = AsyncMock()
    tts.synthesize_sentence = AsyncMock(return_value=b"\x00")
    ws = AsyncMock()
    ws.send_text = AsyncMock()
    ws.send_bytes = AsyncMock()

    q = asyncio.Queue()
    await q.put("Before <think>hidden</think> real text here.")
    await q.put(None)

    await sentence_flush_loop(q, ws, turn_id=1, tts=tts)

    for call in tts.synthesize_sentence.call_args_list:
        assert "hidden" not in call.args[0]


@pytest.mark.asyncio
async def test_send_tts_chunk_sends_json_before_binary():
    from server.tts_pipeline import send_tts_chunk

    ws = AsyncMock()
    calls = []

    async def mock_send_text(data):
        calls.append(("text", data))

    async def mock_send_bytes(data):
        calls.append(("bytes", data))

    ws.send_text = mock_send_text
    ws.send_bytes = mock_send_bytes

    await send_tts_chunk(ws, turn_id=1, seq=0, sentence_idx=0, mp3_bytes=b"ABC")

    assert calls[0][0] == "text"
    assert calls[1][0] == "bytes"
    meta = json.loads(calls[0][1])
    assert meta["type"] == "tts.chunk"
    assert meta["bytes"] == 3
    assert meta["turn_id"] == 1
