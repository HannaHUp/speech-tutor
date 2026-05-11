"""WebSocket /ws endpoint for the Phase 1 turn state machine.

See Plan 04 (server/tts_pipeline.py) for sentence-flush Hermes borrow.
See Plan 03 (server/providers/stt_utils.py) for Whisper-filter Hermes borrow.
See Plan 05 (server/session.py + llm_anthropic.py) for prompt-cache borrow.
"""
import asyncio
import json
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from server.latency_log import log_stage_latency, log_stt_divergence
from server.prosody import extract_prosody
from server.session import Session
from server.tts_pipeline import sentence_flush_loop
from server.turn_debug_log import TurnDebugLogger


def _elapsed_ms(start: float) -> int:
    return int((time.monotonic() - start) * 1000)


async def _drain_outbound(ws: WebSocket, queue: asyncio.Queue) -> None:
    """Serialize all websocket writes through one coroutine."""
    while True:
        item = await queue.get()
        if item is None:
            return
        kind, payload = item
        try:
            if kind == "text":
                await ws.send_text(payload)
            elif kind == "bytes":
                await ws.send_bytes(payload)
        except (RuntimeError, WebSocketDisconnect):
            return


class _OutboundWS:
    def __init__(self, queue: asyncio.Queue) -> None:
        self._queue = queue

    async def send_text(self, data: str) -> None:
        await self._queue.put(("text", data))

    async def send_bytes(self, data: bytes) -> None:
        await self._queue.put(("bytes", data))


async def _send_json(out_ws: _OutboundWS, payload: dict[str, Any]) -> None:
    await out_ws.send_text(json.dumps(payload))


async def _run_transcription(
    *,
    turn_id: int,
    audio: bytes,
    out_ws: _OutboundWS,
    executor: ThreadPoolExecutor,
    stt_provider: Any,
    turn_debug_logger: TurnDebugLogger,
) -> tuple[str, list[dict], dict]:
    await _send_json(out_ws, {"type": "stt.running", "turn_id": turn_id})

    stt_start = time.monotonic()
    stt_task = asyncio.create_task(stt_provider.transcribe(audio, mime="audio/webm"))
    text, word_timestamps = await stt_task
    log_stage_latency(turn_id=turn_id, stage="stt", ms=_elapsed_ms(stt_start))
    turn_debug_logger.log(
        event="transcript_ready",
        turn_id=turn_id,
        extra={"stt_text": text},
    )

    prosody_start = time.monotonic()
    loop = asyncio.get_running_loop()
    try:
        prosody = await asyncio.wait_for(
            loop.run_in_executor(
                executor,
                lambda: extract_prosody(audio, word_timestamps=word_timestamps),
            ),
            timeout=0.5,
        )
    except Exception:
        prosody = {}
    log_stage_latency(turn_id=turn_id, stage="prosody", ms=_elapsed_ms(prosody_start))
    turn_debug_logger.log(
        event="prosody_extracted",
        turn_id=turn_id,
        extra={"stt_text": text, "prosody": prosody},
    )

    await _send_json(
        out_ws, {"type": "transcript.ready", "turn_id": turn_id, "stt_text": text}
    )
    return text, word_timestamps, prosody


async def _run_turn(
    *,
    turn_id: int,
    text: str,
    stt_text: str | None,
    prosody: dict,
    session: Session,
    out_ws: _OutboundWS,
    llm_provider: Any,
    tts_provider: Any,
    turn_debug_logger: TurnDebugLogger,
) -> None:
    if stt_text is not None:
        log_stt_divergence(turn_id=turn_id, stt_text=stt_text, text=text)

    try:
        session.append_user(text, prosody)
        llm_messages = session.messages
        llm_user_message = llm_messages[-1]["content"] if llm_messages else ""
        turn_debug_logger.log(
            event="llm_input",
            turn_id=turn_id,
            extra={
                "stt_text": stt_text,
                "edited_text": text,
                "prosody": prosody,
                "llm_system_prompt": session.system_prompt,
                "llm_user_message": llm_user_message,
                "llm_messages": llm_messages,
            },
        )

        text_queue: asyncio.Queue = asyncio.Queue()
        assistant_parts: list[str] = []

        async def stream_llm() -> None:
            first_delta_at: float | None = None
            llm_start = time.monotonic()
            async for delta in llm_provider.stream(session.system_prompt, llm_messages):
                if first_delta_at is None:
                    first_delta_at = time.monotonic()
                    log_stage_latency(
                        turn_id=turn_id,
                        stage="llm_ttft",
                        ms=int((first_delta_at - llm_start) * 1000),
                    )
                assistant_parts.append(delta)
                turn_debug_logger.log(
                    event="llm_delta",
                    turn_id=turn_id,
                    extra={"delta": delta},
                )
                await _send_json(
                    out_ws, {"type": "llm.delta", "turn_id": turn_id, "text": delta}
                )
                await text_queue.put(delta)
            await text_queue.put(None)

        first_sentence_start = time.monotonic()
        llm_task = asyncio.create_task(stream_llm())
        chunks = await sentence_flush_loop(
            text_queue,
            out_ws,
            turn_id=turn_id,
            tts=tts_provider,
            turn_debug_logger=turn_debug_logger,
        )
        await llm_task
        log_stage_latency(
            turn_id=turn_id,
            stage="llm_first_sentence",
            ms=_elapsed_ms(first_sentence_start),
        )
        if chunks:
            log_stage_latency(turn_id=turn_id, stage="tts_first_chunk", ms=0)
        assistant_text = "".join(assistant_parts)
        turn_debug_logger.log(
            event="llm_complete",
            turn_id=turn_id,
            extra={"assistant_text": assistant_text},
        )
        session.append_assistant(assistant_text)
        await _send_json(
            out_ws, {"type": "tts.done", "turn_id": turn_id, "total_chunks": chunks}
        )
        turn_debug_logger.log(
            event="turn_done",
            turn_id=turn_id,
            extra={"assistant_text": assistant_text, "tts_chunk_count": chunks},
        )
        await _send_json(out_ws, {"type": "turn.done", "turn_id": turn_id})
    except Exception as exc:
        turn_debug_logger.log(
            event="turn_failed",
            turn_id=turn_id,
            extra={"error": f"{exc.__class__.__name__}: {exc}"},
        )
        raise


