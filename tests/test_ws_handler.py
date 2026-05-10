"""REQ-02/08 - WebSocket handler and startup check tests. Impl in Plan 02/06."""
import pytest


def test_ffmpeg_missing_exits(monkeypatch, capsys):
    import shutil

    monkeypatch.setattr(shutil, "which", lambda _: None)
    from server.main import check_ffmpeg

    with pytest.raises(SystemExit) as exc:
        check_ffmpeg()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "winget install Gyan.FFmpeg" in captured.err
    assert "ffmpeg not found" in captured.err


def test_settings_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    from pydantic import ValidationError
    from server.config import Settings

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_api_keys_are_redacted(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-visible-secret")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-visible-secret")

    from server.config import Settings

    settings = Settings(_env_file=None)

    assert "sk-visible-secret" not in repr(settings)
    assert "sk-ant-visible-secret" not in repr(settings)
    assert "**********" in repr(settings)
    assert settings.openai_api_key.get_secret_value() == "sk-visible-secret"


@pytest.mark.skip(reason="W0 stub - implemented in Plan 06 (WS handler)")
def test_turn_send_carries_both_stt_text_and_text():
    ...


@pytest.mark.skip(reason="W0 stub - implemented in Plan 06 (integration)")
@pytest.mark.integration
def test_latency_10_turns():
    ...
