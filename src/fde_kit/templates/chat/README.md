# chat — multi-turn chat starter

System-prompt + history management for a real chat session. Backend is pluggable: `MockChatBackend` for tests, `AnthropicChatBackend` for production.

Run it in the environment where fde-starter-kit is installed (the app imports `fde_kit.backends`):

```bash
python app.py                     # MockChatBackend, no key needed
export ANTHROPIC_API_KEY=sk-ant-...
python app.py                     # real Claude; needs fde-starter-kit[anthropic]
```

Use the `run_repl(backend, prompts)` helper from your own code to drive deterministic conversations under tests.
