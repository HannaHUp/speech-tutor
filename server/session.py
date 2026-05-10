"""Session state with Hermes-style frozen system-prompt snapshot.

Borrowed from Hermes: run_agent.py::AIAgent._cached_system_prompt
Borrowed from Hermes: tools/memory_tool.py::MemoryStore._system_prompt_snapshot
Verified deepwiki 2026-05-10.
"""
from typing import Mapping

from server.config import Settings
from server.prompt_builder import build_session_prompt, build_user_turn_with_prosody


class Session:
    """In-memory per-WebSocket session history."""

    def __init__(self, *, llm_model: str, settings: Settings) -> None:
        self._system_prompt_snapshot = build_session_prompt(settings)
        self._llm_model = llm_model
        self._messages: list[dict] = []

    @property
    def system_prompt(self) -> str:
        return self._system_prompt_snapshot

    @property
    def llm_model(self) -> str:
        return self._llm_model

    @property
    def messages(self) -> list[dict]:
        return list(self._messages)

    def append_user(self, text: str, prosody: Mapping[str, str]) -> None:
        self._messages.append(
            {"role": "user", "content": build_user_turn_with_prosody(text, prosody)}
        )

    def append_assistant(self, text: str) -> None:
        self._messages.append({"role": "assistant", "content": text})
