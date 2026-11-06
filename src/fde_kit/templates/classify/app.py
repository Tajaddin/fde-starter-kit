"""LLM-as-classifier with calibrated confidence + tiny eval harness.

Run:  python app.py
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from fde_kit.backends import ChatBackend, MockChatBackend


@dataclass
class ClassificationResult:
    label: str
    confidence: float
    reasoning: str


def _system(labels: list[str]) -> str:
    return (
        "You are a multi-label classifier. Pick the SINGLE best label from this set:\n"
        f"{', '.join(labels)}\n\n"
        "Respond with a JSON object: "
        '{"label": "<one of the labels>", "confidence": <0..1 float>, '
        '"reasoning": "<one sentence>"}'
    )


_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def classify(
    backend: ChatBackend,
    text: str,
    labels: list[str],
) -> ClassificationResult:
    reply = backend.chat(_system(labels), [{"role": "user", "content": text}])
    m = _JSON_RE.search(reply.text)
    if not m:
        return ClassificationResult(label=labels[0], confidence=0.0, reasoning="parse failure")
    data = json.loads(m.group(0))
    label = data.get("label", labels[0])
    if label not in labels:
        # Fall back to closest match by lowercase comparison.
        lo = label.lower()
        label = next((l for l in labels if l.lower() == lo), labels[0])
    conf = float(data.get("confidence", 0.0))
    conf = max(0.0, min(1.0, conf))
    return ClassificationResult(
        label=label,
        confidence=conf,
        reasoning=str(data.get("reasoning", "")),
    )


@dataclass
class EvalMetrics:
    n: int
    accuracy: float
    mean_confidence: float
    accuracy_on_high_conf: float | None  # accuracy on items with confidence >= 0.7


def evaluate(
    backend: ChatBackend,
    cases: list[tuple[str, str]],
    labels: list[str],
) -> EvalMetrics:
    correct = 0
    confs: list[float] = []
    high_correct = 0
    high_total = 0
    for text, expected in cases:
        r = classify(backend, text, labels)
        confs.append(r.confidence)
        if r.label == expected:
            correct += 1
        if r.confidence >= 0.7:
            high_total += 1
            if r.label == expected:
                high_correct += 1
    n = len(cases)
    return EvalMetrics(
        n=n,
        accuracy=correct / max(n, 1),
        mean_confidence=sum(confs) / max(len(confs), 1),
        accuracy_on_high_conf=(high_correct / high_total) if high_total else None,
    )


if __name__ == "__main__":
    import os

    if os.environ.get("ANTHROPIC_API_KEY"):
        from fde_kit.backends import AnthropicChatBackend
        backend = AnthropicChatBackend()
    else:
        # Deterministic mock that returns "support" for queries about a bug.
        def _respond(_s, m):
            t = m[-1]["content"].lower()
            if "bug" in t or "broken" in t:
                return '{"label":"support","confidence":0.92,"reasoning":"mentions a bug"}'
            return '{"label":"sales","confidence":0.55,"reasoning":"otherwise"}'

        backend = MockChatBackend(responder=_respond)

    cases = [
        ("How much does the Pro plan cost?", "sales"),
        ("There's a bug in checkout!", "support"),
    ]
    metrics = evaluate(backend, cases, ["sales", "support", "billing"])
    print(metrics)
