"""NullPronunciationProvider - feature flag default OFF per D-10.

Real impls can plug in later via the same Protocol.
"""
from .protocols import PronunciationProvider


class NullPronunciationProvider:
    """Implements PronunciationProvider. Always returns disabled."""

    def analyze(self, audio_bytes: bytes) -> dict:
        return {"enabled": False}


_: PronunciationProvider = NullPronunciationProvider()
