"""OpenAIWhisperSTT - paid-stack default STT via openai SDK 1.x.

Uses whisper-1 and returns (text, word_timestamps) per STTProvider Protocol.
Applies is_whisper_hallucination() before return.
"""
import io

from openai import AsyncOpenAI

from server.config import Settings

from .stt_utils import is_whisper_hallucination


class OpenAIWhisperSTT:
    """STTProvider impl via OpenAI Whisper API."""

    def __init__(self, settings: Settings) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.openai_api_key.get_secret_value()
        )

    async def transcribe(
        self, audio_bytes: bytes, *, mime: str = "audio/webm"
    ) -> tuple[str, list[dict]]:
        ext = "webm" if mime == "audio/webm" else "wav"
        with io.BytesIO(audio_bytes) as audio_file:
            audio_file.name = f"audio.{ext}"
            response = await self._client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["word"],
            )

        text = (response.text or "").strip()
        if is_whisper_hallucination(text):
            return "", []

        words = []
        for word in getattr(response, "words", None) or []:
            words.append(
                {
                    "word": word.word,
                    "start": float(word.start),
                    "end": float(word.end),
                }
            )
        return text, words
