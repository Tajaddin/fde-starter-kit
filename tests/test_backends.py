"""Backend protocol + MockChatBackend tests."""

from __future__ import annotations

from fde_kit import MockChatBackend, Reply


def test_mock_default_responder_echoes_last_user():
    b = MockChatBackend()
    r = b.chat(None, [{"role": "user", "content": "hello"}])
    assert "hello" in r.text


def test_mock_records_calls_for_inspection():
    b = MockChatBackend()
    b.chat("sys", [{"role": "user", "content": "1"}])
    b.chat("sys", [{"role": "user", "content": "2"}])
    assert len(b.calls) == 2
    assert b.calls[1]["messages"][0]["content"] == "2"


def test_mock_custom_responder():
    b = MockChatBackend(responder=lambda s, m: "fixed")
    assert b.chat(None, [{"role": "user", "content": "x"}]).text == "fixed"


def test_reply_token_counts_are_estimated():
    b = MockChatBackend(responder=lambda s, m: "abcd" * 10)
    r = b.chat(None, [{"role": "user", "content": "xyz"}])
    assert r.input_tokens >= 1
    assert r.output_tokens >= 1
