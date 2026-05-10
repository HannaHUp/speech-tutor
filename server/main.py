"""Hermes Speech Tutor - FastAPI entry point.

Lifespan order (D-18):
  1. check_ffmpeg() - fail fast with winget message if missing
  2. Settings() - pydantic-settings validates config + API keys
  3. app ready to serve
"""
import shutil
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from server.config import Settings


def check_ffmpeg() -> None:
    """D-18 startup ffmpeg check.

    Phase 1 exit section 8 makes this a hard gate.
    """
    if shutil.which("ffmpeg") is None:
        print(
            "ERROR: ffmpeg not found on PATH.\n"
            "Install via 'winget install Gyan.FFmpeg' (Windows) or "
            "'apt-get install ffmpeg' (Linux).\n"
            "Restart your shell after install.",
            file=sys.stderr,
        )
        sys.exit(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    check_ffmpeg()
    app.state.settings = Settings()
    yield


app = FastAPI(
    title="hermes-speech-tutor",
    version="0.1.0-phase1-wave2",
    lifespan=lifespan,
)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
