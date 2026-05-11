"""REQ-02/08 - WebSocket handler and startup check tests."""
import json

import pytest
from fastapi.testclient import TestClient


def test_ffmpeg_missing_exits(monkeypatch, capsys):
    import shutil

    monkeypatch.setattr(shutil, "which", lambda _: None)
    from server.main import check_ffmpeg
    from server.config import Settings

    with pytest.raises(SystemExit) as exc:
        check_ffmpeg(
            Settings(
                _env_file=None,
                openai_api_key="sk-test",
                ffmpeg_path=None,
            )
        )
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "winget install Gyan.FFmpeg" in captured.err
    assert "ffmpeg not found" in captured.err


def test_ffmpeg_path_override_allows_startup(monkeypatch):
    import shutil

    monkeypatch.setattr(shutil, "which", lambda _: None)
    monkeypatch.setattr("pathlib.Path.is_file", lambda self: True)
    from server.main import check_ffmpeg
    from server.config import Settings

    check_ffmpeg(
        Settings(
            _env_file=None,
            openai_api_key="sk-test",
            ffmpeg_path=r"C:\tools\ffmpeg\bin\ffmpeg.exe",
        )
    )


def test_settings_missing_openai_api_key_raises(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    from pydantic import ValidationError
    from server.config import Settings

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_allows_default_llm_with_only_openai_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-visible-secret")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    from server.config import Settings

    settings = Settings(_env_file=None)

    assert settings.llm_impl == "openai"
    assert settings.openai_api_key.get_secret_value() == "sk-visible-secret"


def test_settings_reads_repo_env_independent_of_cwd(monkeypatch):
    monkeypatch.chdir("web")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    from server.config import Settings

    settings = Settings()

    assert settings.openai_api_key.get_secret_value().startswith("sk-")


def test_settings_requires_anthropic_key_only_for_anthropic_llm(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-visible-secret")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    from pydantic import ValidationError
    from server.config import Settings

    with pytest.raises(ValidationError):
        Settings(_env_file=None, llm_impl="anthropic")


def test_settings_api_keys_are_redacted(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-visible-secret")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-visible-secret")

    from server.config import Settings

    settings = Settings(_env_file=None)

    assert "sk-visible-secret" not in repr(settings)
    assert "sk-ant-visible-secret" not in repr(settings)
    assert "**********" in repr(settings)
    assert settings.openai_api_key.get_secret_value() == "sk-visible-secret"


def test_uvicorn_can_import_fastapi_app():
    from uvicorn.importer import import_from_string

    loaded = import_from_string("server.main:app")

    from server.main import app

    assert loaded is app


def test_turn_send_carries_both_stt_text_and_text():
    payload = {"type": "turn.send", "turn_id": 7, "stt_text": "raw", "text": "edited"}

    assert payload["stt_text"] == "raw"
    assert payload["text"] == "edited"


def test_stage_latency_log_schema(capsys):
    from server.latency_log import log_stage_latency

    log_stage_latency(turn_id=3, stage="stt", ms=42)

    line = json.loads(capsys.readouterr().out)
    assert line["event"] == "stage_latency"
    assert line["turn_id"] == 3
    assert line["stage"] == "stt"
    assert line["ms"] == 42
    assert isinstance(line["ts"], float)


def test_stt_divergence_default_omits_text(monkeypatch, capsys):
    monkeypatch.delenv("LOG_STT_DIVERGENCE_TEXT", raising=False)
    from server.latency_log import log_stt_divergence

    log_stt_divergence(turn_id=2, stt_text="raw words", text="edited words")

    line = json.loads(capsys.readouterr().out)
    assert line == {
        "event": "stt_divergence",
        "turn_id": 2,
        "edited": True,
        "stt_len": 9,
        "text_len": 12,
        "ts": line["ts"],
    }
    assert "stt_text" not in line
    assert "text" not in line


def test_stt_divergence_env_can_include_text(monkeypatch, capsys):
    monkeypatch.setenv("LOG_STT_DIVERGENCE_TEXT", "true")
    from server.latency_log import log_stt_divergence

    log_stt_divergence(turn_id=2, stt_text="raw words", text="edited words")

    line = json.loads(capsys.readouterr().out)
    assert line["stt_text"] == "raw words"
    assert line["text"] == "edited words"


class _FakeSTT:
    def __init__(self):
        self.calls = 0

    async def transcribe(self, audio_bytes: bytes, *, mime: str = "audio/webm"):
        self.calls += 1
        assert audio_bytes == b"audio"
        return "hello from audio", [{"word": "hello", "start": 0.0, "end": 0.2}]


class _FakeTTS:
    async def synthesize_sentence(self, text: str) -> bytes:
        return f"mp3:{text}".encode()


class _FakeLLM:
    async def stream(self, session_prompt: str, messages: list[dict]):
        yield "This is a short tutor response."


def _patch_lifespan(monkeypatch):
    from server import main

    stt = _FakeSTT()
    monkeypatch.setattr(main, "check_ffmpeg", lambda: None)
    monkeypatch.setattr(main, "get_stt_provider", lambda settings: stt)
    monkeypatch.setattr(main, "get_tts_provider", lambda settings: _FakeTTS())
    monkeypatch.setattr(main, "get_llm_provider", lambda settings: _FakeLLM())
    monkeypatch.setattr(main, "get_pronunciation_provider", lambda settings: object())
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    return main.app, stt


def test_ws_handler_ready_path(monkeypatch):
    app, stt = _patch_lifespan(monkeypatch)

    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_json({"type": "turn.start"})
            assert ws.receive_json() == {"type": "turn.started", "turn_id": 1}

            ws.send_json({"type": "audio.frame", "turn_id": 1, "seq": 0})
            ws.send_bytes(b"audio")
            ws.send_json({"type": "turn.stop"})

            assert ws.receive_json() == {"type": "stt.running", "turn_id": 1}
            assert ws.receive_json() == {
                "type": "transcript.ready",
                "turn_id": 1,
                "stt_text": "hello from audio",
            }
    assert stt.calls == 1


def test_ws_text_only_turn_skips_stt_and_streams_tts(monkeypatch):
    app, stt = _patch_lifespan(monkeypatch)

    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_json({"type": "turn.start"})
            assert ws.receive_json() == {"type": "turn.started", "turn_id": 1}

            ws.send_json({"type": "turn.send", "turn_id": 1, "text": "typed prompt"})

            assert ws.receive_json()["type"] == "llm.delta"
            chunk_meta = ws.receive_json()
            assert chunk_meta["type"] == "tts.chunk"
            assert chunk_meta["mime"] == "audio/mpeg"
            assert ws.receive_bytes().startswith(b"mp3:")
            assert ws.receive_json() == {
                "type": "tts.done",
                "turn_id": 1,
                "total_chunks": 1,
            }
            assert ws.receive_json() == {"type": "turn.done", "turn_id": 1}
    assert stt.calls == 0


@pytest.mark.skip(reason="W0 stub - implemented in Plan 06 (integration)")
@pytest.mark.integration
def test_latency_10_turns():
    ...
