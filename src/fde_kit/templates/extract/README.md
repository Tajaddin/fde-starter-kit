# extract — structured data extraction starter

Pydantic-validated extraction from free text. Single repair retry: on a `JSONDecodeError` or `ValidationError`, the prompt is re-sent with the validation error attached so the model can self-correct.

Run it in the environment where fde-starter-kit is installed (the app imports `fde_kit.backends`):

```bash
python app.py                     # MockChatBackend, no key needed
export ANTHROPIC_API_KEY=sk-ant-...
python app.py                     # real Claude; needs fde-starter-kit[anthropic]
```

Define your own `BaseModel` and call `extract(backend, MyModel, text)` — the function returns a validated instance or raises after one retry.
