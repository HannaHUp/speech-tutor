"""REQ-02/08 - WebSocket handler and startup check tests. Impl in Plan 02/06."""
import pytest


@pytest.mark.skip(reason="W0 stub - implemented in Plan 02 (ffmpeg startup check)")
def test_ffmpeg_missing_exits(monkeypatch):
    import shutil

    monkeypatch.setattr(shutil, "which", lambda _: None)
    from server.main import check_ffmpeg

    with pytest.raises(SystemExit) as exc:
        check_ffmpeg()
    assert exc.value.code == 1


@pytest.mark.skip(reason="W0 stub - implemented in Plan 06 (WS handler)")
def test_turn_send_carries_both_stt_text_and_text():
    ...


@pytest.mark.skip(reason="W0 stub - implemented in Plan 06 (integration)")
@pytest.mark.integration
def test_latency_10_turns():
    ...
