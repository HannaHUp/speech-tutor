"""Anthropic LLM provider with Hermes-style prompt cache control.

Borrowed from Hermes: agent/prompt_caching.py::apply_anthropic_cache_control
Verified deepwiki 2026-05-10.
"""
from typing import AsyncIterator

from anthropic import AsyncAnthropic

from server.config import Settings


class AnthropicLLM:
    """LLMProvider implementation using Anthropic streaming."""

    def __init__(self, settings: Settings) -> None:
        api_key = settings.anthropic_api_key
        if hasattr(api_key, "get_secret_value"):
            api_key = api_key.get_secret_value()
        self._client = AsyncAnthropic(api_key=api_key)
        self._model = settings.llm_model

    async def stream(
        self, session_prompt: str, messages: list[dict]
    ) -> AsyncIterator[str]:
        async with self._client.messages.stream(
            model=self._model,
            max_tokens=1024,
            system=[
                {
                    "type": "text",
                    "text": session_prompt,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=messages,
        ) as stream:
            async for text in stream.text_stream:
                yield text
