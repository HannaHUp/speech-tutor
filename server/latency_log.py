"""Per-stage stdout JSON logs for Phase 1 latency measurements."""
import json
import os
import time


def log_stage_latency(*, turn_id: int, stage: str, ms: int) -> None:
    """Emit one stage latency line to stdout."""
    print(
        json.dumps(
            {
                "event": "stage_latency",
                "turn_id": turn_id,
                "stage": stage,
                "ms": ms,
                "ts": time.time(),
            }
        ),
        flush=True,
    )


def log_stt_divergence(*, turn_id: int, stt_text: str, text: str) -> None:
    """Log raw STT versus edited text divergence with text hidden by default."""
    line = {
        "event": "stt_divergence",
        "turn_id": turn_id,
        "edited": stt_text != text,
        "stt_len": len(stt_text),
        "text_len": len(text),
        "ts": time.time(),
    }
    if os.environ.get("LOG_STT_DIVERGENCE_TEXT", "").lower() == "true":
        line["stt_text"] = stt_text
        line["text"] = text
    print(json.dumps(line), flush=True)