async def websocket_endpoint(ws: WebSocket) -> None:
    await ws.accept()

    app_state = ws.app.state
    settings = app_state.settings
    session = Session(llm_model=settings.llm_model, settings=settings)
    executor = app_state.executor
    out_queue: asyncio.Queue = asyncio.Queue()
    out_ws = _OutboundWS(out_queue)
    drain_task = asyncio.create_task(_drain_outbound(ws, out_queue))

    next_turn_id = 1
    current_turn_id: int | None = None
    audio_chunks: list[bytes] = []
    last_stt_text: str | None = None
    last_prosody: dict = {}
    current_task: asyncio.Task | None = None
    turn_debug_logger: TurnDebugLogger = getattr(
        app_state,
        "turn_debug_logger",
        TurnDebugLogger(enabled=False, path=None, include_system_prompt=False),
    )

    try:
        while True:
            message = await ws.receive()
            if "bytes" in message and message["bytes"] is not None:
                audio_chunks.append(message["bytes"])
                continue
            if "text" not in message or message["text"] is None:
                continue

            event = json.loads(message["text"])
            event_type = event.get("type")

            if event_type == "turn.start":
                current_turn_id = next_turn_id
                next_turn_id += 1
                audio_chunks = []
                last_stt_text = None
                last_prosody = {}
                turn_debug_logger.log(event="turn_started", turn_id=current_turn_id)
                await _send_json(
                    out_ws, {"type": "turn.started", "turn_id": current_turn_id}
                )

            elif event_type == "audio.frame":
                continue

            elif event_type == "turn.stop" and current_turn_id is not None:
                audio = b"".join(audio_chunks)
                last_stt_text, _word_timestamps, last_prosody = await _run_transcription(
                    turn_id=current_turn_id,
                    audio=audio,
                    out_ws=out_ws,
                    executor=executor,
                    stt_provider=app_state.stt_provider,
                    turn_debug_logger=turn_debug_logger,
                )

            elif event_type == "turn.send":
                turn_id = int(event["turn_id"])
                text = event["text"]
                stt_text = event.get("stt_text", last_stt_text)
                prosody = last_prosody if stt_text is not None else {}
                current_task = asyncio.create_task(
                    _run_turn(
                        turn_id=turn_id,
                        text=text,
                        stt_text=stt_text,
                        prosody=prosody,
                        session=session,
                        out_ws=out_ws,
                        llm_provider=app_state.llm_provider,
                        tts_provider=app_state.tts_provider,
                        turn_debug_logger=turn_debug_logger,
                    )
                )

            elif event_type == "turn.cancel":
                turn_id = int(event.get("turn_id") or current_turn_id or 0)
                if current_task and not current_task.done():
                    current_task.cancel()
                    try:
                        await current_task
                    except asyncio.CancelledError:
                        pass
                await _send_json(
                    out_ws,
                    {"type": "turn.canceled", "turn_id": turn_id, "at_stage": "llm"},
                )

            if current_task and current_task.done():
                exc = current_task.exception()
                if exc:
                    turn_id = current_turn_id or 0
                    await _send_json(
                        out_ws,
                        {
                            "type": "error",
                            "turn_id": turn_id,
                            "stage": "llm",
                            "code": exc.__class__.__name__,
                            "message": str(exc),
                            "retriable": False,
                        },
                    )
                    await _send_json(
                        out_ws,
                        {"type": "turn.failed", "turn_id": turn_id, "stage": "llm"},
                    )
    except (WebSocketDisconnect, RuntimeError):
        pass
    finally:
        if current_task and not current_task.done():
            current_task.cancel()
        await out_queue.put(None)
        await drain_task
