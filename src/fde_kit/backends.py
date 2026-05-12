"""Pluggable chat backend shared by every example.

* :class:`MockChatBackend` — deterministic, runs without API keys.
* :class:`AnthropicChatBackend` — wraps the real SDK.

The five examples import these via ``from fde_kit.backends import ...`` so
their tests can pass a Mock without touching the network.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable, Protocol


@dataclass
class Reply:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = "mock"


class ChatBackend(Protocol):
    def chat(self, system: str | None, messages: list[dict]) -> Reply: ...


class MockChatBackend:
    """Deterministic backend. ``responder`` is called with the conversation."""

    def __init__(
        self,
        responder: Callable[[str | None, list[dict]], str] | None = None,
    ) -> None:
        self.responder = responder or (lambda s, m: f"mock-reply: {m[-1]['content'][:80]}")
        self.calls: list[dict] = []

    def chat(self, system: str | None, messages: list[dict]) -> Reply:
        self.calls.append({"system": system, "messages": list(messages)})
        text = self.responder(system, messages)
        prompt = " ".join(m.get("content", "") for m in messages)
        return Reply(
            text=text,
            input_tokens=max(1, len(prompt) // 4),
            output_tokens=max(1, len(text) // 4),
            model="mock",
        )


class AnthropicChatBackend:
    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        max_tokens: int = 1024,
    ) -> None:
        from anthropic import Anthropic  # noqa: F401  (lazy)

        self.model = model or os.environ.get("FDE_MODEL", "claude-haiku-4-5-20251001")
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.max_tokens = max_tokens

    def chat(self, system: str | None, messages: list[dict]) -> Reply:
        from anthropic import Anthropic

        client = Anthropic(api_key=self._api_key)
        kwargs: dict = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": messages,
        }
        if system:
            kwargs["system"] = system
        resp = client.messages.create(**kwargs)
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        return Reply(
            text=text,
            input_tokens=resp.usage.input_tokens,
            output_tokens=resp.usage.output_tokens,
            model=resp.model,
        )
