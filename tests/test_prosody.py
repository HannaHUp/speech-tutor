"""REQ-02 - librosa prosody extraction tests."""
import ast
import io
import wave

import numpy as np


def _make_wav_bytes(duration_s: float, freq_hz: float = 220.0, sr: int = 16000) -> bytes:
    t = np.linspace(0, duration_s, int(sr * duration_s), endpoint=False)
    amp = (np.sin(2 * np.pi * freq_hz * t) * 0.3 * 32767).astype("<i2")
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(amp.tobytes())
    return buf.getvalue()


def test_prosody_keys_on_tone_with_word_timestamps():
    from server.prosody import extract_prosody

    wav = _make_wav_bytes(duration_s=2.0)
    words = [
        {"word": "hello", "start": 0.1, "end": 0.5},
        {"word": "world", "start": 0.6, "end": 1.0},
    ]

    result = extract_prosody(wav, word_timestamps=words)

    assert set(result.keys()) == {"pace", "pitch", "hesitations", "stress"}
    assert result["stress"] == "—"


def test_prosody_fail_open_on_tiny_audio():
    from server.prosody import extract_prosody

    result = extract_prosody(b"RIFF\x00\x00\x00\x00WAVE", word_timestamps=[])

    assert result == {}


def test_prosody_fail_open_on_half_second():
    from server.prosody import extract_prosody

    wav = _make_wav_bytes(duration_s=0.2)

    result = extract_prosody(wav, word_timestamps=[])

    assert result == {}


def test_prosody_hesitation_detection():
    from server.prosody import extract_prosody

    wav = _make_wav_bytes(duration_s=2.0)
    words = [
        {"word": "I", "start": 0.0, "end": 0.1},
        {"word": "went", "start": 0.3, "end": 0.5},
        {"word": "yesterday", "start": 1.2, "end": 1.9},
    ]

    result = extract_prosody(wav, word_timestamps=words)

    assert "1" in result["hesitations"]
    assert "yesterday" in result["hesitations"]


def test_prosody_pace_label_thresholds():
    from server.prosody import extract_prosody

    wav = _make_wav_bytes(duration_s=2.0)
    words = [
        {"word": "one", "start": 0.0, "end": 0.4},
        {"word": "two", "start": 0.5, "end": 0.9},
        {"word": "three", "start": 1.0, "end": 1.4},
        {"word": "four", "start": 1.5, "end": 1.9},
    ]

    result = extract_prosody(wav, word_timestamps=words)

    assert "normal" in result["pace"]


def test_librosa_imported_at_module_level():
    src = open("server/prosody.py", encoding="utf-8").read()
    tree = ast.parse(src)
    module_imports = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    names = [
        name.name
        for imp in module_imports
        if isinstance(imp, ast.Import)
        for name in imp.names
    ]
    assert "librosa" in names
