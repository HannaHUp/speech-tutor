"""Hermes Speech Tutor - FastAPI entry point.

Phase 1 scaffold. Real endpoints and startup checks land in Plan 02/06.
"""
from fastapi import FastAPI

app = FastAPI(title="hermes-speech-tutor", version="0.1.0-phase1-wave0")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "phase": "1-wave0-scaffold"}
