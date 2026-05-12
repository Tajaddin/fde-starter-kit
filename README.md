# fde-starter-kit

> Five deploy-ready Anthropic-stack templates for Forward Deployed / Solutions Engineer demos: **chat / rag / agent / extract / classify**. Each template is a self-contained `app.py` with a swappable `ChatBackend` (Mock + Anthropic). `fde-kit init <slug> <dest>` scaffolds any of them into a fresh project. **29 tests** — six scaffold tests + four backend tests + a smoke suite per template — all green in 1.3 s.

[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE) [![Tests](https://img.shields.io/badge/tests-29%20passing-brightgreen)](#tests) [![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()

## The five templates

| Slug | Title | What's in `app.py` |
|---|---|---|
| **chat** | Conversational Chat | `ChatSession` with system prompt + history mutation + `run_repl(backend, prompts)` for headless tests |
| **rag** | RAG over a JSON corpus | Pure-Python BM25 over a 5-doc JSON corpus, `ask(...)` returns answer + sources (no embeddings required) |
| **agent** | ReAct-style tool-use agent | Two built-in tools (safe calculator + stub search), bounded `max_steps`, parses `TOOL:`/`ARG:`/`ANSWER:` lines |
| **extract** | Structured data extraction | Pydantic schema → JSON → validation → **one repair retry** with the validation error attached to the prompt |
| **classify** | Multi-label classification | LLM-as-classifier with confidence clipping + label fallback + a `evaluate(...)` harness that reports accuracy on the high-confidence subset |

Each template is **<200 lines** of `app.py`. The intent is "demo-ready in 10 minutes", not "production-perfect."

## Quickstart

```bash
pip install -e ".[anthropic,dev]"

# Show the catalog
fde-kit list

# Scaffold one into a fresh dir
fde-kit init rag ./my-rag-demo
cd my-rag-demo
python app.py
```

To run any template against the real Anthropic API:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python app.py
```

Without the env var, every template falls back to `MockChatBackend` so you can run end-to-end in CI without credentials.

## The pluggable backend

Every example takes a `ChatBackend` implementing one method:

```python
class ChatBackend(Protocol):
    def chat(self, system: str | None, messages: list[dict]) -> Reply: ...
```

Two implementations ship:

* **`MockChatBackend(responder)`** — deterministic, records every call for test inspection.
* **`AnthropicChatBackend(model=..., api_key=...)`** — wraps `anthropic.Anthropic.messages.create`.

The test suite uses `MockChatBackend` for every smoke test, so the templates have full coverage without ever hitting the network.

## Tests

```bash
pytest -v
```

```
tests/test_scaffold.py            6 passed   list, copy, unknown-slug, refuse-nonempty, force-overwrite
tests/test_backends.py            4 passed   default responder, call inspection, custom responder, token estimates
tests/test_template_chat.py       3 passed   run_repl, history append, reset
tests/test_template_rag.py        3 passed   BM25 retrieval, ask() returns sources, no-match path
tests/test_template_agent.py      5 passed   calc safety, tool call, unknown tool, max_steps cap
tests/test_template_extract.py    3 passed   happy path, repair retry happens, raises after two failures
tests/test_template_classify.py   5 passed   parse, clip, parse-failure fallback, unknown-label fallback, eval metrics
─────────────────────────────────────────────
29 passed in 1.30s
```

Two tests worth pointing out:

* **`test_extract_repairs_on_validation_error`** — first mock response is `{"name":"Eve"}` (missing required `age`); the harness must call the backend a second time with the Pydantic validation error attached, then succeed. Asserted directly via `backend.calls == 2`.
* **`test_agent_stops_at_max_steps`** — backend always says "call calculate" (infinite loop). With `max_steps=3`, the agent terminates with 3 tool steps in the trace and a fallback `final_answer`. Bounds matter on agent loops.

## Why this exists

A Forward Deployed Engineer (or Solutions Engineer) regularly needs to ship a customer demo in 1-2 days. Most of those demos are the same five shapes, with the same plumbing: backend abstraction, system prompts, error paths, citations or tools, a CLI entry point. This kit captures the boilerplate so the customer-specific code is the only thing you write.

Every template is intentionally **minimal but correct**:

* No frameworks beyond Click + Pydantic + Anthropic SDK.
* No fake "modular" abstraction layers — one `app.py` per template.
* No hidden global state — backends and indices are passed in.
* Real tests, not toy tests — each template has a deterministic mock end-to-end path.

## Project layout

```
.
├── src/fde_kit/
│   ├── backends.py   # ChatBackend / MockChatBackend / AnthropicChatBackend
│   ├── scaffold.py   # TEMPLATES list + copy_template(slug, dest)
│   └── cli.py        # `fde-kit list` + `fde-kit init`
├── templates/
│   ├── chat/app.py + README.md
│   ├── rag/app.py + corpus.json + README.md
│   ├── agent/app.py + README.md
│   ├── extract/app.py + README.md
│   └── classify/app.py + README.md
└── tests/                  # 29 cases across 7 files
```

## Limitations

**Mock-first, not production-first.** Every template is designed to be a *starting point* a customer engineer iterates on, not a finished product. There's no auth, no logging, no observability, no rate limiting in the templates themselves (those are separate concerns and live in [llm-gateway-mini](https://github.com/Tajaddin/llm-gateway-mini)).

**`AnthropicChatBackend` requires the SDK.** Templates import it lazily, but `pip install '.[anthropic]'` is needed to run any template against real Claude. Without it, you get the mock.

**RAG is BM25, not vector search.** Deliberate: the demo runs anywhere, with no model downloads, on small corpora. For production RAG, swap the BM25 for an embedding index — the `BM25` class is dropped into one place in `ask()`.

**Agent is single-turn-tool-output.** No tool result chaining beyond text. For a real agent harness, see [tool-use-eval](https://github.com/Tajaddin/tool-use-eval) (eval-only) and [langgraph-research-pilot](https://github.com/Tajaddin/langgraph-research-pilot) (full graph).

## License

MIT — see [LICENSE](LICENSE).
