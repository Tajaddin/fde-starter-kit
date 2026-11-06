# rag — retrieval-augmented generation starter

BM25 over a JSON corpus (no embeddings, no GPUs), with citations returned alongside the answer.

```bash
pip install -e ".[anthropic,dev]"
python app.py   # uses MockChatBackend if ANTHROPIC_API_KEY is unset
```

Swap `corpus.json` for your own corpus (`[{id, title, text}, ...]`). The `ask(backend, index, question)` helper returns both the model's reply and the list of source documents it was given.
