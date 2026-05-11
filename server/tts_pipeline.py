"""TTS pipeline - Hermes regex borrows plus async sentence-flush loop.

Borrowed from Hermes: tools/tts_tool.py::_SENTENCE_BOUNDARY_RE
Borrowed from Hermes: tools/tts_tool.py::_strip_markdown_for_tts
Borrowed from Hermes: tools/tts_tool.py::_think_block_re
Borrowed from Hermes: tools/tts_tool.py::stream_tts_to_speaker sentence-flush shape
Adapted from Hermes: tools/tts_tool.py::stream_tts_to_speaker
  - asyncio.Queue replaces queue.Queue; WebSocket send_bytes replaces sounddevice.
Verified deepwiki 2026-05-10.
"""
import asyncio
import json
import re
from typing import Any, Protocol


# Hermes borrow: tools/tts_tool.py::_SENTENCE_BOUNDARY_RE (verbatim)
_SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?])(?:\s|\n)|(?:\n\n)")


# Hermes borrow: tools/tts_tool.py::_strip_markdown_for_tts (verbatim, 10 consts)
_MD_CODE_BLOCK = re.compile(r"```[\s\S]*?```")
_MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_MD_URL = re.compile(r"https?://\S+")
_MD_BOLD = re.compile(r"\*\*(.+?)\*\*")
_MD_ITALIC = re.compile(r"\*(.+?)\*")
_MD_INLINE_CODE = re.compile(r"`(.+?)`")
_MD_HEADER = re.compile(r"^#+\s*", flags=re.MULTILINE)
_MD_LIST_ITEM = re.compile(r"^\s*[-*]\s+", flags=re.MULTILINE)
_MD_HR = re.compile(r"---+")
_MD_EXCESS_NL = re.compile(r"\n{3,}")


def _strip_markdown_for_tts(text: str) -> str:
    """Remove markdown formatting that should not be spoken aloud."""
    text = _MD_CODE_BLOCK.sub(" ", text)
    text = _MD_LINK.sub(r"\1", text)
    text = _MD_URL.sub("", text)
    text = _MD_BOLD.sub(r"\1", text)
    text = _MD_ITALIC.sub(r"\1", text)
    text = _MD_INLINE_CODE.sub(r"\1", text)
    text = _MD_HEADER.sub("", text)
    text = _MD_LIST_ITEM.sub("", text)
    text = _MD_HR.sub("", text)
    text = _MD_EXCESS_NL.sub("\n\n", text)
    return text.strip()


# Hermes borrow: tools/tts_tool.py::_think_block_re (verbatim)
_think_block_re = re.compile(r"<think[\s>].*?</think>", flags=re.DOTALL)


MIN_SENTENCE_LEN = 20
LONG_FLUSH_LEN = 100


class _TTSLike(Protocol):
    async def synthesize_sentence(self, text: str) -> bytes:
        ...


class _WSLike(Protocol):
    async def send_text(self, data: str) -> None:
        ...

    async def send_bytes(self, data: bytes) -> None:
        ...


async def send_tts_chunk(
    ws: _WSLike,
    *,
    turn_id: int,
    seq: int,
    sentence_idx: int,
    mp3_bytes: bytes,
    turn_debug_logger: Any | None = None,
) -> None:
    """Send JSON metadata followed by the paired binary MP3 frame."""
    meta = {
        "type": "tts.chunk",
        "turn_id": turn_id,
        "seq": seq,
        "sentence_idx": sentence_idx,
        "mime": "audio/mpeg",
        "bytes": len(mp3_bytes),
    }
    if turn_debug_logger is not None:
        turn_debug_logger.log(
            event="tts_chunk_meta",
            turn_id=turn_id,
            extra={
                "seq": seq,
                "sentence_idx": sentence_idx,
                "mime": meta["mime"],
                "bytes": meta["bytes"],
                "tts_chunk_count": seq + 1,
            },
        )
    await ws.send_text(json.dumps(meta))
    await ws.send_bytes(mp3_bytes)


async def _flush_sentence(
    sentence: str,
    ws: _WSLike,
    *,
    turn_id: int,
    seq: int,
    sentence_idx: int,
    tts: _TTSLike,
    turn_debug_logger: Any | None = None,
) -> bool:
    cleaned = _strip_markdown_for_tts(sentence)
    if not cleaned:
        return False
    mp3 = await tts.synthesize_sentence(cleaned)
    await send_tts_chunk(
        ws,
        turn_id=turn_id,
        seq=seq,
        sentence_idx=sentence_idx,
        mp3_bytes=mp3,
        turn_debug_logger=turn_debug_logger,
    )
    return True


async def sentence_flush_loop(
    text_queue: asyncio.Queue,
    ws: _WSLike,
    *,
    turn_id: int,
    tts: _TTSLike,
    turn_debug_logger: Any | None = None,
) -> int:
    """Drain text deltas and emit per-sentence TTS JSON+binary frame pairs.

    Sentinel: put None on the queue to mark the end of the LLM text stream.
    """
    buf = ""
    seq = 0
    sentence_idx = 0
    pending_fragment = ""

    try:
        while True:
            delta = await text_queue.get()
            if delta is None:
                final_text = f"{pending_fragment} {buf}".strip()
                if final_text:
                    flushed = await _flush_sentence(
                        final_text,
                        ws,
                        turn_id=turn_id,
                        seq=seq,
                        sentence_idx=sentence_idx,
                        tts=tts,
                        turn_debug_logger=turn_debug_logger,
                    )
                    if flushed:
                        sentence_idx += 1
                break

            buf += delta
            buf = _think_block_re.sub("", buf)

            while True:
                parts = _SENTENCE_BOUNDARY_RE.split(buf, maxsplit=1)
                if len(parts) < 2:
                    break

                sentence = f"{pending_fragment} {parts[0]}".strip()
                pending_fragment = ""
                buf = parts[1]
                if len(sentence) < MIN_SENTENCE_LEN:
                    pending_fragment = sentence
                    continue

                flushed = await _flush_sentence(
                    sentence,
                    ws,
                    turn_id=turn_id,
                    seq=seq,
                    sentence_idx=sentence_idx,
                    tts=tts,
                    turn_debug_logger=turn_debug_logger,
                )
                if flushed:
                    seq += 1
                    sentence_idx += 1
    except asyncio.CancelledError:
        raise

    return sentence_idx
