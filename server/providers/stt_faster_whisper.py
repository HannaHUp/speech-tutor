"""FasterWhisperSTT - free dev-stack STT via faster-whisper on CPU.

Loads WhisperModel at init so FastAPI startup can pay the model load cost once.
First run may download model weights into the Hugging Face cache.
"""
import asyncio
import io
import sys

from faster_whisper import WhisperModel

from server.config import Settings

from .stt_utils import is_whisper_hallucination


class FasterWhisperSTT:
    """STTProvider impl via faster-whisper."""

    def __init__(self, settings: Settings) -> None:
        model_name = settings.stt_faster_whisper_model
        print(
            f"[FasterWhisperSTT] Loading WhisperModel({model_name!r}, "
            "device='cpu', compute_type='int8'). First run may download weights.",
            file=sys.stderr,
        )
        self._model = WhisperModel(
            model_name,
            device="cpu",
            compute_type="int8",
        )

    async def transcribe(
        self, audio_bytes: bytes, *, mime: str = "audio/webm"
    ) -> tuple[str, list[dict]]:
        text, words = await asyncio.to_thread(self._transcribe_sync, audio_bytes)
        if is_whisper_hallucination(text):
            return "", []
        return text, words

    def _transcribe_sync(self, audio_bytes: bytes) -> tuple[str, list[dict]]:
        # Applied by us (not a Hermes copy): prevents cross-utterance contamination.
        segments, _info = self._model.transcribe(
            io.BytesIO(audio_bytes),
            beam_size=5,
            word_timestamps=True,
            condition_on_previous_text=False,
        )
        parts: list[str] = []
        words: list[dict] = []
        for segment in segments:
            parts.append(segment.text)
            for word in segment.words or []:
                words.append(
                    {
                        "word": word.word,
                        "start": float(word.start),
                        "end": float(word.end),
                    }
                )
        return " ".join(parts).strip(), words
