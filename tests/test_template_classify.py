"""classify template smoke tests."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from fde_kit import MockChatBackend


def _load_classify():
    import sys

    path = Path(__file__).resolve().parents[1] / "templates" / "classify" / "app.py"
    spec = importlib.util.spec_from_file_location("_classify_app", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def test_classify_parses_valid_json():
    cls = _load_classify()
    backend = MockChatBackend(
        responder=lambda s, m: '{"label":"support","confidence":0.9,"reasoning":"bug mention"}'
    )
    r = cls.classify(backend, "there's a bug", ["sales", "support"])
    assert r.label == "support"
    assert 0.0 <= r.confidence <= 1.0


def test_classify_clips_invalid_confidence():
    cls = _load_classify()
    backend = MockChatBackend(
        responder=lambda s, m: '{"label":"support","confidence":17.5,"reasoning":"overconfident"}'
    )
    r = cls.classify(backend, "bug", ["sales", "support"])
    assert r.confidence == 1.0


def test_classify_falls_back_on_parse_failure():
    cls = _load_classify()
    backend = MockChatBackend(responder=lambda s, m: "not JSON at all")
    r = cls.classify(backend, "bug", ["sales", "support"])
    assert r.label == "sales"  # first label fallback
    assert r.confidence == 0.0


def test_classify_falls_back_on_unknown_label():
    cls = _load_classify()
    backend = MockChatBackend(
        responder=lambda s, m: '{"label":"NotARealLabel","confidence":0.5,"reasoning":""}'
    )
    r = cls.classify(backend, "x", ["sales", "support"])
    assert r.label == "sales"


def test_classify_eval_metrics():
    cls = _load_classify()

    def respond(_s, m):
        text = m[-1]["content"].lower()
        if "bug" in text:
            return '{"label":"support","confidence":0.92,"reasoning":""}'
        return '{"label":"sales","confidence":0.55,"reasoning":""}'

    metrics = cls.evaluate(
        MockChatBackend(responder=respond),
        [
            ("how much does it cost?", "sales"),
            ("there's a bug", "support"),
        ],
        ["sales", "support"],
    )
    assert metrics.n == 2
    assert metrics.accuracy == 1.0
    assert metrics.accuracy_on_high_conf == 1.0
