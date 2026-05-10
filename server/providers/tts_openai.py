"""OpenAI TTS provider via the openai SDK 1.x."""
from openai import AsyncOpenAI

from server.config import Settings


class OpenAITTS:
    """TTSProvider implementation using OpenAI tts-1."""

    def __init__(self, settings: Settings) -> None:
        api_key = settings.openai_api_key
        if hasattr(api_key, "get_secret_value"):
            api_key = api_key.get_secret_value()
        self._client = AsyncOpenAI(api_key=api_key)
        self._voice = settings.tts_voice

    async def synthesize_sentence(self, text: str) -> bytes:
        resp = await self._client.audio.speech.create(
            model="tts-1",
            voice=self._voice,
            input=text,
            response_format="mp3",
        )
        if getattr(resp, "content", None) is not None:
            return resp.content
        return await resp.aread()
