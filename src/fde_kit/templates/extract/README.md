# extract — structured data extraction starter

Pydantic-validated extraction from free text. Single repair retry: on a `JSONDecodeError` or `ValidationError`, the prompt is re-sent with the validation error attached so the model can self-correct.

```bash
pip install -e ".[anthropic,dev]"
python app.py
```

Define your own `BaseModel` and call `extract(backend, MyModel, text)` — the function returns a validated instance or raises after one retry.
