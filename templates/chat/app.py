"""Multi-turn chat with system prompt + conversation history.

Run:  python app.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from fde_kit.backends import ChatBackend, MockChatBackend, Reply


SYSTEM = (
    "You are a concise assistant. Reply in <=2 sentences unless the user asks "
    "for detail."
)


@dataclass
class ChatSession:
    backend: ChatBackend
    system: str = SYSTEM
    history: list[dict] = field(default_factory=list)

    def turn(self, user_msg: str) -> Reply:
        self.history.append({"role": "user", "content": user_msg})
        reply = self.backend.chat(self.system, self.history)
        self.history.append({"role": "assistant", "content": reply.text})
        return reply

    def reset(self) -> None:
        self.history.clear()


def run_repl(backend: ChatBackend, prompts: Iterable[str]) -> list[str]:
    """Pure-function REPL for tests / CI."""
    session = ChatSession(backend=backend)
    out = []
    for p in prompts:
        r = session.turn(p)
        out.append(r.text)
    return out


if __name__ == "__main__":
    import os

    if os.environ.get("ANTHROPIC_API_KEY"):
        from fde_kit.backends import AnthropicChatBackend

        backend = AnthropicChatBackend()
    else:
        backend = MockChatBackend()
    print("[ctrl-d to exit]")
    session = ChatSession(backend=backend)
    while True:
        try:
            msg = input("you> ").strip()
        except EOFError:
            break
        if not msg:
            continue
        reply = session.turn(msg)
        print("ai>", reply.text)
