"""OpenAI LLM provider via the chat completions streaming API."""
from typing import AsyncIterator

from openai import AsyncOpenAI

from server.config import Settings


class OpenAILLM:
    """LLMProvider implementation using OpenAI streaming chat completions."""

    def __init__(self, settings: Settings) -> None:
        api_key = settings.openai_api_key
        if hasattr(api_key, "get_secret_value"):
            api_key = api_key.get_secret_value()
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = settings.llm_model

    async def stream(
        self, session_prompt: str, messages: list[dict]
    ) -> AsyncIterator[str]:
        stream = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "system", "content": session_prompt}, *messages],
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                yield delta
