"""Prompt builder adapted from Hermes layered-prefix construction.

Borrowed from Hermes: agent/prompt_builder.py
Verified deepwiki 2026-05-10.
"""
from pathlib import Path
from typing import Mapping

from server.config import Settings


_SOUL_PATH = Path(__file__).resolve().parent.parent / "SOUL.md"


def build_session_prompt(settings: Settings) -> str:
    """Build the stable system prompt prefix for a session."""
    _ = settings
    if _SOUL_PATH.exists():
        text = _SOUL_PATH.read_text(encoding="utf-8").strip()
    else:
        text = "You are a friendly English speech tutor."
    lines = [line for line in text.splitlines() if not line.strip().startswith("<!--")]
    return "\n".join(lines).strip() or "You are a friendly English speech tutor."


def build_user_turn_with_prosody(text: str, prosody: Mapping[str, str]) -> str:
    """Attach the D-06 fenced prosody block when prosody extraction succeeds."""
    if not prosody:
        return text
    lines = [
        f"pace: {prosody.get('pace', '—')}",
        f"pitch: {prosody.get('pitch', '—')}",
        f"hesitations: {prosody.get('hesitations', '—')}",
        f"stress: {prosody.get('stress', '—')}",
    ]
    return f"{text}\n\n```prosody\n" + "\n".join(lines) + "\n```"
