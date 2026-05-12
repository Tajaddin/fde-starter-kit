# chat — multi-turn chat starter

System-prompt + history management for a real chat session. Backend is pluggable: `MockChatBackend` for tests, `AnthropicChatBackend` for production.

```bash
pip install -e ".[anthropic,dev]"
export ANTHROPIC_API_KEY=sk-ant-...
python app.py
```

Use the `run_repl(backend, prompts)` helper from your own code to drive deterministic conversations under tests.
