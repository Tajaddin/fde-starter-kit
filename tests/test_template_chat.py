"""chat template smoke tests."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from fde_kit import MockChatBackend


def _load(slug: str):
    import sys

    path = Path(__file__).resolve().parents[1] / "templates" / slug / "app.py"
    spec = importlib.util.spec_from_file_location(f"_{slug}_app", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def test_chat_run_repl_returns_replies_per_prompt():
    chat = _load("chat")
    out = chat.run_repl(MockChatBackend(), ["hi", "what's up?"])
    assert len(out) == 2


def test_chat_session_appends_history():
    chat = _load("chat")
    s = chat.ChatSession(backend=MockChatBackend())
    s.turn("first")
    s.turn("second")
    # 2 user + 2 assistant = 4 entries
    assert len(s.history) == 4
    assert s.history[0]["role"] == "user"
    assert s.history[1]["role"] == "assistant"


def test_chat_session_reset_clears_history():
    chat = _load("chat")
    s = chat.ChatSession(backend=MockChatBackend())
    s.turn("x")
    assert s.history
    s.reset()
    assert s.history == []
