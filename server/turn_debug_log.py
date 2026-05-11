"""Structured per-turn JSONL debug logging for the Phase 1 voice loop."""
import json
import threading
import time
from pathlib import Path
from typing import Any, Mapping

from server.config import PROJECT_ROOT


class TurnDebugLogger:
    """Append structured turn-debug events to a JSONL file."""

    def __init__(
        self,
        *,
        enabled: bool,
        path: str | Path | None,
        include_system_prompt: bool,
    ) -> None:
        self._enabled = enabled
        self._path = Path(path).expanduser() if path is not None else None
        self._include_system_prompt = include_system_prompt
        self._lock = threading.Lock()

    @classmethod
    def from_settings(cls, settings: Any) -> "TurnDebugLogger":
        raw_path = Path(getattr(settings, "debug_turn_log_path", "debug/turns.jsonl"))
        path = raw_path if raw_path.is_absolute() else PROJECT_ROOT / raw_path
        return cls(
            enabled=bool(getattr(settings, "debug_turn_log", False)),
            path=path,
            include_system_prompt=bool(
                getattr(settings, "debug_turn_log_include_system_prompt", False)
            ),
        )

    @property
    def enabled(self) -> bool:
        return self._enabled and self._path is not None

    def log(
        self, *, event: str, turn_id: int, extra: Mapping[str, Any] | None = None
    ) -> None:
        if not self.enabled or self._path is None:
            return

        record: dict[str, Any] = {"event": event, "turn_id": turn_id, "ts": time.time()}
        if extra:
            record.update(extra)
        if not self._include_system_prompt:
            record.pop("llm_system_prompt", None)

        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            line = json.dumps(record, ensure_ascii=False)
            with self._lock:
                with self._path.open("a", encoding="utf-8") as fh:
                    fh.write(line)
                    fh.write("\n")
        except OSError:
            return
