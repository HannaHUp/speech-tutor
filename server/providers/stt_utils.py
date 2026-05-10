"""Whisper hallucination filter - Hermes borrow.

# Borrowed from Hermes: tools/voice_mode.py::WHISPER_HALLUCINATIONS
# Borrowed from Hermes: tools/voice_mode.py::_HALLUCINATION_REPEAT_RE
# Borrowed from Hermes: tools/voice_mode.py::is_whisper_hallucination
# Verified deepwiki 2026-05-10.
#
# CORRECTION: CONTEXT.md Directly-Borrowed row 4 cites tools/transcription_tools.py.
# Deepwiki confirms the code lives in tools/voice_mode.py. Attribution corrected here.
"""
import re


# Borrowed from Hermes: tools/voice_mode.py::WHISPER_HALLUCINATIONS
WHISPER_HALLUCINATIONS = frozenset(
    {
        "thank you.",
        "thank you",
        "thanks for watching.",
        "thanks for watching",
        "subscribe to my channel.",
        "subscribe to my channel",
        "like and subscribe.",
        "like and subscribe",
        "please subscribe.",
        "please subscribe",
        "thank you for watching.",
        "thank you for watching",
        "bye.",
        "bye",
        "you",
        "the end.",
        "the end",
        "продолжение следует",
        "продолжение следует...",
        "sous-titres",
        "sous-titres réalisés par la communauté d'amara.org",
        "sottotitoli creati dalla comunità amara.org",
        "untertitel von stephanie geiges",
        "amara.org",
        "www.mooji.org",
        "ご視聴ありがとうございました",
    }
)


# Borrowed from Hermes: tools/voice_mode.py::_HALLUCINATION_REPEAT_RE
_HALLUCINATION_REPEAT_RE = re.compile(
    r"^(?:thank you|thanks|bye|you|ok|okay|the end|\.|\s|,|!)+$",
    flags=re.IGNORECASE,
)


def is_whisper_hallucination(text: str) -> bool:
    """Return True for known Whisper hallucination artifacts."""
    if not text:
        return True
    normalized = text.strip().lower()
    if not normalized:
        return True
    if normalized in WHISPER_HALLUCINATIONS:
        return True
    if _HALLUCINATION_REPEAT_RE.match(normalized):
        return True
    return False
