"""RAG over a JSON corpus with BM25 retrieval + cited answers.

Run:  python app.py
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from fde_kit.backends import ChatBackend, MockChatBackend, Reply


# Tiny built-in corpus so the demo runs without external data.
_CORPUS_PATH = Path(__file__).resolve().parent / "corpus.json"


@dataclass
class Doc:
    id: str
    title: str
    text: str


@dataclass
class RetrievalHit:
    doc: Doc
    score: float


_WORD = re.compile(r"[a-zA-Z]+")


def _tokens(s: str) -> list[str]:
    return [t.lower() for t in _WORD.findall(s)]


class BM25:
    """Minimal BM25 (no idf smoothing tricks, no compression)."""

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self.docs: list[Doc] = []
        self.tokens: list[list[str]] = []
        self.df: Counter[str] = Counter()
        self.avgdl: float = 0.0

    def add(self, doc: Doc) -> None:
        toks = _tokens(doc.title + " " + doc.text)
        self.docs.append(doc)
        self.tokens.append(toks)
        for t in set(toks):
            self.df[t] += 1
        total = sum(len(t) for t in self.tokens)
        self.avgdl = total / max(1, len(self.tokens))

    def score(self, query: str, doc_idx: int) -> float:
        q = _tokens(query)
        if not q:
            return 0.0
        N = len(self.docs)
        d = self.tokens[doc_idx]
        dl = len(d)
        tf = Counter(d)
        s = 0.0
        for term in q:
            df = self.df[term]
            if df == 0:
                continue
            idf = math.log(1 + (N - df + 0.5) / (df + 0.5))
            tf_t = tf[term]
            num = tf_t * (self.k1 + 1)
            den = tf_t + self.k1 * (1 - self.b + self.b * dl / max(1, self.avgdl))
            s += idf * num / max(1e-9, den)
        return s

    def search(self, query: str, k: int = 3) -> list[RetrievalHit]:
        scored = [
            RetrievalHit(self.docs[i], self.score(query, i)) for i in range(len(self.docs))
        ]
        scored.sort(key=lambda h: h.score, reverse=True)
        return [h for h in scored[:k] if h.score > 0]


def load_corpus(path: Path | None = None) -> BM25:
    p = path or _CORPUS_PATH
    raw = json.loads(p.read_text(encoding="utf-8"))
    bm = BM25()
    for item in raw:
        bm.add(Doc(id=item["id"], title=item["title"], text=item["text"]))
    return bm


_SYSTEM = (
    "Answer the user's question using ONLY the provided context. "
    "After each sentence that uses a source, cite it as [^N] where N is the "
    "source number. If the context doesn't answer the question, say so."
)


@dataclass
class GroundedAnswer:
    text: str
    sources: list[Doc]
    reply: Reply


def ask(backend: ChatBackend, index: BM25, question: str, k: int = 3) -> GroundedAnswer:
    hits = index.search(question, k=k)
    sources = [h.doc for h in hits]
    if not sources:
        return GroundedAnswer(text="I don't have enough context to answer.", sources=[], reply=Reply(text=""))
    blocks = "\n\n".join(
        f"[Source {i+1}: {d.title}]\n{d.text}" for i, d in enumerate(sources)
    )
    user = f"{question}\n\n---\nContext:\n{blocks}"
    reply = backend.chat(_SYSTEM, [{"role": "user", "content": user}])
    return GroundedAnswer(text=reply.text, sources=sources, reply=reply)


if __name__ == "__main__":
    import os

    backend = (
        __import__("fde_kit.backends", fromlist=["AnthropicChatBackend"]).AnthropicChatBackend()
        if os.environ.get("ANTHROPIC_API_KEY")
        else MockChatBackend(responder=lambda s, m: "Answer using [^1].")
    )
    idx = load_corpus()
    q = "What does the team consider remote-friendly?"
    ans = ask(backend, idx, q)
    print(ans.text)
    for i, s in enumerate(ans.sources):
        print(f"  [{i+1}] {s.title} ({s.id})")
