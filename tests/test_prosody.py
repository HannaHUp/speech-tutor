"""REQ-02 - librosa prosody extraction tests. Implementation lands in Plan 05."""
import pytest


@pytest.mark.skip(reason="W0 stub - implemented in Plan 05 (prosody)")
def test_prosody_keys(silence_1s_bytes):
    from server.prosody import extract_prosody

    result = extract_prosody(silence_1s_bytes, word_timestamps=[])
    assert set(result.keys()) == {"pace", "pitch", "hesitations", "stress"}
    assert result["stress"] == "-"


@pytest.mark.skip(reason="W0 stub - implemented in Plan 05")
def test_prosody_fail_open_on_short_audio():
    from server.prosody import extract_prosody

    result = extract_prosody(b"\x00" * 10, word_timestamps=[])
    assert result == {} or "error" in result
