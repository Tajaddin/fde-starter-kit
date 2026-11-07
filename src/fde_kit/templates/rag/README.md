# rag — retrieval-augmented generation starter

BM25 over a JSON corpus (no embeddings, no GPUs), with citations returned alongside the answer.

Run it in the environment where fde-starter-kit is installed (the app imports `fde_kit.backends`):

```bash
python app.py                     # MockChatBackend, no key needed
export ANTHROPIC_API_KEY=sk-ant-...
python app.py                     # real Claude; needs fde-starter-kit[anthropic]
```

Swap `corpus.json` for your own corpus (`[{id, title, text}, ...]`). The `ask(backend, index, question)` helper returns both the model's reply and the list of source documents it was given.
