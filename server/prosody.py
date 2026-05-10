"""Prosody feature extraction using librosa.

Not a Hermes borrow; Hermes does not do prosody. D-08 fail-open: return {}
when extraction is not reliable so the LLM prosody block is omitted.
"""
import io
from typing import Sequence

import librosa
import numpy as np


_PACE_SLOW_MAX = 1.5
_PACE_NORMAL_MAX = 2.8
_HESITATION_MS_THRESHOLD = 500


def _label_pace(wps: float) -> str:
    if wps < _PACE_SLOW_MAX:
        return "slow"
    if wps <= _PACE_NORMAL_MAX:
        return "normal"
    return "fast"


def _summarize_pitch(f0: np.ndarray) -> str:
    valid = f0[~np.isnan(f0)]
    if valid.size < 4:
        return "flat"
    quarter = max(1, valid.size // 4)
    head = float(np.mean(valid[:quarter]))
    tail = float(np.mean(valid[-quarter:]))
    rel = (tail - head) / max(head, 1e-6)
    if rel > 0.15:
        if valid.size >= 2 and valid[-1] > valid[-2]:
            return "rising_final (possible question intonation)"
        return "rising_overall"
    if rel < -0.15:
        return "falling_final"
    if float(np.std(valid)) > 0.3 * float(np.mean(valid)):
        return "mixed"
    return "flat"


def _detect_hesitations(word_timestamps: Sequence[dict]) -> str:
    count = 0
    first_desc = None
    prev_end = 0.0
    for word in word_timestamps:
        gap_ms = (word["start"] - prev_end) * 1000
        if gap_ms > _HESITATION_MS_THRESHOLD:
            count += 1
            if first_desc is None:
                first_desc = f"before \"{word['word'].strip()}\", {int(gap_ms)}ms"
        prev_end = word["end"]
    if first_desc is None:
        return str(count)
    return f"{count} ({first_desc})"


def extract_prosody(audio_bytes: bytes, *, word_timestamps: Sequence[dict]) -> dict:
    """Extract pace, pitch, hesitations, and stress or return {} on failure."""
    try:
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=None, mono=True)
        if y is None or y.size < sr // 2:
            return {}

        duration_s = y.size / sr
        word_count = len(word_timestamps)
        if word_count:
            wps = word_count / duration_s
            pace = f"{wps:.1f} wps ({_label_pace(wps)})"
        else:
            pace = "— wps (unknown)"

        f0, _voiced_flag, _voiced_prob = librosa.pyin(y, fmin=80.0, fmax=500.0, sr=sr)
        if f0 is None:
            return {}

        return {
            "pace": pace,
            "pitch": _summarize_pitch(f0),
            "hesitations": _detect_hesitations(word_timestamps),
            "stress": "—",
        }
    except Exception:
        return {}
