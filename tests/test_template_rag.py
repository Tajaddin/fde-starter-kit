"""rag template smoke tests."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from fde_kit import MockChatBackend


def _load_rag():
    import sys

    path = Path(__file__).resolve().parents[1] / "templates" / "rag" / "app.py"
    spec = importlib.util.spec_from_file_location("_rag_app", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def test_bm25_retrieves_relevant_doc():
    rag = _load_rag()
    idx = rag.load_corpus()
    hits = idx.search("on-call rotation", k=3)
    assert hits
    titles = [h.doc.title for h in hits]
    assert any("On-call" in t for t in titles)


def test_ask_returns_sources_and_text():
    rag = _load_rag()
    idx = rag.load_corpus()
    backend = MockChatBackend(responder=lambda s, m: "Answer using [^1].")
    ans = rag.ask(backend, idx, "what is the remote policy?")
    assert ans.sources
    assert ans.text


def test_ask_handles_no_match():
    rag = _load_rag()
    idx = rag.BM25()  # empty
    backend = MockChatBackend()
    ans = rag.ask(backend, idx, "anything")
    assert "don't have enough context" in ans.text.lower()
    assert ans.sources == []
