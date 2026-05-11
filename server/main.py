import os
"""Hermes Speech Tutor - FastAPI entry point.

Lifespan order (D-18):
  1. Settings() - pydantic-settings validates config + API keys
  2. check_ffmpeg(settings) - fail fast with winget message if missing
  3. app ready to serve
"""
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from server.config import Settings
from server.providers import (
    get_llm_provider,
    get_pronunciation_provider,
    get_stt_provider,
    get_tts_provider,
)
from server.ws_handler import websocket_endpoint


def check_ffmpeg(settings: Settings) -> None:
    """D-18 startup ffmpeg check.

    Phase 1 exit section 8 makes this a hard gate.
    """
    ffmpeg_override = settings.ffmpeg_path or os.environ.get("FFMPEG_PATH")
    if ffmpeg_override:
        ffmpeg_path = Path(ffmpeg_override).expanduser()
        if ffmpeg_path.is_file():
            return
    if shutil.which("ffmpeg") is None:
        print(
            "ERROR: ffmpeg not found on PATH.\n"
            "Set FFMPEG_PATH in .env to the full ffmpeg.exe path if Windows PATH is inconsistent.\n"
            "Install via 'winget install Gyan.FFmpeg' (Windows) or "
            "'apt-get install ffmpeg' (Linux).\n"
            "Restart your shell after install.",
            file=sys.stderr,
        )
        sys.exit(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    check_ffmpeg(settings)
    app.state.settings = settings
    app.state.stt_provider = get_stt_provider(settings)
    app.state.tts_provider = get_tts_provider(settings)
    app.state.llm_provider = get_llm_provider(settings)
    app.state.pronunciation_provider = get_pronunciation_provider(settings)
    app.state.executor = ThreadPoolExecutor(max_workers=4)
    try:
        yield
    finally:
        app.state.executor.shutdown(wait=False, cancel_futures=True)


app = FastAPI(
    title="hermes-speech-tutor",
    version="0.1.0-phase1-wave2",
    lifespan=lifespan,
)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


app.websocket("/ws")(websocket_endpoint)

_web_dist = Path(__file__).resolve().parents[1] / "web" / "dist"
app.mount("/", StaticFiles(directory=_web_dist, html=True, check_dir=False), name="web")
