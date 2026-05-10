"""Shared pytest fixtures for Phase 1."""
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def silence_1s_bytes() -> bytes:
    return (Path(__file__).parent / "fixtures" / "silence_1s.wav").read_bytes()


@pytest.fixture
def dummy_settings():
    m = MagicMock()
    m.stt_impl = "openai"
    m.tts_impl = "openai"
    m.tts_voice = "nova"
    m.llm_model = "claude-haiku-4-5-20251001"
    m.pronunciation_enabled = False
    m.openai_api_key = "sk-test"
    m.anthropic_api_key = "sk-ant-test"
    m.stt_faster_whisper_model = "small"
    return m


@pytest.fixture
def mock_websocket():
    ws = MagicMock()
    ws.send_text = AsyncMock()
    ws.send_bytes = AsyncMock()
    ws.receive_text = AsyncMock()
    ws.receive_bytes = AsyncMock()
    ws.accept = AsyncMock()
    return ws
