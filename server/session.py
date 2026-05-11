"""Session state with Hermes-style frozen system-prompt snapshot.

Borrowed from Hermes: run_agent.py::AIAgent._cached_system_prompt
Borrowed from Hermes: tools/memory_tool.py::MemoryStore._system_prompt_snapshot
Verified deepwiki 2026-05-10.
"""
from typing import Mapping

from server.config import Settings
from server.prompt_builder import UserTurnContext, build_session_prompt


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

    def append_user(self, turn: UserTurnContext) -> None:
        self._messages.append({"role": "user", "content": turn.to_llm_content()})

    def append_user_text(self, text: str) -> None:
        self.append_user(UserTurnContext.from_text(text))

    def append_user_voice(
        self, *, edited_text: str, stt_text: str, prosody: Mapping[str, str]
    ) -> None:
        self.append_user(
            UserTurnContext.from_voice(
                edited_text=edited_text,
                stt_text=stt_text,
                prosody=prosody,
            )
        )

    def append_assistant(self, text: str) -> None:
        self._messages.append({"role": "assistant", "content": text})
